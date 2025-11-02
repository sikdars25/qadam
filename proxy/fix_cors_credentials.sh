#!/bin/bash
# Fix CORS to allow credentials from Azure Static Web Apps
# This enables session cookies to work across domains

set -e

echo "🔧 Fixing CORS for Cross-Origin Credentials..."

cd /opt/qadam-backend/proxy

# Backup app.py
cp app.py app.py.backup

# Update CORS configuration
echo "⚙️  Updating CORS configuration..."

python3 << 'PYTHON_EOF'
import re

with open('app.py', 'r') as f:
    content = f.read()

# Find the CORS configuration
# Look for the CORS(app) line and replace with proper configuration
old_cors = r"CORS\(app\)"

new_cors = """CORS(app, 
    resources={r"/api/*": {"origins": [
        "https://zealous-ocean-06e22b51e.3.azurestaticapps.net",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]}},
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)"""

content = re.sub(old_cors, new_cors, content)

with open('app.py', 'w') as f:
    f.write(content)

print("✅ Updated CORS configuration")
PYTHON_EOF

echo "🔄 Restarting backend service..."
sudo systemctl restart qadam-backend

sleep 3

echo ""
echo "✅ CORS credentials fixed!"
echo ""
echo "CORS settings:"
echo "  - Origins: Azure Static Web Apps + localhost"
echo "  - Credentials: Enabled"
echo "  - Methods: GET, POST, PUT, DELETE, OPTIONS"
echo ""
echo "🧪 Test:"
echo "  1. Clear browser cookies"
echo "  2. Login again"
echo "  3. Try deleting a paper"
echo ""
echo "📋 Check logs:"
echo "  sudo journalctl -u qadam-backend -f"
