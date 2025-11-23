# Fix "AI features are not enabled" Error

## Root Cause
The backend proxy was missing the `.env` file with the `AI_SERVICE_URL` configuration, causing the AI client to fail at startup.

## Quick Fix (run these commands on the backend proxy server: 130.107.48.166)

```bash
# 1. Navigate to the proxy directory
cd /opt/qadam-backend/proxy

# 2. Create the .env file with AI service configuration
sudo tee .env > /dev/null << 'EOF'
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

# 3. Set proper permissions
sudo chmod 644 .env
sudo chown qadamuser:qadamuser .env

# 4. Restart the backend service
sudo systemctl restart qadam-backend

# 5. Check if AI service is now available
cd /opt/qadam-backend/proxy
source venv/bin/activate
python -c "from ai_client import check_ai_service; print('AI Service Available:', check_ai_service())"

# 6. Test the solve-question endpoint
curl -X POST http://localhost:5000/solve-question \
  -H "Content-Type: application/json" \
  -d '{"question_text":"What is 2+2?","subject":"Mathematics","solution_type":"step-by-step"}' \
  -w '\nStatus: %{http_code}\n'
```

## Expected Results
After running these commands:
- The AI service should show as "Available: True"
- The `/solve-question` endpoint should return `Status: 200` with a proper solution
- The frontend should no longer show "AI features are not enabled"

## Verification
Check the service logs:
```bash
sudo journalctl -u qadam-backend -f
```

You should see:
- `✅ AI service available at http://130.107.48.221:8001`
- No more 503 errors for `/solve-question` requests
