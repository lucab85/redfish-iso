#!/usr/bin/env python3
"""
Example: Using the iDRAC ISO tool as a Python module

This shows how to integrate the tool's functionality into your own scripts.
"""

import sys
import subprocess


def mount_iso_and_reboot(idrac_host: str, username: str, password: str, iso_url: str) -> bool:
    """
    Mount an ISO to an iDRAC and reboot the server.
    
    Args:
        idrac_host: iDRAC hostname or IP
        username: iDRAC username
        password: iDRAC password
        iso_url: HTTP/HTTPS URL to ISO
    
    Returns:
        True if successful, False otherwise
    """
    cmd = [
        "python3", "idrac_iso_tool.py",
        "-H", idrac_host,
        "-u", username,
        "-p", password,
        "-i", iso_url,
        "--insecure"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print(f"✓ Successfully mounted ISO to {idrac_host}")
            return True
        else:
            print(f"✗ Failed to mount ISO to {idrac_host}")
            print(f"  Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"✗ Timeout mounting ISO to {idrac_host}")
        return False
    except Exception as e:
        print(f"✗ Exception: {e}")
        return False


def main():
    # Example configuration
    servers = [
        {
            "host": "10.0.0.25",
            "user": "root",
            "password": "calvin",
            "iso": "http://repo.local/ubuntu-22.04.iso"
        },
        {
            "host": "10.0.0.26",
            "user": "root",
            "password": "calvin",
            "iso": "http://repo.local/centos-stream-9.iso"
        }
    ]
    
    success_count = 0
    
    for server in servers:
        print(f"\nProcessing {server['host']}...")
        if mount_iso_and_reboot(
            server["host"],
            server["user"],
            server["password"],
            server["iso"]
        ):
            success_count += 1
    
    print(f"\n{'='*50}")
    print(f"Completed: {success_count}/{len(servers)} servers successful")
    print(f"{'='*50}")
    
    return 0 if success_count == len(servers) else 1


if __name__ == "__main__":
    sys.exit(main())
