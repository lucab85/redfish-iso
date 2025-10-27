# Examples

This directory contains example scripts showing different ways to use the iDRAC ISO Tool.

## Scripts

### 1. deploy-multiple-servers.sh
**Bash script for deploying OS to multiple servers**

```bash
./deploy-multiple-servers.sh
```

Features:
- Loop through multiple iDRAC hosts
- Color-coded output
- Error handling per server
- Easy to customize server list

Edit the script to configure:
- `ISO_URL`: Your ISO location
- `SERVERS`: Array of iDRAC IPs
- `IDRAC_USER` and `IDRAC_PASS`: Credentials

### 2. python_wrapper.py
**Python wrapper for programmatic usage**

```bash
python3 python_wrapper.py
```

Features:
- Call the tool from Python code
- Batch processing multiple servers
- Capture and handle output
- Success/failure tracking

Use this as a template for integrating into your Python applications.

### 3. ansible-playbook.yml
**Ansible playbook for infrastructure automation**

```bash
ansible-playbook -i inventory.yml ansible-playbook.yml
```

Features:
- Idempotent server provisioning
- Inventory-based targeting
- Parallel execution
- Integration with Ansible workflows

Customize variables:
- `iso_url`: ISO location
- `idrac_timeout`: Operation timeout
- Credentials in inventory

### 4. inventory.yml
**Ansible inventory file**

Edit this file to define your iDRAC hosts and credentials.

## Common Patterns

### Environment Variables
```bash
export IDRAC_USER="root"
export IDRAC_PASS="calvin"
export ISO_URL="http://repo.local/installer.iso"

python3 ../idrac_iso_tool.py -H 10.0.0.25 -u "$IDRAC_USER" -p "$IDRAC_PASS" -i "$ISO_URL"
```

### With Vault/Secrets Manager
```bash
# AWS Secrets Manager
IDRAC_PASS=$(aws secretsmanager get-secret-value --secret-id idrac-password --query SecretString --output text)

# HashiCorp Vault
IDRAC_PASS=$(vault kv get -field=password secret/idrac)

python3 ../idrac_iso_tool.py -H 10.0.0.25 -u root -p "$IDRAC_PASS" -i "$ISO_URL"
```

### Error Handling in Scripts
```bash
if python3 idrac_iso_tool.py -H "$HOST" -u "$USER" -p "$PASS" -i "$ISO"; then
  echo "Success"
  # Continue with post-deployment tasks
else
  echo "Failed with exit code $?"
  # Send alert, log error, etc.
fi
```

### Parallel Execution
```bash
# Using GNU parallel
parallel -j 4 python3 ../idrac_iso_tool.py -H {} -u root -p calvin -i http://repo.local/os.iso ::: 10.0.0.{25..28}

# Using xargs
echo "10.0.0.25 10.0.0.26 10.0.0.27" | xargs -P 3 -n 1 -I {} python3 ../idrac_iso_tool.py -H {} -u root -p calvin -i http://repo.local/os.iso
```

## Integration Examples

### Jenkins Pipeline
```groovy
pipeline {
    agent any
    stages {
        stage('Provision Server') {
            steps {
                sh '''
                    python3 idrac_iso_tool.py \
                        -H ${IDRAC_HOST} \
                        -u ${IDRAC_USER} \
                        -p ${IDRAC_PASSWORD} \
                        -i ${ISO_URL} \
                        --insecure
                '''
            }
        }
    }
}
```

### GitLab CI
```yaml
provision:
  stage: deploy
  script:
    - python3 idrac_iso_tool.py -H $IDRAC_HOST -u $IDRAC_USER -p $IDRAC_PASSWORD -i $ISO_URL --insecure
  only:
    - main
```

### Terraform (External Data Source)
```hcl
data "external" "provision_server" {
  program = ["bash", "-c", <<EOF
python3 idrac_iso_tool.py \
  -H ${var.idrac_host} \
  -u ${var.idrac_user} \
  -p ${var.idrac_password} \
  -i ${var.iso_url} && echo '{"status":"success"}'
EOF
  ]
}
```

## Best Practices

1. **Never hardcode credentials** - Use environment variables or secret managers
2. **Test in development** - Verify ISO URL and credentials before production
3. **Log outputs** - Redirect stdout/stderr for auditing
4. **Handle errors** - Check exit codes and implement retries if needed
5. **Use --debug** - When troubleshooting issues
6. **Verify ISO accessibility** - Ensure iDRAC can reach the ISO URL

## Need Help?

- See main [README.md](../README.md) for tool documentation
- Check [CONTRIBUTING.md](../CONTRIBUTING.md) for development guidelines
- Open an issue on GitHub for bugs or questions
