# Proxy Debug Deployment Instructions

## Issue Identified
The AI service is still receiving `solution_type: step-by-step` even when frontend sends `with-diagram`. We need to debug what the proxy is actually receiving and forwarding.

## Debug Code Deployed
I've added debug logging to the proxy (backend-proxy branch, commit `1b84645`):

### Debug Points Added:
1. **Proxy App** (`app.py`):
   - Shows full request data received from frontend
   - Shows extracted `solution_type` value
   - Shows all available keys in request

2. **AI Client** (`ai_client.py`):
   - Shows exact payload being sent to AI service
   - Confirms `solution_type` is included in the forward

## Deployment Steps

### 1. Deploy to Proxy Server (130.107.48.166)
```bash
# SSH into proxy server
ssh your-user@130.107.48.166

# Navigate to backend directory
cd /opt/qadam-backend/proxy

# Pull latest changes
git pull origin backend-proxy

# Restart the proxy service
sudo systemctl restart qadam-backend

# Check status
sudo systemctl status qadam-backend
```

### 2. Test and Monitor Logs
```bash
# Monitor proxy logs in real-time
sudo journalctl -u qadam-backend -f

# In another terminal, test with a question
curl -X POST http://localhost:5000/solve-question \
  -H "Content-Type: application/json" \
  -d '{
    "question_text": "Construct a triangle ABC",
    "subject": "Mathematics",
    "solution_type": "with-diagram"
  }'
```

### 3. Expected Debug Output
You should see logs like:
```
🔍 DEBUG: Received request data: {'question_text': '...', 'subject': 'Mathematics', 'solution_type': 'with-diagram'}
🔍 DEBUG: Extracted solution_type: with-diagram
🔍 DEBUG: Available keys in request: ['question_text', 'subject', 'solution_type']
🔍 DEBUG: Sending payload to AI service: {'question_text': '...', 'subject': 'Mathematics', 'context': '', 'solution_type': 'with-diagram'}
```

## Possible Issues & Solutions

### Issue 1: Frontend not deployed yet
- **Symptom**: Debug shows `solution_type: step-by-step` (default)
- **Solution**: Wait for Azure frontend deployment, clear cache

### Issue 2: Proxy not receiving solution_type
- **Symptom**: Debug shows `solution_type` key missing from request
- **Solution**: Frontend deployment issue, check browser network tab

### Issue 3: AI service still getting step-by-step
- **Symptom**: Debug shows correct `with-diagram` but AI logs show `step-by-step`
- **Solution**: AI service caching issue, restart AI service

## Quick Test After Deployment

1. **Check proxy logs**:
   ```bash
   sudo journalctl -u qadam-backend -n 50
   ```

2. **Test from frontend**:
   - Open the application
   - Select "📊 With Diagram"
   - Submit triangle construction question
   - Check proxy logs for debug output

3. **Verify AI service receives correct type**:
   - AI logs should show: `solution_type: with-diagram`
   - If still shows `step-by-step`, there's a forwarding issue

## Next Steps After Debug

Once we see the debug output, we'll know exactly where the issue is:
- **If proxy receives `with-diagram`** → Issue is in proxy→AI forwarding
- **If proxy receives `step-by-step`** → Issue is in frontend→proxy sending
- **If AI receives correct** → Issue is in AI service processing

The debug logs will give us the complete picture!
