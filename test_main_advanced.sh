#!/bin/bash
# Quick test of advanced features integration

echo "Testing advanced features in main.py..."
echo ""
echo "Test input: Use advanced features + pregnant patient with UTI"
echo ""

# Simulate user input
echo -e "y\ny\n28\nfemale\ny\nn\nn\nn\nfrequent urination burning sensation\nquit" | python main.py
