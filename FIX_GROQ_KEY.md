# Fix Groq API Key Not Loading

## Issue
After setting GROQ_API_KEY in the systemd service file, it's still showing as `false`.

## Troubleshooting Steps

### Step 1: Verify the service file content

```bash
sudo cat /etc/systemd/system/qadam-ai.service | grep GROQ
```

**Expected output:**
```
Environment="GROQ_API_KEY=gsk_YOUR_KEY_HERE"
```

**If you see `your_groq_api_key_here`** → The key wasn't updated properly

### Step 2: Check if the service is using the right file

```bash
sudo systemctl status qadam-ai
```

Look for the line that shows which service file it's using.

### Step 3: Edit the service file correctly

```bash
sudo nano /etc/systemd/system/qadam-ai.service
```

The file should look like this:

```ini
[Unit]
Description=Qadam AI Service
After=network.target

[Service]
Type=simple
User=qadamuser
WorkingDirectory=/opt/qadam-ai/ai
Environment="GROQ_API_KEY=gsk_YOUR_ACTUAL_KEY_HERE"
ExecStart=/opt/qadam-ai/ai/venv/bin/python3 app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**IMPORTANT:** Replace `gsk_YOUR_ACTUAL_KEY_HERE` with your real Groq API key!

### Step 4: Reload and restart

```bash
sudo systemctl daemon-reload
sudo systemctl restart qadam-ai
sudo systemctl status qadam-ai
```

### Step 5: Check logs for errors

```bash
sudo journalctl -u qadam-ai -n 50 --no-pager
```

Look for lines like:
- ✅ `✅ Groq API initialized`
- ❌ `⚠️ GROQ_API_KEY not set`

### Step 6: Verify the key is loaded

```bash
curl http://localhost:8001/api/health
```

**Expected:**
```json
{
  "features": {
    "groq_api": true,  ← Should be true!
    ...
  }
}
```

## Alternative: Set via Environment File

If the service file approach doesn't work, create an environment file:

```bash
# Create environment file
sudo nano /opt/qadam-ai/ai/.env
```

Add this line:
```
GROQ_API_KEY=gsk_YOUR_ACTUAL_KEY_HERE
```

Then update the service file:
```bash
sudo nano /etc/systemd/system/qadam-ai.service
```

Change the `Environment=` line to:
```ini
EnvironmentFile=/opt/qadam-ai/ai/.env
```

Then reload and restart:
```bash
sudo systemctl daemon-reload
sudo systemctl restart qadam-ai
```

## Quick Test Commands

Run these on the VM to verify:

```bash
# 1. Check service file
echo "=== Service File ==="
sudo cat /etc/systemd/system/qadam-ai.service

# 2. Check service status
echo "=== Service Status ==="
sudo systemctl status qadam-ai

# 3. Check recent logs
echo "=== Recent Logs ==="
sudo journalctl -u qadam-ai -n 20 --no-pager

# 4. Test health endpoint
echo "=== Health Check ==="
curl http://localhost:8001/api/health
```

---

**Run these commands on the VM and share the output so I can help you fix it!**
