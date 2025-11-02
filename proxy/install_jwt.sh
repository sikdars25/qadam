#!/bin/bash
# Install JWT library for token-based authentication

set -e

echo "📦 Installing JWT library..."

cd /opt/qadam-backend/proxy

# Activate virtual environment
source venv/bin/activate

# Install PyJWT
pip install PyJWT

# Update requirements.txt
pip freeze | grep PyJWT >> requirements.txt

echo "✅ JWT library installed!"
echo ""
echo "Next steps:"
echo "  1. Update backend code to generate and validate JWT tokens"
echo "  2. Update frontend to store and send tokens"
