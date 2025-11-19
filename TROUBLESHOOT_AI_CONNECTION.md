# Troubleshooting AI Service Connection Error

## Error Details

**Error from Proxy Service:**
```
requests.exceptions.ConnectionError: HTTPConnectionPool(host='172.17.0.4', port=8001)
Exception: Cannot connect to AI service - please check if service is running
```

**What's happening:**
- Proxy service (on `gadam-backend-proxy`) is trying to connect to AI service
- AI service should be at `http://172.17.0.4:8001`
- Connection is being refused or timing out

---

## Diagnostic Steps

### Step 1: Check if AI Service is Running

**On AI VM:**
```bash
sudo systemctl status qadam-ai
```

**Expected:** `Active: active (running)`

**If not running:**
```bash
# Check why it failed
sudo journalctl -u qadam-ai -n 50 --no-pager

# Start the service
sudo systemctl start qadam-ai

# Monitor startup
sudo journalctl -u qadam-ai -f
```

---

### Step 2: Check AI Service Port

**On AI VM:**
```bash
# Check if port 8001 is listening
sudo netstat -tlnp | grep 8001
# OR
sudo ss -tlnp | grep 8001
# OR
sudo lsof -i :8001
```

**Expected output:**
```
tcp   0   0 0.0.0.0:8001   0.0.0.0:*   LISTEN   12345/python
```

**If port not listening:**
- Service is not running
- Service failed to start
- Wrong port configuration

---

### Step 3: Check AI Service IP Address

**On AI VM:**
```bash
# Check all network interfaces
ip addr show

# Check Docker network (if using Docker)
docker network inspect bridge
```

**Expected:**
- AI service should be listening on `0.0.0.0:8001` (all interfaces)
- Or specifically on `172.17.0.4:8001`

---

### Step 4: Test AI Service Locally

**On AI VM:**
```bash
# Test health endpoint locally
curl http://localhost:8001/api/health

# Test from 172.17.0.4
curl http://172.17.0.4:8001/api/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "service": "AI Service",
  "version": "1.0"
}
```

---

### Step 5: Test Connection from Proxy VM

**On Proxy VM:**
```bash
# Test if AI service is reachable
curl http://172.17.0.4:8001/api/health

# Test with verbose output
curl -v http://172.17.0.4:8001/api/health

# Test network connectivity
ping 172.17.0.4

# Test port connectivity
telnet 172.17.0.4 8001
# OR
nc -zv 172.17.0.4 8001
```

---

### Step 6: Check Firewall Rules

**On AI VM:**
```bash
# Check if firewall is blocking port 8001
sudo ufw status

# If firewall is active, allow port 8001
sudo ufw allow 8001/tcp

# Check iptables
sudo iptables -L -n | grep 8001
```

---

### Step 7: Check Network Security Groups (Azure)

**In Azure Portal:**
1. Go to AI VM → Networking
2. Check Inbound port rules
3. Ensure port 8001 is allowed from Proxy VM's IP or subnet

**Required rule:**
- **Source:** Proxy VM IP or VNet
- **Destination port:** 8001
- **Protocol:** TCP
- **Action:** Allow

---

## Common Issues & Solutions

### Issue 1: AI Service Not Running

**Symptoms:**
```
sudo systemctl status qadam-ai
● qadam-ai.service - Qadam AI Service
   Loaded: loaded
   Active: failed
```

**Solutions:**
```bash
# Check logs for error
sudo journalctl -u qadam-ai -n 100 --no-pager

# Common causes:
# 1. Missing dependencies
pip3 install -r /opt/qadam-ai/ai/requirements.txt

# 2. Missing environment variables
cat /opt/qadam-ai/ai/.env

# 3. Port already in use
sudo lsof -i :8001
# Kill the process using the port
sudo kill -9 <PID>

# Restart service
sudo systemctl restart qadam-ai
```

---

### Issue 2: Wrong IP Address

**Symptoms:**
- Service running but not accessible from proxy
- Works on localhost but not on 172.17.0.4

**Check Flask app binding:**
```python
# In app.py, should be:
app.run(host='0.0.0.0', port=8001)  # Listen on all interfaces

# NOT:
app.run(host='127.0.0.1', port=8001)  # Only localhost
```

**Fix in app.py:**
```bash
cd /opt/qadam-ai/ai
nano app.py
```

Find the line with `app.run()` and ensure it's:
```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=False)
```

**Restart service:**
```bash
sudo systemctl restart qadam-ai
```

---

### Issue 3: Firewall Blocking

**Symptoms:**
- Service running on AI VM
- Port listening on 0.0.0.0:8001
- Cannot connect from proxy VM

**Solution:**
```bash
# On AI VM - Allow port 8001
sudo ufw allow 8001/tcp
sudo ufw reload
sudo ufw status

# Verify rule added
sudo ufw status numbered
```

---

### Issue 4: Network Routing Issue

**Symptoms:**
- Cannot ping AI VM from proxy VM
- Network connectivity issue

**Check routing:**
```bash
# On Proxy VM
traceroute 172.17.0.4
ping 172.17.0.4

# Check if VMs are in same VNet/subnet
ip route show
```

**Solution:**
- Ensure both VMs are in same Azure VNet or have peering configured
- Check Azure Network Security Groups
- Check subnet routing tables

---

### Issue 5: Service Crashed After Deployment

**Symptoms:**
```
ModuleNotFoundError: No module named 'requests'
```

**Solution:**
```bash
cd /opt/qadam-ai/ai
source venv/bin/activate  # If using venv
pip3 install -r requirements.txt
sudo systemctl restart qadam-ai
```

---

## Quick Fix Commands

### On AI VM:

```bash
# Complete diagnostic and fix
cd /opt/qadam-ai/ai && \
pip3 install -r requirements.txt && \
sudo systemctl restart qadam-ai && \
sleep 3 && \
sudo systemctl status qadam-ai && \
curl http://localhost:8001/api/health && \
sudo netstat -tlnp | grep 8001
```

---

## Verification After Fix

### 1. Check Service Status
```bash
sudo systemctl status qadam-ai
```
**Expected:** `Active: active (running)`

### 2. Check Port Listening
```bash
sudo netstat -tlnp | grep 8001
```
**Expected:** `0.0.0.0:8001` or `172.17.0.4:8001`

### 3. Test Local Health Endpoint
```bash
curl http://localhost:8001/api/health
```
**Expected:** `{"status": "healthy", ...}`

### 4. Test from External IP
```bash
curl http://172.17.0.4:8001/api/health
```
**Expected:** `{"status": "healthy", ...}`

### 5. Test from Proxy VM
**On Proxy VM:**
```bash
curl http://172.17.0.4:8001/api/health
```
**Expected:** `{"status": "healthy", ...}`

### 6. Test Question Solving
**On Proxy VM:**
```bash
curl -X POST http://172.17.0.4:8001/api/solve-question \
  -H "Content-Type: application/json" \
  -d '{"question_text": "Test question", "subject": "Math"}'
```
**Expected:** JSON response with solution

---

## Configuration Check

### AI Service Configuration

**Check app.py:**
```bash
cd /opt/qadam-ai/ai
grep -n "app.run" app.py
```

**Should show:**
```python
app.run(host='0.0.0.0', port=8001, debug=False)
```

**Check systemd service:**
```bash
sudo systemctl cat qadam-ai
```

**Should show:**
```ini
[Service]
WorkingDirectory=/opt/qadam-ai/ai
ExecStart=/opt/qadam-ai/venv/bin/python app.py
# OR
ExecStart=/opt/qadam-ai/ai/venv/bin/python app.py
```

---

## Proxy Service Configuration

**Check AI service URL in proxy:**
```bash
cd /opt/qadam-backend/proxy
grep -r "172.17.0.4" .
grep -r "AI_SERVICE_URL" .
```

**Check .env file:**
```bash
cat .env | grep AI_SERVICE_URL
```

**Should be:**
```
AI_SERVICE_URL=http://172.17.0.4:8001
```

---

## Network Topology Check

### Expected Setup:

```
┌─────────────────────┐         ┌─────────────────────┐
│   Proxy VM          │         │   AI VM             │
│   gadam-backend     │         │   qadam-ai-vm       │
│                     │         │                     │
│   Port: 5000        │────────▶│   Port: 8001        │
│   (Gunicorn)        │  HTTP   │   (Flask)           │
│                     │         │                     │
│   IP: 172.17.0.x    │         │   IP: 172.17.0.4    │
└─────────────────────┘         └─────────────────────┘
```

**Verify:**
1. Both VMs in same VNet or peered VNets
2. Network Security Groups allow traffic
3. No firewall blocking port 8001
4. AI service listening on 0.0.0.0:8001

---

## Monitoring Commands

### Continuous Monitoring

**On AI VM:**
```bash
# Monitor service logs
sudo journalctl -u qadam-ai -f

# Monitor port connections
watch -n 1 'sudo netstat -an | grep 8001'

# Monitor service status
watch -n 5 'sudo systemctl status qadam-ai'
```

**On Proxy VM:**
```bash
# Monitor proxy logs
sudo journalctl -u qadam-backend-proxy -f | grep "AI service"

# Test connection repeatedly
watch -n 5 'curl -s http://172.17.0.4:8001/api/health'
```

---

## Summary Checklist

- [ ] AI service is running: `sudo systemctl status qadam-ai`
- [ ] Port 8001 is listening: `sudo netstat -tlnp | grep 8001`
- [ ] Service binds to 0.0.0.0: Check app.py
- [ ] Health endpoint works locally: `curl localhost:8001/api/health`
- [ ] Health endpoint works on 172.17.0.4: `curl 172.17.0.4:8001/api/health`
- [ ] Firewall allows port 8001: `sudo ufw status`
- [ ] Azure NSG allows port 8001: Check Azure Portal
- [ ] Proxy can reach AI VM: `ping 172.17.0.4` from proxy
- [ ] Proxy can connect to port: `curl 172.17.0.4:8001/api/health` from proxy
- [ ] Dependencies installed: `pip3 list | grep requests`
- [ ] Environment variables set: Check .env file
- [ ] No errors in logs: `sudo journalctl -u qadam-ai -n 50`

---

## Emergency Restart Procedure

```bash
# On AI VM - Complete restart
cd /opt/qadam-ai/ai && \
sudo systemctl stop qadam-ai && \
sleep 2 && \
pip3 install -r requirements.txt && \
sudo systemctl start qadam-ai && \
sleep 3 && \
sudo systemctl status qadam-ai && \
curl http://localhost:8001/api/health && \
curl http://172.17.0.4:8001/api/health
```

If this works, test from proxy VM:
```bash
# On Proxy VM
curl http://172.17.0.4:8001/api/health
```
