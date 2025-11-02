#!/bin/bash
# Check session configuration and test login

echo "🔍 Checking Session Configuration..."
echo ""

cd /opt/qadam-backend/proxy

# Check CORS configuration
echo "1️⃣ CORS Configuration:"
grep -A 10 "CORS(app" app.py | head -15

echo ""
echo "2️⃣ Session Cookie Configuration:"
grep -A 5 "SESSION_COOKIE" app.py | head -10

echo ""
echo "3️⃣ Test Login Endpoint:"
echo "   Sending login request..."
curl -v -X POST https://130.107.48.166/api/login \
  -H "Content-Type: application/json" \
  -H "Origin: https://zealous-ocean-06e22b51e.3.azurestaticapps.net" \
  -d '{"username":"student1","password":"student123"}' \
  -c cookies.txt \
  2>&1 | grep -E "(Set-Cookie|Access-Control|HTTP/)"

echo ""
echo "4️⃣ Cookies Received:"
cat cookies.txt 2>/dev/null || echo "   No cookies file"

echo ""
echo "5️⃣ Test Authenticated Request:"
echo "   Using cookies from login..."
curl -v https://130.107.48.166/api/user/profile \
  -H "Origin: https://zealous-ocean-06e22b51e.3.azurestaticapps.net" \
  -b cookies.txt \
  2>&1 | grep -E "(HTTP/|user_id)"

rm -f cookies.txt

echo ""
echo "✅ Diagnostics complete"
