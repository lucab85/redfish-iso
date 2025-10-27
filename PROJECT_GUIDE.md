# Project Structure

```
redfish-iso/
├── idrac_iso_tool.py          # Main tool (single-file implementation)
├── README.md                   # Project documentation
├── LICENSE                     # MIT License
├── CHANGELOG.md                # Version history
├── CONTRIBUTING.md             # Contribution guidelines
├── SECURITY.md                 # Security policy
├── requirements.txt            # Python dependencies
├── setup.sh                    # Quick setup script
├── Dockerfile                  # Container build instructions
├── .gitignore                  # Git ignore patterns
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions CI/CD
└── examples/
    ├── deploy-multiple-servers.sh    # Bash multi-server example
    ├── python_wrapper.py             # Python integration example
    ├── ansible-playbook.yml          # Ansible playbook example
    └── inventory.yml                 # Ansible inventory example
```

## Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/yourusername/redfish-iso.git
cd redfish-iso
./setup.sh
```

### 2. Basic Usage
```bash
python3 idrac_iso_tool.py \
  -H 10.0.0.25 \
  -u root \
  -p calvin \
  -i http://repo.local/ubuntu-24.04.iso
```

### 3. Run Examples
```bash
# Bash automation
./examples/deploy-multiple-servers.sh

# Python wrapper
python3 examples/python_wrapper.py

# Ansible
ansible-playbook -i examples/inventory.yml examples/ansible-playbook.yml

# Docker
docker build -t idrac-iso-tool .
docker run --rm idrac-iso-tool -H 10.0.0.25 -u root -p calvin -i http://...
```

## Publishing to GitHub

### Initial Setup
```bash
cd redfish-iso

# Initialize git (if not already)
git init

# Add all files
git add .

# Initial commit
git commit -m "Initial commit: iDRAC ISO Tool v1.0.0"

# Add remote (replace with your GitHub repo URL)
git remote add origin https://github.com/yourusername/redfish-iso.git

# Push to GitHub
git push -u origin main
```

### Create Release
1. Go to your GitHub repository
2. Click "Releases" → "Create a new release"
3. Tag version: `v1.0.0`
4. Release title: `v1.0.0 - Initial Release`
5. Description: Copy from CHANGELOG.md
6. Attach `idrac_iso_tool.py` as a release asset
7. Publish release

### Configure Repository

#### Settings
- **Description**: "Single-file Python CLI for mounting ISOs to Dell iDRAC via Redfish"
- **Website**: Link to documentation if separate
- **Topics**: `dell`, `idrac`, `redfish`, `automation`, `bare-metal`, `python`, `devops`

#### Branch Protection (for main)
- Require pull request reviews
- Require status checks to pass
- Enable GitHub Actions

#### Enable Features
- ✅ Issues
- ✅ Discussions
- ✅ Wiki (optional)
- ✅ Projects (optional)

## GitHub Repository Description

**Short version:**
```
🔧 Single-file Python CLI tool for mounting ISOs to Dell iDRAC via Redfish API. 
Automate bare-metal OS installations on PowerEdge servers.
```

**Full version:**
```
Lightweight Python tool for remote ISO mounting on Dell PowerEdge servers via iDRAC 
Redfish API. Features automatic VirtualMedia discovery, one-time boot configuration, 
server reboot, and comprehensive error handling. Perfect for bare-metal provisioning 
automation, CI/CD pipelines, and infrastructure-as-code deployments.
```

## Maintenance

### Version Updates
1. Update CHANGELOG.md
2. Bump version in documentation
3. Create git tag: `git tag v1.x.x`
4. Push tag: `git push origin v1.x.x`
5. Create GitHub release

### Testing Checklist
- [ ] Python 3.8+ compatibility
- [ ] Syntax validation
- [ ] Help output works
- [ ] Example scripts run
- [ ] Docker build succeeds
- [ ] Documentation is current

## Support Channels

- **Bug Reports**: GitHub Issues
- **Feature Requests**: GitHub Issues with `enhancement` label
- **Questions**: GitHub Discussions
- **Security**: See SECURITY.md

## License

MIT License - See LICENSE file
