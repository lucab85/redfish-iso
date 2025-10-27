# Contributing to iDRAC ISO Tool

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful, constructive, and professional in all interactions.

## How to Contribute

### Reporting Bugs

Before creating a bug report, please check existing issues. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected vs actual behavior**
- **Environment details** (Python version, OS, iDRAC version)
- **Debug output** if available (`--debug` flag)

Example:
```
Title: InsertMedia fails with 400 on iDRAC9 v6.10.00.00

Description:
When trying to insert an ISO on iDRAC9 firmware 6.10.00.00, the tool fails 
with a 400 error even though no media is currently inserted.

Steps to reproduce:
1. Run: python idrac_iso_tool.py -H 10.0.0.25 -u root -p xxx -i http://... --debug
2. See error: "InsertMedia failed (400)"

Environment:
- Python 3.11.5
- macOS 14.1
- iDRAC9 v6.10.00.00
- PowerEdge R640
```

### Suggesting Enhancements

Enhancement suggestions are welcome! Please:

1. Check if the enhancement has already been suggested
2. Provide a clear use case
3. Explain why this would be useful
4. Consider backward compatibility

### Pull Requests

#### Setup Development Environment

```bash
git clone https://github.com/yourusername/redfish-iso.git
cd redfish-iso
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Before Submitting

1. **Test your changes** with real iDRAC hardware if possible
2. **Follow the existing code style** (see below)
3. **Update documentation** if needed
4. **Add your changes** to the "Unreleased" section of CHANGELOG.md (if it exists)

#### Code Style Guidelines

- Follow [PEP 8](https://pep8.org/) style guide
- Use type hints for function parameters and return values
- Keep functions focused and under 50 lines when possible
- Use meaningful variable names
- Add docstrings to functions and classes
- Comment complex logic

Example:
```python
def discover_virtualmedia_cd(client: RedfishClient, manager_id: str = "iDRAC.Embedded.1") -> str:
    """
    Find the VirtualMedia CD endpoint.
    
    Args:
        client: RedfishClient instance for API calls
        manager_id: Manager identifier (default: iDRAC.Embedded.1)
    
    Returns:
        URI path to the CD VirtualMedia device
    
    Raises:
        SystemExit: If no VirtualMedia devices found
    """
```

#### Commit Message Format

Use clear, descriptive commit messages:

```
[type]: Brief description (50 chars or less)

More detailed explanation if needed. Wrap at 72 characters.
Explain the problem that this commit is solving and why this
approach was chosen.

Fixes #123
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic changes)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat: Add --session flag for X-Auth-Token authentication

Allows users to provide existing X-Auth-Token instead of
username/password for better security in automation scenarios.

Fixes #45
```

```
fix: Handle empty MediaTypes array in VirtualMedia discovery

Some iDRAC versions return empty MediaTypes. Added fallback
logic to use first available VirtualMedia device.

Fixes #67
```

#### Pull Request Process

1. **Fork** the repository
2. **Create a branch** from `main`:
   ```bash
   git checkout -b feat/my-new-feature
   ```
3. **Make your changes** and commit
4. **Push** to your fork:
   ```bash
   git push origin feat/my-new-feature
   ```
5. **Open a Pull Request** with:
   - Clear title describing the change
   - Reference to related issues
   - Description of what changed and why
   - Any testing performed

### Testing Guidelines

Since this tool interacts with hardware, testing can be challenging:

#### Manual Testing Checklist

- [ ] Help output works (`--help`)
- [ ] Authentication success and failure
- [ ] ISO insertion with valid URL
- [ ] ISO insertion with invalid URL (proper error)
- [ ] Eject existing media
- [ ] One-time boot configuration
- [ ] Reboot sequence
- [ ] Debug logging output
- [ ] Insecure mode (SSL verification disabled)
- [ ] Password prompt when not provided
- [ ] Exit codes are correct

#### Test on Multiple Platforms

If possible, test on:
- Different Python versions (3.8, 3.9, 3.10, 3.11, 3.12)
- Different OS (Linux, macOS, Windows)
- Different iDRAC versions (iDRAC9, iDRAC10)

#### Mock Testing

For automated testing without hardware:
```python
import unittest
from unittest.mock import Mock, patch

# Example test structure
class TestRedfishClient(unittest.TestCase):
    @patch('requests.Session')
    def test_successful_authentication(self, mock_session):
        # Test implementation
        pass
```

## Feature Requests

Priority areas for contributions:

### High Priority
- [ ] Unit tests with mocked Redfish responses
- [ ] Support for X-Auth-Token session authentication
- [ ] JSON output mode for automation
- [ ] Cleanup/eject command after installation

### Medium Priority
- [ ] Progress bar for long operations
- [ ] Configuration file support
- [ ] Multiple server orchestration
- [ ] Dockerfile for containerized execution

### Low Priority
- [ ] Web UI wrapper
- [ ] Ansible module/role
- [ ] PowerShell version

## Documentation

Documentation improvements are always welcome:

- README clarifications
- Additional examples
- FAQ section
- Troubleshooting guides
- Video tutorials

## Questions?

- Open a [Discussion](https://github.com/yourusername/redfish-iso/discussions)
- Check existing [Issues](https://github.com/yourusername/redfish-iso/issues)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
