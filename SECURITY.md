# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please follow these steps:

1. **Do NOT** open a public issue
2. Email the maintainers directly at: [your-email@example.com]
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will respond within 48 hours and work with you to address the issue.

## Security Best Practices

When using this tool:

### Credentials
- Never commit credentials to version control
- Use environment variables or secure vaults
- Enable password prompts when possible
- Rotate credentials regularly

### Network Security
- Use HTTPS for ISO URLs when possible
- Enable SSL verification in production (avoid `--insecure`)
- Restrict network access to iDRAC management network
- Use VPN or bastion hosts for remote access

### Access Control
- Use principle of least privilege for iDRAC accounts
- Create dedicated service accounts for automation
- Enable iDRAC audit logging
- Review access logs regularly

### Examples

**Good:**
```bash
# Use environment variables
export IDRAC_USER="automation-svc"
export IDRAC_PASS="$(vault read -field=password secret/idrac)"
python idrac_iso_tool.py -H idrac.local -u "$IDRAC_USER" -p "$IDRAC_PASS" -i https://...
```

**Bad:**
```bash
# Don't hardcode credentials in scripts
python idrac_iso_tool.py -H idrac.local -u root -p supersecret123 -i http://...
```

## Known Security Considerations

1. **Basic Authentication**: The tool uses HTTP Basic Auth. Always use HTTPS.
2. **Password in Process List**: Command-line passwords may be visible in process lists. Use password prompt or environment variables.
3. **No Credential Validation**: The tool does not validate credential strength.
4. **Reboot Action**: The tool performs a system reboot without additional confirmation.

## Updates

Security updates will be released as patch versions (e.g., 1.0.1) and documented in CHANGELOG.md.
