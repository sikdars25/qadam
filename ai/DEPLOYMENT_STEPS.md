# AI Service Deployment Steps

## Quick Deployment on AI VM

### Step 1: Navigate to AI Directory
```bash
cd /opt/qadam-ai/ai
```

### Step 2: Stash Local Changes (if any)
```bash
git stash
```

### Step 3: Pull Latest Code
```bash
git pull origin backend-ai
```

### Step 4: Install Missing Dependencies
```bash
# Install requests module (required by IntelligentQuestionSolver)
pip3 install requests

# Or install all requirements
pip3 install -r requirements.txt
```

### Step 5: Verify Environment Variables
```bash
# Check if API keys are configured
cat .env | grep -E "GROQ_API_KEY|WOLFRAM_APP_ID"
```

If not configured, add them:
```bash
echo "GROQ_API_KEY=your_groq_api_key_here" >> .env
echo "WOLFRAM_APP_ID=your_wolfram_app_id_here" >> .env
```

### Step 6: Restart the Service
```bash
sudo systemctl restart qadam-ai
```

### Step 7: Verify Service Started Successfully
```bash
sudo systemctl status qadam-ai
```

Should show: `Active: active (running)`

### Step 8: Monitor Logs
```bash
sudo journalctl -u qadam-ai -f
```

You should see:
```
✅ Intelligent Question Solver loaded successfully
✅ Groq API: Available
✅ TF-IDF Vectorizer: Available
 * Running on http://127.0.0.1:8001
```

---

## Troubleshooting

### Issue 1: ModuleNotFoundError: No module named 'requests'

**Error:**
```
ModuleNotFoundError: No module named 'requests'
```

**Solution:**
```bash
cd /opt/qadam-ai/ai
pip3 install requests
sudo systemctl restart qadam-ai
```

### Issue 2: NameError: name 'logger' is not defined

**Error:**
```
NameError: name 'logger' is not defined
```

**Solution:**
This is fixed in the latest code. Pull the latest version:
```bash
cd /opt/qadam-ai/ai
git pull origin backend-ai
sudo systemctl restart qadam-ai
```

### Issue 3: Intelligent Question Solver not available

**Warning in logs:**
```
⚠️ Intelligent Question Solver not available: <error>
```

**Check:**
1. Is `requests` installed?
   ```bash
   pip3 show requests
   ```

2. Are API keys configured?
   ```bash
   cat .env | grep -E "GROQ_API_KEY|WOLFRAM_APP_ID"
   ```

3. Check the actual error:
   ```bash
   sudo journalctl -u qadam-ai -n 50 | grep "Intelligent Question Solver"
   ```

### Issue 4: Service fails to start

**Check logs:**
```bash
sudo journalctl -u qadam-ai -n 100 --no-pager
```

**Common causes:**
- Missing Python dependencies
- Missing environment variables
- Port 8001 already in use
- Permission issues

**Solutions:**
```bash
# Install all dependencies
pip3 install -r /opt/qadam-ai/ai/requirements.txt

# Check port usage
sudo lsof -i :8001

# Check permissions
ls -la /opt/qadam-ai/ai/
```

### Issue 5: Wolfram logs not appearing

**Check:**
1. Is IntelligentQuestionSolver loaded?
   ```bash
   sudo journalctl -u qadam-ai | grep "Intelligent Question Solver loaded"
   ```

2. Is the endpoint being called with intelligent solver?
   ```bash
   curl -X POST http://localhost:8001/api/solve-question \
     -H "Content-Type: application/json" \
     -d '{"question_text": "Find x where 2x + 5 = 15", "use_intelligent_solver": true}'
   ```

3. Monitor logs while making request:
   ```bash
   sudo journalctl -u qadam-ai -f
   ```

---

## Verification Tests

### Test 1: Check Service Status
```bash
sudo systemctl status qadam-ai
```

**Expected:** `Active: active (running)`

### Test 2: Check Health Endpoint
```bash
curl http://localhost:8001/api/health
```

**Expected:**
```json
{
  "status": "healthy",
  "service": "AI Service",
  "version": "1.0"
}
```

### Test 3: Test Question Solving
```bash
curl -X POST http://localhost:8001/api/solve-question \
  -H "Content-Type: application/json" \
  -d '{
    "question_text": "Find x where 2x + 5 = 15",
    "subject": "Algebra",
    "use_intelligent_solver": true
  }'
```

**Expected:** JSON response with solution and extracted expressions

### Test 4: Verify Wolfram Logs
```bash
# In one terminal, monitor logs
sudo journalctl -u qadam-ai -f

# In another terminal, send request
curl -X POST http://localhost:8001/api/solve-question \
  -H "Content-Type: application/json" \
  -d '{"question_text": "Solve 2x + 5 = 15"}'
```

**Expected in logs:**
```
INFO:__main__:🤖 Using Intelligent Question Solver with Groq + Wolfram Alpha
INFO:__main__:================================================================================
INFO:__main__:WOLFRAM ALPHA API CALL - Expression ID: expr_1
INFO:__main__:Original Expression: 2x + 5 = 15
INFO:__main__:Query to Wolfram: 2x + 5 = 15
...
INFO:__main__:Final Result: x = 5
INFO:__main__:================================================================================
```

---

## Complete Deployment Checklist

- [ ] Navigate to `/opt/qadam-ai/ai`
- [ ] Stash local changes: `git stash`
- [ ] Pull latest code: `git pull origin backend-ai`
- [ ] Install dependencies: `pip3 install -r requirements.txt`
- [ ] Verify API keys in `.env` file
- [ ] Restart service: `sudo systemctl restart qadam-ai`
- [ ] Check service status: `sudo systemctl status qadam-ai`
- [ ] Verify IntelligentQuestionSolver loaded in logs
- [ ] Test health endpoint
- [ ] Test question solving endpoint
- [ ] Verify Wolfram logs appear in journalctl
- [ ] Monitor for any errors

---

## Dependencies Required

### Python Packages
```
requests>=2.31.0
python-dotenv>=1.0.0
flask
flask-cors
groq
```

### Environment Variables
```
GROQ_API_KEY=<your_groq_api_key>
WOLFRAM_APP_ID=<your_wolfram_app_id>
```

### System Requirements
- Python 3.8+
- Port 8001 available
- Internet access for API calls

---

## Rollback Procedure

If deployment fails:

```bash
cd /opt/qadam-ai/ai

# Restore previous version
git stash pop  # If you stashed changes
# OR
git reset --hard HEAD~1  # Revert to previous commit

# Restart service
sudo systemctl restart qadam-ai

# Verify service is running
sudo systemctl status qadam-ai
```

---

## Post-Deployment Monitoring

### Monitor Logs Continuously
```bash
sudo journalctl -u qadam-ai -f
```

### Check for Errors
```bash
sudo journalctl -u qadam-ai -p err --since "10 minutes ago"
```

### Monitor Wolfram API Calls
```bash
sudo journalctl -u qadam-ai | grep "WOLFRAM ALPHA API CALL"
```

### Check Processing Times
```bash
sudo journalctl -u qadam-ai | grep "processing_time_seconds"
```

### Monitor Service Restarts
```bash
sudo journalctl -u qadam-ai | grep "Started qadam-ai.service"
```

---

## Summary

**Quick Deploy:**
```bash
cd /opt/qadam-ai/ai && \
git stash && \
git pull origin backend-ai && \
pip3 install -r requirements.txt && \
sudo systemctl restart qadam-ai && \
sudo journalctl -u qadam-ai -f
```

**Verify:**
- ✅ Service running
- ✅ IntelligentQuestionSolver loaded
- ✅ Wolfram logs appearing
- ✅ API responding correctly

**Monitor:**
```bash
sudo journalctl -u qadam-ai -f | grep --line-buffered "WOLFRAM"
```
