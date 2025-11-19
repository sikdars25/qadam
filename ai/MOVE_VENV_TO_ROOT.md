# Move Virtual Environment to Root Folder

## Current Structure
```
/opt/qadam-ai/
├── ai/
│   ├── venv/          # Current location
│   ├── app.py
│   ├── requirements.txt
│   └── ...
```

## Target Structure
```
/opt/qadam-ai/
├── venv/              # New location (root)
├── ai/
│   ├── app.py
│   ├── requirements.txt
│   └── ...
```

---

## Option 1: Create New Virtual Environment (Recommended)

This is the cleanest approach as virtual environments are not meant to be moved.

### Step 1: Navigate to Root Directory
```bash
cd /opt/qadam-ai
```

### Step 2: Create New Virtual Environment at Root
```bash
python3 -m venv venv
```

### Step 3: Activate New Virtual Environment
```bash
source venv/bin/activate
```

### Step 4: Install Dependencies from AI Project
```bash
pip install -r ai/requirements.txt
```

### Step 5: Verify Installation
```bash
pip list
python -c "import requests; print('requests:', requests.__version__)"
python -c "from dotenv import load_dotenv; print('python-dotenv: OK')"
```

### Step 6: Update Systemd Service File
```bash
sudo nano /etc/systemd/system/qadam-ai.service
```

**Change:**
```ini
[Service]
WorkingDirectory=/opt/qadam-ai/ai
ExecStart=/opt/qadam-ai/ai/venv/bin/python app.py
```

**To:**
```ini
[Service]
WorkingDirectory=/opt/qadam-ai/ai
ExecStart=/opt/qadam-ai/venv/bin/python app.py
```

### Step 7: Reload Systemd and Restart Service
```bash
sudo systemctl daemon-reload
sudo systemctl restart qadam-ai
```

### Step 8: Verify Service is Running
```bash
sudo systemctl status qadam-ai
```

### Step 9: Remove Old Virtual Environment
```bash
rm -rf /opt/qadam-ai/ai/venv
```

---

## Option 2: Move Existing Virtual Environment (Not Recommended)

Virtual environments contain hardcoded paths, so moving them requires fixing these paths.

### Step 1: Move the Directory
```bash
cd /opt/qadam-ai
mv ai/venv ./venv
```

### Step 2: Fix Activation Scripts
```bash
# Fix activate script
sed -i 's|/opt/qadam-ai/ai/venv|/opt/qadam-ai/venv|g' venv/bin/activate
sed -i 's|/opt/qadam-ai/ai/venv|/opt/qadam-ai/venv|g' venv/bin/activate.csh
sed -i 's|/opt/qadam-ai/ai/venv|/opt/qadam-ai/venv|g' venv/bin/activate.fish
```

### Step 3: Fix Python Shebang in Scripts
```bash
# Fix all Python scripts in venv/bin
find venv/bin -type f -exec sed -i 's|/opt/qadam-ai/ai/venv|/opt/qadam-ai/venv|g' {} +
```

### Step 4: Recreate pyvenv.cfg
```bash
cat > venv/pyvenv.cfg << EOF
home = $(which python3 | xargs dirname | xargs dirname)
include-system-site-packages = false
version = $(python3 --version | cut -d' ' -f2)
EOF
```

### Step 5: Update Systemd Service (same as Option 1 Step 6-8)

---

## Option 3: Use Relative Paths (Alternative)

Keep venv in ai folder but use relative paths in systemd service.

### Update Systemd Service
```bash
sudo nano /etc/systemd/system/qadam-ai.service
```

**Change to:**
```ini
[Service]
WorkingDirectory=/opt/qadam-ai/ai
ExecStart=/opt/qadam-ai/ai/venv/bin/python app.py
Environment="PATH=/opt/qadam-ai/ai/venv/bin:$PATH"
```

---

## Complete Step-by-Step (Recommended Approach)

### 1. Backup Current Setup
```bash
cd /opt/qadam-ai
# Note current packages
ai/venv/bin/pip freeze > ai/current_packages.txt
```

### 2. Stop the Service
```bash
sudo systemctl stop qadam-ai
```

### 3. Create New Virtual Environment at Root
```bash
cd /opt/qadam-ai
python3 -m venv venv
```

### 4. Activate and Install Dependencies
```bash
source venv/bin/activate
pip install --upgrade pip
pip install -r ai/requirements.txt

# Verify critical packages
pip show requests python-dotenv flask flask-cors groq
```

### 5. Update Systemd Service File
```bash
sudo nano /etc/systemd/system/qadam-ai.service
```

**Complete service file should look like:**
```ini
[Unit]
Description=Qadam AI Service
After=network.target

[Service]
Type=simple
User=qadamuser
WorkingDirectory=/opt/qadam-ai/ai
ExecStart=/opt/qadam-ai/venv/bin/python app.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=qadam-ai

# Environment variables (if not using .env file)
# Environment="GROQ_API_KEY=your_key"
# Environment="WOLFRAM_APP_ID=your_id"

[Install]
WantedBy=multi-user.target
```

### 6. Reload and Restart
```bash
sudo systemctl daemon-reload
sudo systemctl start qadam-ai
sudo systemctl status qadam-ai
```

### 7. Verify Logs
```bash
sudo journalctl -u qadam-ai -f
```

**Expected output:**
```
✅ Intelligent Question Solver loaded successfully
✅ Groq API: Available
 * Running on http://127.0.0.1:8001
```

### 8. Test the Service
```bash
curl http://localhost:8001/api/health
```

### 9. Remove Old Virtual Environment
```bash
# Only after confirming everything works!
rm -rf /opt/qadam-ai/ai/venv
```

---

## Troubleshooting

### Issue: Service fails to start after moving venv

**Check:**
```bash
# Verify Python path
/opt/qadam-ai/venv/bin/python --version

# Verify packages are installed
/opt/qadam-ai/venv/bin/pip list

# Check service file syntax
sudo systemctl cat qadam-ai

# Check for errors
sudo journalctl -u qadam-ai -n 50 --no-pager
```

### Issue: Module not found errors

**Solution:**
```bash
source /opt/qadam-ai/venv/bin/activate
pip install -r /opt/qadam-ai/ai/requirements.txt
sudo systemctl restart qadam-ai
```

### Issue: Permission denied

**Solution:**
```bash
# Fix ownership
sudo chown -R qadamuser:qadamuser /opt/qadam-ai/venv

# Fix permissions
chmod -R 755 /opt/qadam-ai/venv
```

### Issue: Old venv still being used

**Solution:**
```bash
# Verify systemd service file
sudo systemctl cat qadam-ai | grep ExecStart

# Should show: ExecStart=/opt/qadam-ai/venv/bin/python app.py
# NOT: ExecStart=/opt/qadam-ai/ai/venv/bin/python app.py

# If wrong, edit and reload
sudo nano /etc/systemd/system/qadam-ai.service
sudo systemctl daemon-reload
sudo systemctl restart qadam-ai
```

---

## Verification Checklist

- [ ] New venv created at `/opt/qadam-ai/venv`
- [ ] All packages installed: `pip list`
- [ ] Systemd service file updated
- [ ] Systemd daemon reloaded
- [ ] Service started successfully
- [ ] Service status shows "active (running)"
- [ ] Logs show no errors
- [ ] Health endpoint responds
- [ ] Question solving works
- [ ] Old venv removed

---

## Quick Commands Summary

```bash
# Complete migration in one go:
cd /opt/qadam-ai && \
sudo systemctl stop qadam-ai && \
python3 -m venv venv && \
source venv/bin/activate && \
pip install --upgrade pip && \
pip install -r ai/requirements.txt && \
deactivate && \
sudo sed -i 's|/opt/qadam-ai/ai/venv|/opt/qadam-ai/venv|g' /etc/systemd/system/qadam-ai.service && \
sudo systemctl daemon-reload && \
sudo systemctl start qadam-ai && \
sudo systemctl status qadam-ai
```

**Then verify and cleanup:**
```bash
# Monitor logs
sudo journalctl -u qadam-ai -f

# After confirming it works, remove old venv
rm -rf /opt/qadam-ai/ai/venv
```

---

## Benefits of Root-Level Virtual Environment

1. **Shared Dependencies**: Multiple projects in qadam-ai can share the same venv
2. **Cleaner Structure**: Separates code from environment
3. **Easier Management**: Single venv to maintain
4. **Standard Practice**: Common pattern in production deployments

---

## Rollback Procedure

If something goes wrong:

```bash
# Stop service
sudo systemctl stop qadam-ai

# Restore old service file
sudo nano /etc/systemd/system/qadam-ai.service
# Change ExecStart back to: /opt/qadam-ai/ai/venv/bin/python app.py

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl start qadam-ai

# If old venv was deleted, recreate it
cd /opt/qadam-ai/ai
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Summary

**Recommended: Create new venv at root (Option 1)**
- Cleanest approach
- No path fixing needed
- Takes ~2-3 minutes
- Most reliable

**Not Recommended: Move existing venv (Option 2)**
- Requires fixing hardcoded paths
- Error-prone
- May have hidden issues

**Best Practice:**
Always create a fresh virtual environment when changing locations rather than moving an existing one.
