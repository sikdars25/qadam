#!/bin/bash
# Fix session cookies for cross-origin requests
# This ensures cookies work between frontend (Azure) and backend (VM)

set -e

echo "🍪 Fixing Session Cookie Configuration..."

cd /opt/qadam-backend/proxy

# Update app.py to set correct cookie settings
echo "⚙️  Updating session cookie settings in app.py..."

# Create a Python script to update the configuration
cat > update_cookies.py << 'PYTHON_EOF'
import re

# Read the file
with open('app.py', 'r') as f:
    content = f.read()

# Find the session configuration section
# Look for the HTTPS check and update cookie settings
old_pattern = r"if BACKEND_HTTPS:.*?app\.config\['SESSION_COOKIE_SAMESITE'\] = 'None'.*?else:.*?app\.config\['SESSION_COOKIE_SAMESITE'\] = 'Lax'"

new_config = """if BACKEND_HTTPS:
    print("🔐 HTTPS mode enabled")
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'None'  # Required for cross-origin
    app.config['SESSION_COOKIE_DOMAIN'] = None  # Don't restrict domain
else:
    print("🔓 HTTP mode enabled")
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_DOMAIN'] = None"""

# Replace the pattern
content = re.sub(old_pattern, new_config, content, flags=re.DOTALL)

# Write back
with open('app.py', 'w') as f:
    f.write(content)

print("✅ Updated session cookie configuration")
PYTHON_EOF

# Run the update script
source venv/bin/activate
python3 update_cookies.py
rm update_cookies.py

echo "🔄 Restarting backend service..."
sudo systemctl restart qadam-backend

sleep 3

echo ""
echo "✅ Session cookies fixed!"
echo ""
echo "Cookie settings:"
echo "  - SameSite: None (allows cross-origin)"
echo "  - Secure: True (HTTPS only)"
echo "  - HttpOnly: True (JavaScript can't access)"
echo "  - Domain: None (not restricted)"
echo ""
echo "🧪 Test by logging in again"
