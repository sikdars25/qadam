#!/bin/bash

# Deploy proxy debug code to trace diagram data flow

echo "🔧 Deploying Proxy Debug Code..."
echo "================================"

# SSH into proxy server and deploy
ssh your-user@130.107.48.166 << 'EOF'
echo "📍 On proxy server..."
cd /opt/qadam-backend/proxy

# Check current branch
echo "📋 Current branch:"
git branch

# Pull latest debug code
echo "📥 Pulling debug code..."
git pull origin backend-proxy

# Restart service
echo "🔄 Restarting proxy service..."
sudo systemctl restart qadam-backend

# Check status
echo "📊 Service status:"
sudo systemctl status qadam-backend --no-pager

echo ""
echo "✅ Proxy debug deployment complete!"
echo "📝 Monitor logs with: sudo journalctl -u qadam-backend -f"
EOF

echo ""
echo "🧪 After deployment, test with:"
echo "curl -X POST http://130.107.48.166:5000/solve-question \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"question_text\": \"Construct a triangle ABC\", \"subject\": \"Mathematics\", \"solution_type\": \"with-diagram\"}'"
