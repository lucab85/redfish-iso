#!/bin/bash
# Quick setup and verification script

set -e

echo "=========================================="
echo "iDRAC ISO Tool - Setup & Verification"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version
echo ""

# Check if pip is available
echo "Checking pip..."
python3 -m pip --version
echo ""

# Install dependencies
echo "Installing dependencies..."
python3 -m pip install -r requirements.txt
echo ""

# Make script executable
echo "Making script executable..."
chmod +x idrac_iso_tool.py
echo ""

# Verify syntax
echo "Verifying Python syntax..."
python3 -m py_compile idrac_iso_tool.py
echo "✓ Syntax OK"
echo ""

# Test help output
echo "Testing help output..."
python3 idrac_iso_tool.py --help
echo ""

echo "=========================================="
echo "✓ Setup complete!"
echo "=========================================="
echo ""
echo "Quick start:"
echo "  python3 idrac_iso_tool.py -H <idrac-ip> -u <user> -i <iso-url>"
echo ""
echo "Example:"
echo "  python3 idrac_iso_tool.py -H 10.0.0.25 -u root -i http://repo.local/ubuntu.iso"
echo ""
