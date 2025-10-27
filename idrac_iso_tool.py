#!/usr/bin/env python3
"""
Dell iDRAC Redfish Virtual Media ISO Boot Tool

Single-file CLI tool to mount an ISO over HTTP(S), set one-time boot to CD, and reboot.
Requires: Python 3.8+, requests library

Usage:
  python idrac_iso_tool.py -H 10.0.0.25 -u root -p calvin -i http://repo.local/ubuntu.iso
  python idrac_iso_tool.py --host idrac.example.com --user admin --iso https://releases.ubuntu.com/24.04/ubuntu-24.04.iso --insecure
"""

import argparse
import getpass
import json
import logging
import sys
import time
from typing import Any, Dict, Optional
from urllib.parse import urlparse

try:
    import requests
    from requests.adapters import HTTPAdapter
    try:
        from urllib3.util.retry import Retry
    except ImportError:
        from requests.packages.urllib3.util.retry import Retry
except ImportError:
    print("ERROR: 'requests' library required. Install with: pip install requests", file=sys.stderr)
    sys.exit(3)


# Exit codes
EXIT_SUCCESS = 0
EXIT_AUTH_CONNECTION = 1
EXIT_API_ERROR = 2
EXIT_INVALID_ARGS = 3
EXIT_TIMEOUT = 4


class RedfishClient:
    """Minimal Redfish client for iDRAC operations"""
    
    def __init__(self, host: str, username: str, password: str, 
                 verify: bool = True, timeout: int = 30, debug: bool = False):
        self.base_url = f"https://{host}"
        self.username = username
        self.password = password
        self.timeout = timeout
        self.verify = verify
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        level = logging.DEBUG if debug else logging.INFO
        logging.basicConfig(
            format='%(levelname)-7s %(message)s',
            level=level
        )
        
        # Setup session with retries
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.verify = verify
        
        # Retry strategy for transient errors
        retry_strategy = Retry(
            total=2,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PATCH"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        
        if not verify:
            try:
                requests.packages.urllib3.disable_warnings()
            except AttributeError:
                import urllib3
                urllib3.disable_warnings()
    
    def _request(self, method: str, path: str, json_data: Optional[Dict] = None) -> requests.Response:
        """Execute HTTP request with error handling"""
        url = f"{self.base_url}{path}"
        self.logger.debug(f"{method} {url}")
        if json_data:
            self.logger.debug(f"Body: {json.dumps(json_data, indent=2)}")
        
        try:
            resp = self.session.request(
                method, url, json=json_data, timeout=self.timeout
            )
            self.logger.debug(f"Response: {resp.status_code}")
            
            # Try to parse extended error info
            if not resp.ok:
                try:
                    error_body = resp.json()
                    if 'error' in error_body:
                        error_info = error_body['error']
                        if '@Message.ExtendedInfo' in error_info:
                            for msg in error_info['@Message.ExtendedInfo']:
                                self.logger.error(f"  {msg.get('Message', msg)}")
                except:
                    pass
            
            return resp
            
        except requests.exceptions.Timeout:
            self.logger.error(f"Request timeout after {self.timeout}s")
            sys.exit(EXIT_TIMEOUT)
        except requests.exceptions.SSLError as e:
            self.logger.error(f"SSL verification failed: {e}")
            self.logger.error("Try --insecure to skip SSL verification")
            sys.exit(EXIT_AUTH_CONNECTION)
        except requests.exceptions.ConnectionError as e:
            self.logger.error(f"Connection failed: {e}")
            sys.exit(EXIT_AUTH_CONNECTION)
        except Exception as e:
            self.logger.error(f"Request failed: {e}")
            sys.exit(EXIT_API_ERROR)
    
    def get(self, path: str) -> Dict[str, Any]:
        """GET request returning JSON"""
        resp = self._request("GET", path)
        if resp.status_code == 401:
            self.logger.error("Authentication failed (401). Check credentials.")
            sys.exit(EXIT_AUTH_CONNECTION)
        if resp.status_code == 403:
            self.logger.error("Insufficient privileges (403).")
            sys.exit(EXIT_AUTH_CONNECTION)
        if not resp.ok:
            self.logger.error(f"GET {path} failed with status {resp.status_code}")
            sys.exit(EXIT_API_ERROR)
        return resp.json()
    
    def post(self, path: str, data: Dict[str, Any]) -> requests.Response:
        """POST request"""
        resp = self._request("POST", path, data)
        if resp.status_code in [401, 403]:
            self.logger.error(f"Authentication/Authorization failed ({resp.status_code})")
            sys.exit(EXIT_AUTH_CONNECTION)
        return resp
    
    def patch(self, path: str, data: Dict[str, Any]) -> requests.Response:
        """PATCH request"""
        resp = self._request("PATCH", path, data)
        if resp.status_code in [401, 403]:
            self.logger.error(f"Authentication/Authorization failed ({resp.status_code})")
            sys.exit(EXIT_AUTH_CONNECTION)
        return resp


def discover_virtualmedia_cd(client: RedfishClient, manager_id: str = "iDRAC.Embedded.1") -> str:
    """Find the VirtualMedia CD endpoint"""
    vm_path = f"/redfish/v1/Managers/{manager_id}/VirtualMedia"
    client.logger.info(f"Discovering VirtualMedia endpoints...")
    
    try:
        vm_collection = client.get(vm_path)
    except SystemExit:
        client.logger.error(f"Failed to access {vm_path}")
        client.logger.error("Verify iDRAC firmware supports Redfish VirtualMedia")
        raise
    
    members = vm_collection.get("Members", [])
    if not members:
        client.logger.error("No VirtualMedia devices found")
        sys.exit(EXIT_API_ERROR)
    
    # Look for CD device
    for member in members:
        member_uri = member.get("@odata.id", "")
        if "CD" in member_uri.upper():
            # Verify it supports CD media types
            try:
                vm_detail = client.get(member_uri)
                media_types = vm_detail.get("MediaTypes", [])
                if "CD" in media_types or "DVD" in media_types:
                    client.logger.info(f"VirtualMedia CD: {member_uri}")
                    return member_uri
            except:
                continue
    
    # Fallback: return first member
    fallback_uri = members[0].get("@odata.id", "")
    client.logger.warning(f"No explicit CD device found, using: {fallback_uri}")
    return fallback_uri


def eject_media(client: RedfishClient, cd_uri: str):
    """Eject any existing virtual media"""
    client.logger.info("Ejecting existing media...")
    eject_uri = f"{cd_uri}/Actions/VirtualMedia.EjectMedia"
    resp = client.post(eject_uri, {})
    
    if resp.status_code in [200, 202, 204]:
        client.logger.info("Media ejected successfully")
        time.sleep(2)  # Brief pause
    elif resp.status_code == 400:
        client.logger.warning("Eject returned 400 (may be already ejected)")
    else:
        client.logger.error(f"Eject failed with status {resp.status_code}")
        sys.exit(EXIT_API_ERROR)


def insert_media(client: RedfishClient, cd_uri: str, iso_url: str, wait: bool = True):
    """Insert ISO from HTTP(S) URL"""
    # Validate URL
    parsed = urlparse(iso_url)
    if parsed.scheme not in ["http", "https"]:
        client.logger.error(f"Invalid ISO URL scheme: {parsed.scheme} (must be http/https)")
        sys.exit(EXIT_INVALID_ARGS)
    
    if parsed.scheme == "http":
        client.logger.warning("Using unencrypted HTTP for ISO URL")
    
    client.logger.info(f"Inserting ISO: {iso_url}")
    insert_uri = f"{cd_uri}/Actions/VirtualMedia.InsertMedia"
    
    payload = {
        "Image": iso_url,
        "Inserted": True,
        "WriteProtected": True
    }
    
    resp = client.post(insert_uri, payload)
    
    if resp.status_code in [200, 202, 204]:
        client.logger.info("InsertMedia request accepted")
    elif resp.status_code == 400:
        client.logger.error("InsertMedia failed (400). Media may already be inserted.")
        client.logger.error("Try --eject-first flag")
        sys.exit(EXIT_API_ERROR)
    elif resp.status_code == 409:
        client.logger.error("Conflict (409). Media may already be inserted.")
        client.logger.error("Try --eject-first flag")
        sys.exit(EXIT_API_ERROR)
    else:
        client.logger.error(f"InsertMedia failed with status {resp.status_code}")
        sys.exit(EXIT_API_ERROR)
    
    # Wait for insertion to complete
    if wait:
        client.logger.info("Waiting for media insertion to complete...")
        max_attempts = 10
        for attempt in range(max_attempts):
            time.sleep(2)
            state = client.get(cd_uri)
            if state.get("Inserted") is True:
                client.logger.info(f"Media inserted: {state.get('Image', 'unknown')}")
                return
        client.logger.warning("Timed out waiting for insertion confirmation (proceeding anyway)")


def set_onetime_boot(client: RedfishClient, system_id: str = "System.Embedded.1"):
    """Set one-time boot override to CD"""
    system_path = f"/redfish/v1/Systems/{system_id}"
    client.logger.info("Setting one-time boot to virtual CD...")
    
    payload = {
        "Boot": {
            "BootSourceOverrideEnabled": "Once",
            "BootSourceOverrideTarget": "Cd"
        }
    }
    
    resp = client.patch(system_path, payload)
    
    if resp.status_code in [200, 202, 204]:
        client.logger.info("One-time boot override set to CD")
    else:
        client.logger.error(f"Failed to set boot override (status {resp.status_code})")
        sys.exit(EXIT_API_ERROR)


def reboot_system(client: RedfishClient, system_id: str = "System.Embedded.1"):
    """Reboot the server"""
    reset_path = f"/redfish/v1/Systems/{system_id}/Actions/ComputerSystem.Reset"
    
    # Try reset types in order of preference
    reset_types = ["ForceRestart", "GracefulRestart", "PowerCycle"]
    
    for reset_type in reset_types:
        client.logger.info(f"Requesting {reset_type}...")
        payload = {"ResetType": reset_type}
        resp = client.post(reset_path, payload)
        
        if resp.status_code in [200, 202, 204]:
            client.logger.info(f"Reboot initiated ({reset_type})")
            return
        elif resp.status_code == 400:
            client.logger.debug(f"{reset_type} not supported, trying next...")
            continue
    
    client.logger.error("All reset types failed")
    sys.exit(EXIT_API_ERROR)


def main():
    parser = argparse.ArgumentParser(
        description="Mount ISO via Dell iDRAC Redfish and boot from it",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -H 10.0.0.25 -u root -p calvin -i http://repo.local/ubuntu.iso
  %(prog)s --host idrac.example.com --user admin --iso https://releases.ubuntu.com/24.04/ubuntu-24.04.iso --insecure
        """
    )
    
    # Required arguments
    parser.add_argument("-H", "--host", required=True,
                        help="iDRAC hostname or IP address")
    parser.add_argument("-u", "--user", required=True,
                        help="iDRAC username")
    parser.add_argument("-p", "--password",
                        help="iDRAC password (will prompt if omitted)")
    parser.add_argument("-i", "--iso", required=True,
                        help="HTTP(S) URL to ISO image")
    
    # Optional arguments
    parser.add_argument("--insecure", action="store_true",
                        help="Disable SSL certificate verification")
    parser.add_argument("--timeout", type=int, default=30,
                        help="Request timeout in seconds (default: 30)")
    parser.add_argument("--debug", action="store_true",
                        help="Enable debug logging")
    parser.add_argument("--eject-first", action="store_true",
                        help="Force eject any existing media before insert")
    parser.add_argument("--no-wait", action="store_true",
                        help="Don't wait for status confirmation after actions")
    
    # Advanced options
    parser.add_argument("--manager-id", default="iDRAC.Embedded.1",
                        help="Manager ID (default: iDRAC.Embedded.1)")
    parser.add_argument("--system-id", default="System.Embedded.1",
                        help="System ID (default: System.Embedded.1)")
    
    args = parser.parse_args()
    
    # Prompt for password if not provided
    password = args.password
    if not password:
        try:
            password = getpass.getpass(f"Password for {args.user}@{args.host}: ")
        except KeyboardInterrupt:
            print("\nAborted.", file=sys.stderr)
            sys.exit(EXIT_INVALID_ARGS)
    
    if not password:
        print("ERROR: Password required", file=sys.stderr)
        sys.exit(EXIT_INVALID_ARGS)
    
    # Initialize client
    client = RedfishClient(
        host=args.host,
        username=args.user,
        password=password,
        verify=not args.insecure,
        timeout=args.timeout,
        debug=args.debug
    )
    
    client.logger.info(f"Connecting to https://{args.host}")
    
    try:
        # Test connection
        client.get("/redfish/v1")
        
        # Discover VirtualMedia CD endpoint
        cd_uri = discover_virtualmedia_cd(client, args.manager_id)
        
        # Check current state and optionally eject
        current_state = client.get(cd_uri)
        if current_state.get("Inserted") and args.eject_first:
            eject_media(client, cd_uri)
        elif current_state.get("Inserted"):
            current_image = current_state.get("Image", "unknown")
            client.logger.info(f"Media already inserted: {current_image}")
            if current_image != args.iso:
                client.logger.warning("Different ISO already inserted. Use --eject-first to replace.")
        
        # Insert ISO
        insert_media(client, cd_uri, args.iso, wait=not args.no_wait)
        
        # Set one-time boot
        set_onetime_boot(client, args.system_id)
        
        # Reboot
        reboot_system(client, args.system_id)
        
        client.logger.info("✓ Done. Host will boot from virtual CD on next POST.")
        sys.exit(EXIT_SUCCESS)
        
    except KeyboardInterrupt:
        client.logger.error("\nInterrupted by user")
        sys.exit(EXIT_INVALID_ARGS)
    except Exception as e:
        client.logger.error(f"Unexpected error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(EXIT_API_ERROR)


if __name__ == "__main__":
    main()
