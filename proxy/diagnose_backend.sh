#!/bin/bash
# Diagnose Backend Connection Issues

echo "🔍 BACKEND DIAGNOSTICS"
echo "=" * 60

# Check if backend service is running
echo ""
echo "1️⃣ Backend Service Status:"
sudo systemctl status qadam-backend --no-pager -l | head -10

# Check if gunicorn is listening
echo ""
echo "2️⃣ Gunicorn Process:"
ps aux | grep gunicorn | grep -v grep

# Check if port 5000 is listening
echo ""
echo "3️⃣ Port 5000 (Gunicorn):"
sudo netstat -tlnp | grep :5000

# Check if Nginx is running
echo ""
echo "4️⃣ Nginx Status:"
sudo systemctl status nginx --no-pager -l | head -5

# Check if port 80 is listening
echo ""
echo "5️⃣ Port 80 (Nginx):"
sudo netstat -tlnp | grep :80

# Check Nginx configuration
echo ""
echo "6️⃣ Nginx Configuration:"
sudo nginx -t

# Check firewall
echo ""
echo "7️⃣ Firewall Status (UFW):"
sudo ufw status | grep -E "80|5000"

# Test local connection
echo ""
echo "8️⃣ Test Local Connection:"
echo "   Testing http://localhost:5000/api/health"
curl -s http://localhost:5000/api/health || echo "   ❌ Failed"

echo ""
echo "   Testing http://127.0.0.1/api/health (via Nginx)"
curl -s http://127.0.0.1/api/health || echo "   ❌ Failed"

# Check recent logs
echo ""
echo "9️⃣ Recent Backend Logs:"
sudo journalctl -u qadam-backend -n 20 --no-pager

echo ""
echo "🔟 Recent Nginx Logs:"
sudo tail -n 10 /var/log/nginx/error.log

echo ""
echo "=" * 60
echo "✅ Diagnostics Complete"
