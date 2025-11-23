# Fix AI Service URL in .env

## Problem
The server's `.env` file has `AI_SERVICE_URL=http://172.17.0.4:8001` (internal Docker IP) instead of the external IP `http://130.107.48.221:8001`.

## Solution (run these commands on gadam-backend-proxy: 130.107.48.166)

```bash
# 1. Backup current .env file
sudo cp .env .env.backup

# 2. Update AI_SERVICE_URL to use external IP
sudo sed -i 's/AI_SERVICE_URL=http:\/\/172.17.0.4:8001/AI_SERVICE_URL=http:\/\/130.107.48.221:8001/' .env

# 3. Add missing BACKEND_HTTPS=true if not present
if ! grep -q "BACKEND_HTTPS=true" .env; then
    echo "BACKEND_HTTPS=true" | sudo tee -a .env
fi

# 4. Verify the change
grep "AI_SERVICE_URL" .env
grep "BACKEND_HTTPS" .env

# 5. Restart the backend service
sudo systemctl restart qadam-backend

# 6. Check service status
sudo systemctl status qadam-backend

# 7. Test AI service connectivity
cd /opt/qadam-backend/proxy
source venv/bin/activate
python -c "from ai_client import check_ai_service; print('AI Service Available:', check_ai_service())"

# 8. Test the solve-question endpoint
curl -X POST http://localhost:5000/solve-question \
  -H "Content-Type: application/json" \
  -d '{"question_text":"What is 2+2?","subject":"Mathematics","solution_type":"step-by-step"}' \
  -w '\nStatus: %{http_code}\n'
```

## Expected Output
After running these commands:
- `AI_SERVICE_URL` should show `http://130.107.48.221:8001`
- `AI Service Available: True`
- `Status: 200` for the solve-question test

## Manual Alternative
If the sed command doesn't work, you can manually edit the file:

```bash
sudo nano .env
# Find the line: AI_SERVICE_URL=http://172.17.0.4:8001
# Change it to: AI_SERVICE_URL=http://130.107.48.221:8001
# Save and exit (Ctrl+X, Y, Enter)
```
