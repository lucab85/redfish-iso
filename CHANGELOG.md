# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-27

### Added
- Initial release
- Single-file Python CLI tool for iDRAC ISO mounting
- HTTP/HTTPS ISO URL support
- One-time boot to CD configuration
- Automatic server reboot
- VirtualMedia endpoint auto-discovery
- Retry logic for transient errors
- Extended Redfish error message parsing
- Multiple reset type fallbacks (ForceRestart, GracefulRestart, PowerCycle)
- SSL verification with `--insecure` option
- Debug logging mode
- Password prompt for security
- `--eject-first` option to replace existing media
- `--no-wait` option for non-blocking execution
- Standard exit codes (0-4)
- Comprehensive error handling
- Support for iDRAC9 and iDRAC10

### Documentation
- Complete README with examples
- Contributing guidelines
- MIT License
- Example scripts (Bash, Python, Ansible)
- Dockerfile for containerized execution

## [Unreleased]

### Planned
- X-Auth-Token session authentication
- JSON output mode
- Cleanup/eject-only command
- Unit tests with mocked responses
- Configuration file support
