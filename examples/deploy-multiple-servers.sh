#!/bin/bash
# Example automation script for deploying an OS to multiple servers

# Configuration
ISO_URL="http://repo.local/ubuntu-22.04-autoinstall.iso"
IDRAC_USER="root"
IDRAC_PASS="calvin"

# Server list
SERVERS=(
  "10.0.0.25"
  "10.0.0.26"
  "10.0.0.27"
)

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================"
echo "Bare-Metal OS Deployment Script"
echo "========================================"
echo ""
echo "ISO: ${ISO_URL}"
echo "Target servers: ${#SERVERS[@]}"
echo ""

# Process each server
for host in "${SERVERS[@]}"; do
  echo -e "${YELLOW}Processing: ${host}${NC}"
  
  # Run the tool
  python3 idrac_iso_tool.py \
    -H "${host}" \
    -u "${IDRAC_USER}" \
    -p "${IDRAC_PASS}" \
    -i "${ISO_URL}" \
    --eject-first \
    --insecure
  
  # Check exit code
  if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Success: ${host}${NC}"
  else
    echo -e "${RED}✗ Failed: ${host}${NC}"
  fi
  
  echo ""
done

echo "========================================"
echo "Deployment initiated on all servers"
echo "========================================"
