#!/bin/bash
# Update .env file on the backend proxy server
# Run this script to fix the "AI features are not enabled" issue

echo "🔧 Updating .env file on backend proxy..."

# Configuration
SERVER_IP="130.107.48.166"
SERVER_USER="qadamuser"
APP_DIR="/opt/qadam-backend/proxy"

# Create the updated .env content
cat > /tmp/new_env.txt << 'EOF'
# AI Service Configuration
AI_SERVICE_URL=http://130.107.48.221:8001

# Backend Configuration
SECRET_KEY=your-secret-key-here-change-in-production
BACKEND_HTTPS=true

# Database Configuration (if using MySQL)
# DB_HOST=localhost
# DB_USER=qadam_user
# DB_PASSWORD=your_password
# DB_NAME=qadam_db

# Azure Blob Storage (optional)
# AZURE_STORAGE_CONNECTION_STRING=your_azure_storage_connection_string_here
# BLOB_CONTAINER_NAME=qadam-uploads

# OCR Service Configuration
OCR_SERVICE_URL=http://130.107.48.145:8000
EOF

echo "📤 Copying updated .env to server..."
scp /tmp/new_env.txt ${SERVER_USER}@${SERVER_IP}:/tmp/new_env.txt

echo "🔧 Installing .env file on server..."
ssh ${SERVER_USER}@${SERVER_IP} "sudo cp /tmp/new_env.txt ${APP_DIR}/.env && sudo chown qadamuser:qadamuser ${APP_DIR}/.env && sudo chmod 644 ${APP_DIR}/.env"

echo "🔄 Restarting backend service..."
ssh ${SERVER_USER}@${SERVER_IP} "sudo systemctl restart qadam-backend"

echo "✅ .env file updated and service restarted!"
echo ""
echo "Testing AI service connectivity..."
ssh ${SERVER_USER}@${SERVER_IP} "cd ${APP_DIR} && source venv/bin/activate && python -c 'from ai_client import check_ai_service; print(\"AI Service Available:\", check_ai_service())'"

echo ""
echo "Testing /solve-question endpoint..."
ssh ${SERVER_USER}@${SERVER_IP} "curl -X POST http://localhost:5000/solve-question -H 'Content-Type: application/json' -d '{\"question_text\":\"What is 2+2?\",\"subject\":\"Mathematics\",\"solution_type\":\"step-by-step\"}' -w '\nStatus: %{http_code}\n'"
