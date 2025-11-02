#!/bin/bash

# OCR Service Diagnostic Script
# Run this on the Proxy VM to check OCR service connectivity

echo "🔍 OCR Service Diagnostics"
echo "=========================="
echo ""

OCR_SERVICE_URL="${OCR_SERVICE_URL:-http://4.229.225.140}"
OCR_IP="4.229.225.140"

echo "📍 OCR Service URL: $OCR_SERVICE_URL"
echo ""

# 1. Check network connectivity
echo "1️⃣ Testing network connectivity..."
if ping -c 3 $OCR_IP > /dev/null 2>&1; then
    echo "   ✅ Can ping OCR VM ($OCR_IP)"
else
    echo "   ❌ Cannot ping OCR VM ($OCR_IP)"
    echo "   → Check firewall rules and network security groups"
fi
echo ""

# 2. Check if port 80 is open
echo "2️⃣ Testing port 80 connectivity..."
if timeout 5 bash -c "cat < /dev/null > /dev/tcp/$OCR_IP/80" 2>/dev/null; then
    echo "   ✅ Port 80 is open on OCR VM"
else
    echo "   ❌ Port 80 is not accessible on OCR VM"
    echo "   → Check if Nginx is running: sudo systemctl status nginx"
fi
echo ""

# 3. Check health endpoint
echo "3️⃣ Testing OCR health endpoint..."
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 "$OCR_SERVICE_URL/api/health" 2>/dev/null)
if [ "$HEALTH_RESPONSE" = "200" ]; then
    echo "   ✅ Health endpoint responding (200 OK)"
    curl -s "$OCR_SERVICE_URL/api/health" | jq '.' 2>/dev/null || echo "   Response: $(curl -s $OCR_SERVICE_URL/api/health)"
elif [ "$HEALTH_RESPONSE" = "502" ]; then
    echo "   ❌ Health endpoint returning 502 Bad Gateway"
    echo "   → OCR service is down or not responding"
    echo "   → Check OCR service status on OCR VM"
else
    echo "   ❌ Health endpoint not responding (HTTP $HEALTH_RESPONSE)"
fi
echo ""

# 4. Check if OCR service is running (if on OCR VM)
echo "4️⃣ OCR Service Status (run this on OCR VM):"
echo "   sudo systemctl status qadam-ocr"
echo "   sudo journalctl -u qadam-ocr -n 50 --no-pager"
echo ""

# 5. Check Nginx status (if on OCR VM)
echo "5️⃣ Nginx Status (run this on OCR VM):"
echo "   sudo systemctl status nginx"
echo "   sudo nginx -t"
echo ""

# 6. Test OCR extraction
echo "6️⃣ Testing OCR extraction endpoint..."
TEST_IMAGE="iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
EXTRACT_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 \
    -X POST "$OCR_SERVICE_URL/api/extract-text" \
    -H "Content-Type: application/json" \
    -d "{\"image_base64\": \"$TEST_IMAGE\", \"language\": \"en\"}" 2>/dev/null)

if [ "$EXTRACT_RESPONSE" = "200" ]; then
    echo "   ✅ OCR extraction endpoint working (200 OK)"
elif [ "$EXTRACT_RESPONSE" = "502" ]; then
    echo "   ❌ OCR extraction endpoint returning 502 Bad Gateway"
else
    echo "   ❌ OCR extraction endpoint not responding (HTTP $EXTRACT_RESPONSE)"
fi
echo ""

# 7. Recommendations
echo "📋 Troubleshooting Steps:"
echo "========================"
echo ""
echo "If you see 502 errors, run these commands ON THE OCR VM (4.229.225.140):"
echo ""
echo "1. Check if OCR service is running:"
echo "   sudo systemctl status qadam-ocr"
echo ""
echo "2. If not running, start it:"
echo "   sudo systemctl start qadam-ocr"
echo ""
echo "3. Check service logs:"
echo "   sudo journalctl -u qadam-ocr -n 100 --no-pager"
echo ""
echo "4. Check Nginx status:"
echo "   sudo systemctl status nginx"
echo ""
echo "5. Test OCR service directly (bypass Nginx):"
echo "   curl http://localhost:8000/api/health"
echo ""
echo "6. Check Nginx error logs:"
echo "   sudo tail -f /var/log/nginx/error.log"
echo ""
echo "7. Restart services if needed:"
echo "   sudo systemctl restart qadam-ocr"
echo "   sudo systemctl restart nginx"
echo ""
