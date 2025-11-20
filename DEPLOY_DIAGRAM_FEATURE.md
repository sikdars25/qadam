# 🚀 Deploy Diagram Feature - Quick Guide

## Issue

The diagram feature code is implemented but **NOT YET DEPLOYED** to the AI VM.

**Current Status:**
- ✅ Code committed to `backend-ai` branch
- ✅ Frontend deployed to Azure Static Web Apps
- ❌ Backend-AI NOT deployed to VM yet

---

## 🔧 Deployment Steps

### **Step 1: SSH to VM**

```bash
ssh azureuser@130.107.48.166
```

---

### **Step 2: Navigate to AI Directory**

```bash
cd /home/azureuser/ai/
```

---

### **Step 3: Check Current Branch and Status**

```bash
# Check current branch
git branch

# Check for local changes
git status

# If there are local changes to requirements.txt or other files:
git stash
# OR
git add .
git commit -m "Save local changes before diagram feature deployment"
```

---

### **Step 4: Pull Latest Backend-AI Code**

```bash
# Fetch latest changes
git fetch origin backend-ai

# Checkout backend-ai branch
git checkout backend-ai

# Pull latest code (includes diagram_generator.py)
git pull origin backend-ai
```

---

### **Step 5: Verify New Files**

```bash
# Check if diagram_generator.py exists
ls -la diagram_generator.py

# Should show:
# -rw-r--r-- 1 azureuser azureuser 15000+ Nov 21 diagram_generator.py

# Verify recent commits
git log -3 --oneline

# Should show:
# cd1399c feat: Add diagram generation for with-diagram solution type
```

---

### **Step 6: Restart AI Service**

```bash
# Restart the AI service
sudo systemctl restart qadam-ai

# Check status
sudo systemctl status qadam-ai

# Should show: "active (running)"
```

---

### **Step 7: Verify Deployment**

```bash
# Check logs for any errors
sudo journalctl -u qadam-ai -n 50

# Test the endpoint
curl -X POST http://localhost:5001/api/solve-question \
  -H "Content-Type: application/json" \
  -d '{
    "question_text": "In a right-angled triangle, the hypotenuse is 10 units and the opposite side is 6 units. Find sin(θ).",
    "subject": "Mathematics",
    "solution_type": "with-diagram"
  }' | jq .
```

---

### **Expected Response:**

```json
{
  "success": true,
  "solution": "## Understanding...\n\n{{DIAGRAM_0}}\n\n## Solution...",
  "diagrams": [
    {
      "type": "geometry",
      "subtype": "right_triangle",
      "ascii": "...",
      "description": "Right Triangle",
      "labels": ["hypotenuse=10", "opposite=6"]
    }
  ],
  "has_diagrams": true,
  "diagram_count": 1,
  "solver_type": "intelligent_with_diagrams"
}
```

---

## 🧪 Test from Frontend

After deployment:

1. Open: `https://zealous-ocean-06e22b51e.3.azurestaticapps.net`
2. Select **"📊 With Diagram"** from dropdown
3. Enter the question:
   ```
   In a right-angled triangle, the length of the hypotenuse is 10 units, 
   and the length of the side opposite to angle θ is 6 units. 
   Find the value of sin(θ) and the measure of angle θ.
   ```
4. Submit

**Expected:**
- Solution with embedded diagram
- ASCII art right triangle showing hypotenuse=10, opposite=6
- Labels and calculations
- Final answer with sin(θ) = 0.6 and θ ≈ 36.9°

---

## 🔍 Troubleshooting

### **Issue 1: Git Conflicts**

If you see:
```
error: Your local changes to the following files would be overwritten by merge:
	ai/requirements.txt
```

**Fix:**
```bash
# Option A: Stash changes
git stash
git pull origin backend-ai
git stash pop

# Option B: Commit changes
git add .
git commit -m "Local changes"
git pull origin backend-ai
```

---

### **Issue 2: Module Not Found**

If logs show:
```
ModuleNotFoundError: No module named 'diagram_generator'
```

**Fix:**
```bash
# Verify file exists
ls -la /home/azureuser/ai/diagram_generator.py

# Check Python path
python3 -c "import sys; print(sys.path)"

# Restart service
sudo systemctl restart qadam-ai
```

---

### **Issue 3: No Diagrams in Response**

If `has_diagrams: false` or `diagrams: []`:

**Check:**
```bash
# View AI service logs
sudo journalctl -u qadam-ai -f

# Look for:
# "🤖 Using Intelligent Question Solver with Groq + Wolfram Alpha (solution_type: with-diagram)"
# "Diagram types identified: ['geometry']"
```

**Verify:**
- Solution type is being passed correctly
- Diagram generator is being imported
- No errors in diagram generation

---

### **Issue 4: Service Won't Start**

```bash
# Check detailed status
sudo systemctl status qadam-ai -l

# Check logs for errors
sudo journalctl -u qadam-ai -n 100

# Common issues:
# - Syntax errors in Python files
# - Missing dependencies
# - Port conflicts
```

---

## 📝 Quick Deployment Script

Save this as `deploy_diagrams.sh` on the VM:

```bash
#!/bin/bash

echo "🚀 Deploying Diagram Feature..."

cd /home/azureuser/ai/

echo "📦 Stashing local changes..."
git stash

echo "🔄 Fetching latest code..."
git fetch origin backend-ai
git checkout backend-ai
git pull origin backend-ai

echo "✅ Verifying diagram_generator.py..."
if [ -f "diagram_generator.py" ]; then
    echo "✓ diagram_generator.py found"
else
    echo "✗ diagram_generator.py NOT found - deployment may have failed"
    exit 1
fi

echo "🔄 Restarting AI service..."
sudo systemctl restart qadam-ai

echo "⏳ Waiting for service to start..."
sleep 3

echo "📊 Checking service status..."
sudo systemctl status qadam-ai --no-pager

echo "🧪 Testing diagram endpoint..."
curl -X POST http://localhost:5001/api/solve-question \
  -H "Content-Type: application/json" \
  -d '{
    "question_text": "Find the area of a right triangle with sides 3 and 4",
    "subject": "Mathematics",
    "solution_type": "with-diagram"
  }' | jq '.has_diagrams, .diagram_count'

echo "✅ Deployment complete!"
echo "Test from frontend: https://zealous-ocean-06e22b51e.3.azurestaticapps.net"
```

**Run:**
```bash
chmod +x deploy_diagrams.sh
./deploy_diagrams.sh
```

---

## 🎯 Summary

**To fix the "no diagram showing" issue:**

1. SSH to VM: `ssh azureuser@130.107.48.166`
2. Navigate: `cd /home/azureuser/ai/`
3. Pull code: `git pull origin backend-ai`
4. Restart: `sudo systemctl restart qadam-ai`
5. Test from frontend

**The diagram feature is ready in the code, it just needs to be deployed to the VM!**

---

## 📞 Verification Checklist

After deployment, verify:

- [ ] `diagram_generator.py` exists in `/home/azureuser/ai/`
- [ ] AI service is running (`sudo systemctl status qadam-ai`)
- [ ] No errors in logs (`sudo journalctl -u qadam-ai -n 50`)
- [ ] Test endpoint returns `has_diagrams: true`
- [ ] Frontend shows diagrams when "With Diagram" is selected

---

**Once deployed, your triangle question will show a beautiful ASCII art diagram!** 📐✨
