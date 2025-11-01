# Deploy AI Service to VM - IMMEDIATE ACTION REQUIRED

## 🚨 Current Issue

Backend is trying to call AI service at `http://130.107.48.221` but it's **NOT RUNNING**.

**Error:** "Error solving question: mt" (timeout error)

## ✅ Solution: Deploy AI Service to VM

### Step 1: SSH to VM

```bash
ssh qadamuser@130.107.48.221
```

### Step 2: Install Dependencies (First Time Only)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-venv python3-pip nginx git build-essential python3-dev

# Create application directory
sudo mkdir -p /opt/qadam-ai
sudo chown qadamuser:qadamuser /opt/qadam-ai
```

### Step 3: Clone Repository

```bash
cd /opt/qadam-ai
git init
git remote add origin https://github.com/sikdars25/qadam.git
git fetch origin backend-ai
git checkout backend-ai
```

### Step 4: Set Groq API Key

```bash
# Edit the systemd service file
nano ai/qadam-ai.service
```

Find this line:
```
Environment="GROQ_API_KEY=your_groq_api_key_here"
```

Replace `your_groq_api_key_here` with your actual Groq API key.

Save and exit (Ctrl+X, Y, Enter).

### Step 5: Deploy

```bash
# Make deploy script executable
chmod +x ai/deploy.sh

# Run deployment
./ai/deploy.sh
```

The script will:
- ✅ Pull latest code
- ✅ Create Python virtual environment
- ✅ Install dependencies (Flask, Groq, etc.)
- ✅ Configure systemd service
- ✅ Configure Nginx
- ✅ Start the service

### Step 6: Verify Service is Running

```bash
# Check service status
sudo systemctl status qadam-ai

# Check if it's listening on port 8001
sudo netstat -tlnp | grep 8001

# Test health endpoint
curl http://localhost:8001/api/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "AI Service",
  "groq_api": true
}
```

### Step 7: Test from Outside VM

From your local machine:

```bash
curl http://130.107.48.221/api/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "AI Service",
  "groq_api": true
}
```

### Step 8: Test Question Solving

```bash
curl -X POST http://130.107.48.221/api/solve-question \
  -H "Content-Type: application/json" \
  -d '{"question_text": "What is 2+2?", "subject": "Math"}'
```

**Expected Response:**
```json
{
  "success": true,
  "solution": "..."
}
```

## 🔧 Troubleshooting

### If Service Won't Start

```bash
# Check logs
sudo journalctl -u qadam-ai -n 50

# Common issues:
# 1. Python not found - use python3 in ExecStart
# 2. GROQ_API_KEY not set - edit qadam-ai.service
# 3. Port 8001 in use - kill other process or change port
```

### If Nginx Not Working

```bash
# Check Nginx status
sudo systemctl status nginx

# Check Nginx error log
sudo tail -f /var/log/nginx/error.log

# Test Nginx config
sudo nginx -t
```

### If Still Getting Errors

```bash
# Restart everything
sudo systemctl restart qadam-ai
sudo systemctl restart nginx

# Check if port 80 is open
sudo ufw status
sudo ufw allow 80/tcp
```

## 📊 After Deployment

Once the AI service is running:

1. ✅ Backend will connect successfully
2. ✅ Questions will be solved
3. ✅ No more timeout errors
4. ✅ Frontend will work properly

## 🎯 Quick Verification Checklist

- [ ] SSH to VM successful
- [ ] Dependencies installed
- [ ] Code cloned from backend-ai branch
- [ ] GROQ_API_KEY set in qadam-ai.service
- [ ] deploy.sh executed successfully
- [ ] Service status shows "active (running)"
- [ ] curl localhost:8001/api/health returns 200
- [ ] curl 130.107.48.221/api/health returns 200
- [ ] Question solving test works

---

**ACTION REQUIRED:** SSH to 130.107.48.221 and run the deployment steps above!
