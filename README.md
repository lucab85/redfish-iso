# iDRAC ISO Tool

A lightweight, single-file Python CLI tool for mounting ISO images over HTTP/HTTPS to Dell iDRAC via Redfish API, setting one-time boot to virtual CD, and rebooting the server.

Perfect for automating remote OS installations, rescue boots, and bare-metal provisioning on Dell PowerEdge servers.

## Features

- 🚀 **Single-file script** - Easy to deploy and use
- 🔒 **Secure by default** - TLS verification enabled (with option to disable)
- 🔄 **Automatic retries** - Handles transient network errors gracefully
- 📝 **Clear logging** - Info and debug modes for troubleshooting
- 🎯 **Smart discovery** - Automatically finds the correct VirtualMedia endpoint
- ⚡ **Fast execution** - Completes in seconds with proper error handling
- 🛡️ **Exit codes** - Scriptable with standard exit codes
- 💡 **Smart power management** - Automatically powers on if server is off, reboots if on

## Requirements

- Python 3.8 or higher
- `requests` library
- Dell iDRAC9 or iDRAC10 with Redfish support
- Network access to both iDRAC and ISO URL

## Installation

### Option 1: Direct Download

```bash
curl -O https://raw.githubusercontent.com/yourusername/redfish-iso/main/idrac_iso_tool.py
chmod +x idrac_iso_tool.py
```

### Option 2: Clone Repository

```bash
git clone https://github.com/yourusername/redfish-iso.git
cd redfish-iso
chmod +x idrac_iso_tool.py
```

### Install Dependencies

```bash
pip install requests
```

Or with a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install requests
```

## Quick Start

### Basic Usage

```bash
python idrac_iso_tool.py \
  -H 10.0.0.25 \
  -u root \
  -p calvin \
  -i http://repo.example.com/ubuntu-24.04.iso
```

### Secure Usage (HTTPS ISO with SSL verification)

```bash
python idrac_iso_tool.py \
  --host idrac.example.com \
  --user admin \
  --iso https://releases.ubuntu.com/24.04/ubuntu-24.04-live-server-amd64.iso
```

### Interactive Password Prompt

```bash
python idrac_iso_tool.py -H 10.0.0.25 -u root -i http://repo.local/installer.iso
# Password prompt appears (hidden input)
```

### Replace Existing Media

```bash
python idrac_iso_tool.py \
  -H 10.0.0.25 \
  -u root \
  -p calvin \
  -i http://repo.local/new-installer.iso \
  --eject-first
```

### Skip SSL Verification (Lab/Testing Only)

```bash
python idrac_iso_tool.py \
  -H 10.0.0.25 \
  -u root \
  -p calvin \
  -i http://repo.local/installer.iso \
  --insecure
```

## Command-Line Options

### Required Arguments

| Option | Description |
|--------|-------------|
| `-H`, `--host` | iDRAC hostname or IP address |
| `-u`, `--user` | iDRAC username |
| `-i`, `--iso` | HTTP(S) URL to ISO image |

### Optional Arguments

| Option | Description | Default |
|--------|-------------|---------|
| `-p`, `--password` | iDRAC password (prompts if omitted) | - |
| `--insecure` | Disable SSL certificate verification | False |
| `--timeout` | Request timeout in seconds | 30 |
| `--debug` | Enable debug logging | False |
| `--eject-first` | Force eject existing media before insert | False |
| `--no-wait` | Don't wait for status confirmation | False |
| `--manager-id` | Manager ID | iDRAC.Embedded.1 |
| `--system-id` | System ID | System.Embedded.1 |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Authentication or connection error |
| 2 | API error (invalid response, conflict, etc.) |
| 3 | Invalid arguments |
| 4 | Timeout |

## Usage Examples

### Automated Bare-Metal Installation

```bash
#!/bin/bash
# deploy-server.sh

IDRAC_HOST="10.0.0.25"
IDRAC_USER="root"
IDRAC_PASS="calvin"
ISO_URL="http://repo.local/ubuntu-autoinstall.iso"

python idrac_iso_tool.py \
  -H "$IDRAC_HOST" \
  -u "$IDRAC_USER" \
  -p "$IDRAC_PASS" \
  -i "$ISO_URL" \
  --eject-first

if [ $? -eq 0 ]; then
  echo "Server is rebooting and will install Ubuntu"
else
  echo "Failed to mount ISO"
  exit 1
fi
```

### CI/CD Integration

```yaml
# .github/workflows/provision.yml
- name: Mount installation ISO
  run: |
    python idrac_iso_tool.py \
      -H ${{ secrets.IDRAC_HOST }} \
      -u ${{ secrets.IDRAC_USER }} \
      -p ${{ secrets.IDRAC_PASSWORD }} \
      -i https://repo.example.com/os-install.iso \
      --insecure
```

### Rescue Boot

```bash
# Boot into rescue mode
python idrac_iso_tool.py \
  -H server1-idrac.local \
  -u admin \
  -i https://boot.netboot.xyz/ipxe/netboot.xyz.iso \
  --debug
```

## How It Works

1. **Authenticate** - Connects to iDRAC using Basic Authentication
2. **Discover** - Finds the VirtualMedia CD endpoint via Redfish API
3. **Check State** - Verifies current media status (ejects if `--eject-first`)
4. **Insert ISO** - Mounts the ISO from the provided HTTP(S) URL
5. **Set Boot** - Configures one-time boot override to CD
6. **Check Power State** - Determines if server is powered on or off
7. **Power On/Reboot** - Powers on (if off) or reboots (if on) the server
8. **Verify** - Waits for confirmation (unless `--no-wait`)

> **Smart Power Management**: The tool automatically detects the server's power state. If the server is powered off, it executes a startup from CD. If the server is already running, it performs a reboot.

## Redfish API Endpoints Used

```
GET  /redfish/v1
GET  /redfish/v1/Systems/System.Embedded.1
GET  /redfish/v1/Managers/iDRAC.Embedded.1/VirtualMedia
GET  /redfish/v1/Managers/iDRAC.Embedded.1/VirtualMedia/CD
POST /redfish/v1/Managers/iDRAC.Embedded.1/VirtualMedia/CD/Actions/VirtualMedia.InsertMedia
POST /redfish/v1/Managers/iDRAC.Embedded.1/VirtualMedia/CD/Actions/VirtualMedia.EjectMedia
PATCH /redfish/v1/Systems/System.Embedded.1
POST /redfish/v1/Systems/System.Embedded.1/Actions/ComputerSystem.Reset
```

## Troubleshooting

### Authentication Failed (401)

```bash
# Verify credentials
curl -k -u root:calvin https://10.0.0.25/redfish/v1

# Try with correct credentials
python idrac_iso_tool.py -H 10.0.0.25 -u root -p correct_password -i http://...
```

### SSL Certificate Verification Failed

```bash
# For production: Add CA certificate to system trust store
# For testing only: Use --insecure flag
python idrac_iso_tool.py -H 10.0.0.25 -u root -p calvin -i http://... --insecure
```

### Media Already Inserted (409/400)

```bash
# Force eject before inserting new media
python idrac_iso_tool.py -H 10.0.0.25 -u root -p calvin -i http://... --eject-first
```

### Connection Timeout

```bash
# Increase timeout for slow networks
python idrac_iso_tool.py -H 10.0.0.25 -u root -p calvin -i http://... --timeout 60
```

### Debug Output

```bash
# Enable debug logging to see all API calls
python idrac_iso_tool.py -H 10.0.0.25 -u root -p calvin -i http://... --debug
```

## Supported Platforms

### Tested On

- Dell PowerEdge R640, R650, R750 (iDRAC9)
- Dell PowerEdge R660, R760 (iDRAC10)
- Python 3.8, 3.9, 3.10, 3.11, 3.12

### Compatible With

- Any Dell server with iDRAC9 or iDRAC10
- Redfish 1.x compatible iDRAC firmware

## Security Considerations

- **Never commit passwords** to version control
- Use environment variables or secure vaults for credentials
- Enable TLS verification in production (`--insecure` should only be used for testing)
- ISO URLs over HTTP are warned about (use HTTPS when possible)
- The tool does not store or cache credentials

### Example: Using Environment Variables

```bash
export IDRAC_HOST="10.0.0.25"
export IDRAC_USER="root"
export IDRAC_PASS="calvin"

python idrac_iso_tool.py \
  -H "$IDRAC_HOST" \
  -u "$IDRAC_USER" \
  -p "$IDRAC_PASS" \
  -i http://repo.local/installer.iso
```

## Limitations

- **HTTP/HTTPS only** - NFS and CIFS shares are not supported
- **Single host** - No multi-node orchestration (use shell loops or Ansible)
- **No ISO upload** - ISO must be hosted on accessible HTTP(S) server
- **One-time boot only** - Persistent boot configuration not supported

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

```bash
git clone https://github.com/yourusername/redfish-iso.git
cd redfish-iso
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Running Tests

```bash
# Syntax check
python3 -m py_compile idrac_iso_tool.py

# Type hints check (if mypy installed)
mypy idrac_iso_tool.py

# Test help output
python idrac_iso_tool.py --help
```

## License

MIT License - See [LICENSE](LICENSE) file for details

## Author

Created for automating Dell PowerEdge bare-metal provisioning

## Related Projects

- [Dell iDRAC Redfish API Documentation](https://developer.dell.com/apis/2978/versions/6.xx/docs/GettingStarted/Introduction.md)
- [DMTF Redfish Specification](https://www.dmtf.org/standards/redfish)

## Support

- 🐛 [Report Issues](https://github.com/yourusername/redfish-iso/issues)
- 💬 [Discussions](https://github.com/yourusername/redfish-iso/discussions)
- 📖 [Wiki](https://github.com/yourusername/redfish-iso/wiki)

---

**⚠️ Important**: This tool reboots the target server. Always verify the correct iDRAC host before running!
