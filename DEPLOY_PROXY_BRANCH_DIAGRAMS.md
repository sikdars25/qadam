# 🚀 Deploy Proxy Branch Diagram Service - Correct Branch Guide

## ✅ Branch Architecture Fixed

**Issue Resolved**: Backend-proxy changes are now properly in the `backend-proxy` branch, not `main` branch.

### 📁 Branch Structure

- **`main` branch**: Frontend code + calls proxy service
- **`backend-proxy` branch**: Backend diagram analysis service
- **`backend-ai` branch**: AI question solver service

## 🔧 Deployment Steps for Proxy Branch

### **Step 1: SSH to AI VM**

```bash
ssh qadamuser@130.107.48.166
```

### **Step 2: Navigate to Proxy Directory**

```bash
cd /opt/qadam-backend/proxy
```

### **Step 3: Switch to Proxy Branch**

```bash
# Checkout the correct branch
cd /opt/qadam-backend
git checkout backend-proxy
git pull origin backend-proxy

# Verify new files exist
ls -la proxy/comprehensive_diagram_generator.py
ls -la proxy/diagram_endpoint.py
```

### **Step 4: Install Dependencies**

```bash
# Install Flask and CORS if needed
pip3 install flask flask-cors

# Or if using system packages
sudo apt update
sudo apt install python3-flask python3-flask-cors
```

### **Step 5: Test the Comprehensive Diagram Generator**

```bash
cd /opt/qadam-backend/proxy

# Test the comprehensive diagram generator
python3 comprehensive_diagram_generator.py

# Should output sample unified diagram JSON
```

### **Step 6: Start the Enhanced Diagram Service**

```bash
# Start the enhanced diagram service (includes comprehensive analysis)
python3 diagram_endpoint.py

# Or run in background:
nohup python3 diagram_endpoint.py > diagram_endpoint.log 2>&1 &

# Check if it's running
ps aux | grep diagram_endpoint
```

### **Step 7: Verify Service Endpoints**

```bash
# Test health endpoint
curl http://localhost:5001/health

# Test comprehensive diagram analysis
curl -X POST http://localhost:5001/analyze-diagrams \
  -H "Content-Type: application/json" \
  -d '{
    "solution_text": "[DIAGRAM: Line segment BC with a length of 6 cm marked on it] [DIAGRAM: Perpendicular bisector of line segment BC]",
    "question_text": "Construct perpendicular bisector of BC",
    "subject": "Mathematics"
  }'

# Test enhanced test endpoint
curl http://localhost:5001/test-diagram
```

## 🎯 Service Architecture

### **Proxy Branch Service (Port 5001)**

**Enhanced Endpoints:**
- **POST /analyze-diagrams** - New comprehensive analysis
- **GET /test-diagram** - Enhanced with comprehensive testing
- **POST /generate-diagrams** - Legacy endpoint (unchanged)
- **GET /health** - Health check

**New Features:**
- Comprehensive diagram analysis from solution text
- Unified SVG generation for construction sequences
- Pattern matching for geometric elements
- Connected step-by-step visualizations

### **Frontend Integration (Main Branch)**

**Service Calls:**
- Main: `http://130.107.48.166:5001/analyze-diagrams`
- Fallback: `http://130.107.48.166:5001/test-diagram`
- Service info shows "(Proxy Branch)" indicator

## 🧪 Complete Testing Flow

### **1. Test Backend Service**

```bash
# From VM
curl -X POST http://localhost:5001/analyze-diagrams \
  -H "Content-Type: application/json" \
  -d '{
    "solution_text": "Step 1: Draw base. [DIAGRAM: Line segment BC with a length of 6 cm marked on it] Step 2: Add bisector. [DIAGRAM: Perpendicular bisector of line segment BC]",
    "question_text": "Construct perpendicular bisector of BC",
    "subject": "Mathematics"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "diagram": {
    "type": "construction_sequence",
    "svg": "<svg>...</svg>",
    "description": "Construction sequence for: Construct perpendicular bisector...",
    "elements_count": 2,
    "steps": [
      "Line segment BC with length 6cm",
      "Perpendicular bisector of line segment BC"
    ]
  },
  "metadata": {
    "has_diagrams": true,
    "elements_found": 2
  }
}
```

### **2. Test from External Machine**

```bash
# Replace localhost with VM IP
curl -X POST http://130.107.48.166:5001/analyze-diagrams \
  -H "Content-Type: application/json" \
  -d '{
    "solution_text": "[DIAGRAM: Line segment BC with a length of 6 cm marked on it]",
    "question_text": "Construct perpendicular bisector",
    "subject": "Mathematics"
  }'
```

### **3. Test from Frontend**

1. Open: `https://zealous-ocean-06e22b51e.3.azurestaticapps.net`
2. Login → "🎯 Clean Solve Question"
3. Select "📊 Solution with Diagram"
4. Enter: "Construct the perpendicular bisector of line segment BC with length 6cm"
5. Submit

**Expected Result:**
- Right column: "Backend-Generated Unified Diagram"
- Single unified SVG with construction sequence
- Connected steps with flow arrows
- Step descriptions listed below

## 🔄 Service Management

### **Start/Stop Commands**

```bash
cd /opt/qadam-backend/proxy

# Start service
python3 diagram_endpoint.py &

# Stop service
pkill -f diagram_endpoint.py

# Check status
ps aux | grep diagram_endpoint.py
```

### **Log Monitoring**

```bash
# View logs
tail -f diagram_endpoint.log

# Or if running manually, watch console output
```

### **Systemd Service (Optional)**

Create systemd service:
```bash
sudo nano /etc/systemd/system/qadam-diagram.service
```

Content:
```ini
[Unit]
Description=Qadam Enhanced Diagram Service
After=network.target

[Service]
Type=simple
User=qadamuser
WorkingDirectory=/opt/qadam-backend/proxy
ExecStart=/usr/bin/python3 diagram_endpoint.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl daemon-reload
sudo systemctl enable qadam-diagram
sudo systemctl start qadam-diagram
sudo systemctl status qadam-diagram
```

## 🛠️ Troubleshooting

### **Issue 1: Wrong Branch**

```bash
# Verify you're on the correct branch
cd /opt/qadam-backend
git branch
# Should show: * backend-proxy

# If not, switch branches
git checkout backend-proxy
git pull origin backend-proxy
```

### **Issue 2: Missing Comprehensive Generator**

```bash
# Check if file exists
ls -la /opt/qadam-backend/proxy/comprehensive_diagram_generator.py

# If missing, pull latest code
cd /opt/qadam-backend
git pull origin backend-proxy
```

### **Issue 3: Import Error**

```bash
# Test import
cd /opt/qadam-backend/proxy
python3 -c "from comprehensive_diagram_generator import analyze_and_generate_diagram; print('Import OK')"

# If fails, check file permissions and Python path
ls -la comprehensive_diagram_generator.py
python3 -c "import sys; print(sys.path)"
```

### **Issue 4: Port Conflict**

```bash
# Check what's using port 5001
sudo netstat -tulpn | grep :5001

# Kill existing process
sudo kill -9 <PID>

# Restart service
python3 diagram_endpoint.py &
```

## 📋 Verification Checklist

After deployment, verify:

- [ ] **Correct branch**: `git branch` shows `* backend-proxy`
- [ ] **Files present**: `comprehensive_diagram_generator.py` and `diagram_endpoint.py`
- [ ] **Service running**: `curl http://localhost:5001/health` returns success
- [ ] **New endpoint works**: `/analyze-diagrams` returns unified diagram
- [ ] **Frontend connects**: No service errors in browser console
- [ ] **Unified diagrams**: Single SVG with connected steps
- [ ] **Step descriptions**: Construction steps listed below diagram

## 🎉 Success Indicators

✅ **Branch correct**: Changes in `backend-proxy`, not `main`  
✅ **Service enhanced**: Comprehensive analysis available at `/analyze-diagrams`  
✅ **Frontend integrated**: Calls proxy service correctly  
✅ **Unified diagrams**: Single SVG showing construction sequence  
✅ **Connected flow**: Steps linked with arrows and progression  
✅ **Professional output**: Clean mathematical visualizations  

## 🚀 Summary

**Branch Architecture Fixed:**
- **Backend changes** → `backend-proxy` branch ✅
- **Frontend changes** → `main` branch ✅
- **Proper separation** → No cross-branch conflicts ✅

**Service Deployment:**
1. **Deploy proxy branch** to VM (`/opt/qadam-backend`)
2. **Start enhanced diagram service** (`python3 diagram_endpoint.py`)
3. **Frontend automatically calls** comprehensive analysis
4. **Unified diagrams generated** from solution text

**The diagram analysis service is now properly organized in the correct branch with full backend processing!** 🎉
