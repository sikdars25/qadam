#!/bin/bash

echo "🔍 OCR VM Deployment Status Check"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "ℹ️  $1"
}

echo "1. Checking OCR Service Directory..."
if [ -d "/opt/qadam-ocr" ]; then
    print_status 0 "OCR directory exists"
    cd /opt/qadam-ocr
else
    print_status 1 "OCR directory not found at /opt/qadam-ocr"
    exit 1
fi

echo ""
echo "2. Checking Git Branch..."
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" = "backend-ocr" ]; then
    print_status 0 "On correct branch: $CURRENT_BRANCH"
else
    print_status 1 "Wrong branch: $CURRENT_BRANCH (should be backend-ocr)"
fi

echo ""
echo "3. Checking Latest Commit..."
LATEST_COMMIT=$(git log --oneline -1)
echo "Latest commit: $LATEST_COMMIT"

if [[ "$LATEST_COMMIT" == *"deployment verification tools"* ]]; then
    print_status 0 "Has latest deployment fix"
else
    print_warning "May not have latest code"
fi

echo ""
echo "4. Checking Service Status..."
if sudo systemctl is-active --quiet qadam-ocr; then
    print_status 0 "OCR service is running"
else
    print_status 1 "OCR service is not running"
fi

echo ""
echo "5. Checking Service Enabled Status..."
if sudo systemctl is-enabled --quiet qadam-ocr; then
    print_status 0 "OCR service is enabled on boot"
else
    print_warning "OCR service is not enabled on boot"
fi

echo ""
echo "6. Testing Mathematical Symbol Fix..."
cd ocr
if python verify_deployment.py > /dev/null 2>&1; then
    print_status 0 "Mathematical symbol fix is working"
else
    print_status 1 "Mathematical symbol fix is not working"
fi

echo ""
echo "7. Checking Recent Logs..."
echo "Recent service logs:"
sudo journalctl -u qadam-ocr --no-pager -n 5 --no-pager

echo ""
echo "8. Testing API Health..."
if curl -s http://localhost:5000/api/health > /dev/null; then
    print_status 0 "OCR API is responding"
else
    print_status 1 "OCR API is not responding"
fi

echo ""
echo "=================================="
echo "🎯 Deployment Status Summary:"
echo "=================================="

# Final summary
if sudo systemctl is-active --quiet qadam-ocr && \
   [ "$CURRENT_BRANCH" = "backend-ocr" ] && \
   python verify_deployment.py > /dev/null 2>&1; then
    
    echo -e "${GREEN}🎉 DEPLOYMENT STATUS: HEALTHY${NC}"
    echo "✅ All systems operational with latest fixes"
    echo "✅ Mathematical symbol corrections are working"
else
    echo -e "${RED}⚠️  DEPLOYMENT STATUS: NEEDS ATTENTION${NC}"
    echo ""
    echo "Recommended actions:"
    if [ "$CURRENT_BRANCH" != "backend-ocr" ]; then
        echo "- Switch to backend-ocr branch"
    fi
    if ! sudo systemctl is-active --quiet qadam-ocr; then
        echo "- Start/restart the OCR service"
    fi
    if ! python verify_deployment.py > /dev/null 2>&1; then
        echo "- Update code and restart service"
    fi
    
    echo ""
    echo "Run this to update:"
    echo "cd /opt/qadam-ocr"
    echo "git fetch origin backend-ocr"
    echo "git reset --hard origin/backend-ocr"
    echo "sudo systemctl restart qadam-ocr"
fi

echo ""
