#!/bin/bash

echo "Testing diagram endpoint pull from backend-proxy branch..."

# SSH into server and test
ssh qadamuser@130.107.48.166 << 'EOF'
cd /opt/qadam-backend
echo "Current branch: $(git branch --show-current)"
echo "Pulling backend-proxy branch..."
git pull origin backend-proxy
echo "Checking if diagram_endpoint.py exists:"
ls -la diagram_endpoint.py
echo "First 10 lines of diagram_endpoint.py:"
head -10 diagram_endpoint.py
EOF

echo "Test completed!"
