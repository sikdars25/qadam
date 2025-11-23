# 🐛 Debug: Solution Type Always Step-by-Step

## Issue

Backend-ai code is deployed, but the system is always choosing step-by-step path even when high-level is selected.

---

## 🔍 Root Cause Analysis

Since backend-ai is deployed and the issue persists, the problem is likely one of:

1. **Proxy not forwarding `solution_type`** parameter
2. **Backend receiving `null` or wrong value** for solution_type
3. **Default value being used** because parameter is missing

---

## 🧪 Diagnostic Steps

### **Step 1: Check What Frontend Sends**

Open browser DevTools → Network tab → Submit with "High-Level" selected

**Check Request Payload:**
```json
{
  "question_text": "What is 2+2?",
  "subject": "Mathematics",
  "solution_type": "high-level"  // ✅ Should be "high-level"
}
```

**If NOT present:** Frontend issue  
**If present:** Continue to Step 2

---

### **Step 2: Check What Backend Receives**

SSH to VM and add debug logging:

```bash
ssh azureuser@130.107.48.166
cd /home/azureuser/ai/
```

**Add temporary debug logging to `app.py`:**

```python
@app.route('/api/solve-question', methods=['POST'])
def solve_question():
    try:
        data = request.get_json()
        question_text = data.get('question_text', '')
        subject = data.get('subject', '')
        context = data.get('context', '')
        use_intelligent_solver = data.get('use_intelligent_solver', True)
        solution_type = data.get('solution_type', 'step-by-step')
        
        # ⚠️ ADD THIS DEBUG LINE
        logger.info(f"🔍 DEBUG: Received solution_type = '{solution_type}' (type: {type(solution_type)})")
        logger.info(f"🔍 DEBUG: Full request data = {data}")
        
        # ... rest of code
```

**Restart service:**
```bash
sudo systemctl restart qadam-ai
```

**Check logs:**
```bash
sudo journalctl -u qadam-ai -f
```

**Submit from frontend and look for:**
```
🔍 DEBUG: Received solution_type = 'high-level' (type: <class 'str'>)
```

**If shows 'step-by-step':** Proxy is not forwarding correctly  
**If shows 'high-level':** Backend logic issue

---

### **Step 3: Check Proxy Forwarding**

The proxy might be filtering or not forwarding the parameter.

**Check proxy code on VM:**

```bash
ssh azureuser@130.107.48.166
cd /home/azureuser/proxy/  # or wherever proxy is located
cat app.py | grep -A 30 "solve-question"
```

**Look for:**
```python
@app.route('/solve-question', methods=['POST'])
def solve_question():
    data = request.get_json()
    
    # ⚠️ Check if it forwards ALL data
    response = requests.post(
        'http://localhost:5001/api/solve-question',
        json=data,  # ✅ Should forward entire data object
        timeout=60
    )
```

**If proxy is filtering fields, FIX IT:**
```python
# ❌ BAD - Only forwards specific fields
response = requests.post(
    'http://localhost:5001/api/solve-question',
    json={
        'question_text': data.get('question_text'),
        'subject': data.get('subject')
        # Missing solution_type!
    }
)

# ✅ GOOD - Forwards all fields
response = requests.post(
    'http://localhost:5001/api/solve-question',
    json=data,  # Forwards everything including solution_type
    timeout=60
)
```

---

## 🔧 Fixes

### **Fix 1: Update Proxy to Forward All Fields**

**File:** `/home/azureuser/proxy/app.py` (on VM)

```python
@app.route('/solve-question', methods=['POST'])
def solve_question():
    """Forward solve question request to AI service"""
    try:
        # Get ALL request data
        data = request.get_json()
        
        # Log what we received (for debugging)
        logger.info(f"📨 Proxy received: {list(data.keys())}")
        
        # Forward ENTIRE request to AI service
        response = requests.post(
            'http://localhost:5001/api/solve-question',
            json=data,  # ✅ Forwards ALL fields
            timeout=60
        )
        
        return jsonify(response.json()), response.status_code
        
    except Exception as e:
        logger.error(f"Proxy error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
```

**Restart proxy:**
```bash
sudo systemctl restart qadam-proxy
```

---

### **Fix 2: Add Explicit Logging in Backend**

**File:** `/home/azureuser/ai/app.py` (on VM)

Add logging right after extracting solution_type:

```python
solution_type = data.get('solution_type', 'step-by-step')

# Add this logging
logger.info(f"📋 Request parameters:")
logger.info(f"   - question_text: {question_text[:50]}...")
logger.info(f"   - subject: {subject}")
logger.info(f"   - solution_type: {solution_type}")
logger.info(f"   - use_intelligent_solver: {use_intelligent_solver}")
```

**Restart AI service:**
```bash
sudo systemctl restart qadam-ai
```

---

### **Fix 3: Verify Backend Logic**

Check that the bypass logic is working:

```python
# For high-level, skip Wolfram and use basic solver directly
if solution_type == 'high-level':
    logger.info(f"🤖 High-level mode: Using direct Groq API (bypassing Wolfram)")
    use_intelligent_solver = False  # Force basic solver for high-level
```

**Make sure this code is BEFORE the intelligent solver check:**

```python
# ✅ CORRECT ORDER
solution_type = data.get('solution_type', 'step-by-step')

# Bypass Wolfram for high-level
if solution_type == 'high-level':
    use_intelligent_solver = False

# Use Intelligent Question Solver if available and requested
if use_intelligent_solver and INTELLIGENT_SOLVER_AVAILABLE:
    # This will be skipped for high-level
    result = intelligent_solver.solve_question(...)
```

---

## 🧪 Testing Commands

### **Test 1: Direct to AI Service (Bypass Proxy)**

```bash
# Test high-level directly
curl -X POST http://130.107.48.166:5001/api/solve-question \
  -H "Content-Type: application/json" \
  -d '{
    "question_text": "What is 2+2?",
    "subject": "Mathematics",
    "solution_type": "high-level"
  }' | jq .

# Check logs immediately
ssh azureuser@130.107.48.166
sudo journalctl -u qadam-ai -n 20
```

**Expected in logs:**
```
📋 Request parameters:
   - solution_type: high-level
🤖 High-level mode: Using direct Groq API (bypassing Wolfram)
📝 Using basic solution generator (solution_type: high-level)
```

**If this works:** Proxy is the problem  
**If this doesn't work:** Backend code issue

---

### **Test 2: Through Proxy**

```bash
# Test through proxy (HTTPS)
curl -k -X POST https://130.107.48.166/solve-question \
  -H "Content-Type: application/json" \
  -d '{
    "question_text": "What is 2+2?",
    "subject": "Mathematics",
    "solution_type": "high-level"
  }' | jq .

# Check both proxy and AI logs
ssh azureuser@130.107.48.166
sudo journalctl -u qadam-proxy -n 20
sudo journalctl -u qadam-ai -n 20
```

**Expected:**
- Proxy logs show receiving request
- AI logs show "high-level" solution_type
- Response is fast and concise

---

### **Test 3: From Frontend**

1. Open DevTools → Network tab
2. Select "High-Level" from dropdown
3. Submit question
4. Check request payload in DevTools
5. Check response
6. Check VM logs

---

## 🎯 Most Likely Issues & Fixes

### **Issue 1: Proxy Not Forwarding Parameter**

**Symptom:** Direct curl to AI service works, but frontend doesn't

**Fix:** Update proxy to forward entire request body:
```python
json=data  # Instead of manually selecting fields
```

---

### **Issue 2: Parameter Name Mismatch**

**Symptom:** Frontend sends `solutionType` (camelCase) but backend expects `solution_type` (snake_case)

**Check frontend:**
```javascript
solution_type: solutionType  // ✅ Correct - uses snake_case in request
```

**If frontend uses camelCase, fix it:**
```javascript
// ❌ Wrong
solutionType: solutionType

// ✅ Correct
solution_type: solutionType
```

---

### **Issue 3: Backend Code Not Updated**

**Symptom:** Logs don't show "High-level mode" message

**Fix:** Verify backend-ai branch is actually deployed:
```bash
cd /home/azureuser/ai/
git branch  # Should show * backend-ai
git log -1  # Should show recent commit with high-level fix
grep -n "High-level mode" app.py  # Should find the line
```

---

## 📝 Verification Checklist

Run through these in order:

- [ ] Frontend sends `solution_type: "high-level"` (check DevTools)
- [ ] Direct curl to AI service with high-level works
- [ ] AI service logs show "High-level mode" message
- [ ] Curl through proxy with high-level works
- [ ] Proxy logs show forwarding request
- [ ] Frontend request through proxy works
- [ ] High-level returns plain text (no headings)
- [ ] Step-by-step returns markdown (with headings)

---

## 🚀 Quick Fix Script

Create this script on the VM to add debug logging:

**File:** `/home/azureuser/add_debug_logging.sh`

```bash
#!/bin/bash

# Add debug logging to AI service
cd /home/azureuser/ai/

# Backup original
cp app.py app.py.backup

# Add debug line after solution_type extraction
sed -i '/solution_type = data.get/a\        logger.info(f"🔍 DEBUG: solution_type={solution_type}, type={type(solution_type)}, data_keys={list(data.keys())}")' app.py

# Restart service
sudo systemctl restart qadam-ai

# Show logs
echo "Watching logs... Submit a request from frontend now"
sudo journalctl -u qadam-ai -f
```

**Run it:**
```bash
chmod +x /home/azureuser/add_debug_logging.sh
./add_debug_logging.sh
```

---

## 🎯 Summary

**The issue is most likely:**

1. **Proxy not forwarding `solution_type`** (80% probability)
2. **Backend code not actually deployed** (15% probability)
3. **Frontend sending wrong parameter name** (5% probability)

**Quick diagnostic:**

```bash
# Test direct to AI service
curl -X POST http://130.107.48.166:5001/api/solve-question \
  -H "Content-Type: application/json" \
  -d '{"question_text":"test","subject":"Math","solution_type":"high-level"}'

# If this works → Proxy issue
# If this doesn't work → Backend issue
```

**Next steps:**

1. Run the direct curl test above
2. Check the logs for "High-level mode" message
3. If present → Fix proxy
4. If absent → Verify backend-ai is deployed

---

**Let me know the result of the direct curl test and I'll provide the exact fix!** 🔍
