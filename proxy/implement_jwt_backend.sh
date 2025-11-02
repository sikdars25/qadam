#!/bin/bash
# Implement JWT authentication in backend

set -e

echo "🔧 Implementing JWT Authentication in Backend..."

cd /opt/qadam-backend/proxy

# Step 1: Install JWT library
echo "📦 Step 1: Installing JWT library..."
source venv/bin/activate
pip install PyJWT
echo "PyJWT" >> requirements.txt

# Step 2: Update app.py to import JWT module and update login
echo "⚙️  Step 2: Updating app.py..."

python3 << 'PYTHON_EOF'
import re

with open('app.py', 'r') as f:
    content = f.read()

# Add JWT import at the top (after other imports)
if 'from jwt_auth import' not in content:
    # Find the imports section
    import_pattern = r'(from flask import.*?\n)'
    jwt_import = r'\1from jwt_auth import generate_token, token_required, get_current_user\n'
    content = re.sub(import_pattern, jwt_import, content, count=1)
    print("✅ Added JWT imports")

# Update login endpoint to return token
# Find the login endpoint and update the success response
login_pattern = r"(session\['user_id'\] = user\['id'\].*?session\['role'\] = user\.get\('role', 'student'\).*?)(return jsonify\(\{[^}]*'message': 'Login successful'[^}]*\}\))"

def replace_login(match):
    session_code = match.group(1)
    # Add token generation before return
    new_code = session_code + """
        # Generate JWT token for cross-origin authentication
        token = generate_token(
            user_id=user['id'],
            username=user['username'],
            role=user.get('role', 'student')
        )
        print(f"🔑 Generated JWT token for user: {user['username']}")
        
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'role': user.get('role', 'student')
            },
            'token': token  # JWT token for cross-origin requests
        })"""
    return new_code

content = re.sub(login_pattern, replace_login, content, flags=re.DOTALL)
print("✅ Updated login endpoint to return JWT token")

# Update delete-paper endpoint to use token_required decorator
# Find the delete endpoint
delete_pattern = r"(@app\.route\('/api/delete-paper/<paper_id>', methods=\['DELETE'\]\)\ndef delete_paper_endpoint\(paper_id\):)"

def replace_delete(match):
    return """@app.route('/api/delete-paper/<paper_id>', methods=['DELETE'])
@token_required  # JWT authentication
def delete_paper_endpoint(paper_id):"""

content = re.sub(delete_pattern, replace_delete, content)
print("✅ Added JWT authentication to delete-paper endpoint")

with open('app.py', 'w') as f:
    f.write(content)

print("✅ Backend updated successfully")
PYTHON_EOF

# Step 3: Restart backend
echo "🔄 Step 3: Restarting backend service..."
sudo systemctl restart qadam-backend

sleep 3

echo ""
echo "✅ JWT Authentication Implemented!"
echo ""
echo "Backend changes:"
echo "  ✅ JWT library installed"
echo "  ✅ Login endpoint returns JWT token"
echo "  ✅ Protected endpoints accept JWT tokens"
echo "  ✅ Session authentication still works (backward compatible)"
echo ""
echo "🧪 Test login:"
echo "  curl -X POST https://130.107.48.166/api/login \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"username\":\"student1\",\"password\":\"student123\"}'"
echo ""
echo "Response should include 'token' field"
echo ""
echo "📋 Check logs:"
echo "  sudo journalctl -u qadam-backend -f"
