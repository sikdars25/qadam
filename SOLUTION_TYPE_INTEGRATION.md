# 🔄 Solution Type Integration - Frontend to Backend

## Overview

Complete integration guide for `solution_type` parameter from frontend to AI service.

**Status:** Frontend already sends `solution_type`, backend already receives it.  
**Issue:** Need to verify proxy is forwarding the parameter correctly.

---

## 📊 Current Architecture

```
Frontend (React)
    ↓ POST /solve-question
    ↓ { question_text, subject, solution_type }
    ↓
Proxy (130.107.48.166:443)
    ↓ Forwards to AI Service
    ↓
AI Service (130.107.48.166:5001)
    ↓ /api/solve-question
    ↓ Processes with solution_type
    ↓
Returns solution
```

---

## ✅ Frontend Implementation (ALREADY DONE)

### **File:** `frontend/src/components/DashboardQuestionSolver.js`

**State Management:**
```javascript
const [solutionType, setSolutionType] = useState('step-by-step');
```

**API Call:**
```javascript
const solveResponse = await axiosInstance.post(`${API_URL}/solve-question`, {
  question_text: questionText,
  subject: subject,
  solution_type: solutionType  // ✅ Already sending
});
```

**UI Selector:**
```javascript
<div className="control-group">
  <label>Solution Type</label>
  <select value={solutionType} onChange={(e) => setSolutionType(e.target.value)}>
    <option value="step-by-step">Step-by-Step</option>
    <option value="high-level">High-Level</option>
    <option value="with-diagram">With Diagram</option>
  </select>
</div>
```

**Status:** ✅ **Frontend is correctly sending `solution_type`**

---

## ✅ Backend Implementation (ALREADY DONE)

### **File:** `ai/app.py` (backend-ai branch)

**Extract Parameter:**
```python
solution_type = data.get('solution_type', 'step-by-step')  # ✅ Already extracting
```

**Bypass Wolfram for High-Level:**
```python
if solution_type == 'high-level':
    logger.info(f"🤖 High-level mode: Using direct Groq API (bypassing Wolfram)")
    use_intelligent_solver = False  # ✅ Already implemented
```

**Pass to Solver:**
```python
result = intelligent_solver.solve_question(processed_text, subject, solution_type)
# ✅ Already passing solution_type
```

**Status:** ✅ **Backend is correctly processing `solution_type`**

---

## ❓ Proxy Configuration (NEEDS VERIFICATION)

### **Expected Proxy Behavior:**

The proxy at `130.107.48.166` should forward ALL request body parameters to the AI service.

**Expected Flow:**
```
Frontend → Proxy (port 443)
    POST /solve-question
    Body: { question_text, subject, solution_type }
    ↓
Proxy → AI Service (port 5001)
    POST /api/solve-question
    Body: { question_text, subject, solution_type }  # Should forward ALL fields
```

---

## 🔍 Verification Steps

### **1. Check Frontend is Sending Parameter**

Open browser DevTools → Network tab → Submit question → Check request payload:

```json
{
  "question_text": "Find x where 2x + 5 = 15",
  "subject": "Mathematics",
  "solution_type": "high-level"  // ✅ Should be present
}
```

---

### **2. Check Proxy Forwarding**

SSH to proxy VM and check logs:

```bash
ssh azureuser@130.107.48.166

# Check proxy logs
sudo journalctl -u qadam-proxy -f

# Look for:
# - Incoming request with solution_type
# - Forwarded request to AI service
```

**Expected Log:**
```
Received POST /solve-question
Body: {"question_text": "...", "subject": "...", "solution_type": "high-level"}
Forwarding to AI service at 5001...
```

---

### **3. Check AI Service Receiving Parameter**

```bash
ssh azureuser@130.107.48.166

# Check AI service logs
sudo journalctl -u qadam-ai -f

# Look for:
# - solution_type in request
# - High-level mode message (if high-level)
# - Step-by-step mode message (if step-by-step)
```

**Expected Log for High-Level:**
```
📊 Math analysis: ...
🤖 High-level mode: Using direct Groq API (bypassing Wolfram)
📝 Using basic solution generator (solution_type: high-level)
```

**Expected Log for Step-by-Step:**
```
📊 Math analysis: ...
🤖 Using Intelligent Question Solver with Groq + Wolfram Alpha (solution_type: step-by-step)
```

---

## 🔧 Proxy Configuration File

### **Expected Proxy Code:**

The proxy should forward the entire request body without modification.

**File:** `proxy/app.py` (on VM)

```python
@app.route('/solve-question', methods=['POST'])
def solve_question():
    """Forward solve question request to AI service"""
    try:
        # Get request data
        data = request.get_json()
        
        # Forward to AI service (should include ALL fields)
        response = requests.post(
            'http://localhost:5001/api/solve-question',
            json=data,  # ✅ This forwards ALL fields including solution_type
            timeout=60
        )
        
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

**Key Point:** Using `json=data` forwards the entire request body, including `solution_type`.

---

## 🧪 Testing

### **Test 1: High-Level Request**

```bash
# Direct to AI service (bypasses proxy)
curl -X POST http://130.107.48.166:5001/api/solve-question \
  -H "Content-Type: application/json" \
  -d '{
    "question_text": "Find x where 2x + 5 = 15",
    "subject": "Mathematics",
    "solution_type": "high-level"
  }'
```

**Expected:**
- Fast response (~1-2 sec)
- Plain text output (no headings)
- Concise answer
- Logs show "High-level mode"

---

### **Test 2: Step-by-Step Request**

```bash
# Direct to AI service
curl -X POST http://130.107.48.166:5001/api/solve-question \
  -H "Content-Type: application/json" \
  -d '{
    "question_text": "Find x where 2x + 5 = 15",
    "subject": "Mathematics",
    "solution_type": "step-by-step"
  }'
```

**Expected:**
- Slower response (~5-8 sec)
- Markdown formatted (with headings)
- Detailed explanation
- Logs show "Intelligent Question Solver"

---

### **Test 3: Through Proxy**

```bash
# Through proxy (HTTPS)
curl -X POST https://130.107.48.166/solve-question \
  -H "Content-Type: application/json" \
  -k \
  -d '{
    "question_text": "Find x where 2x + 5 = 15",
    "subject": "Mathematics",
    "solution_type": "high-level"
  }'
```

**Expected:**
- Same result as direct AI service call
- Proxy logs show forwarding
- AI service logs show receiving request

---

## 🐛 Troubleshooting

### **Issue: Always Getting Step-by-Step**

**Possible Causes:**

1. **Frontend not sending parameter**
   - Check browser DevTools → Network
   - Verify `solution_type` in request payload

2. **Proxy not forwarding parameter**
   - Check proxy logs
   - Verify proxy code uses `json=data`

3. **Backend not reading parameter**
   - Check AI service logs
   - Verify `solution_type` is extracted

4. **Default value being used**
   - Backend defaults to `'step-by-step'` if not provided
   - Check if parameter is reaching backend

---

### **Debugging Commands:**

```bash
# SSH to VM
ssh azureuser@130.107.48.166

# Check proxy service
sudo systemctl status qadam-proxy
sudo journalctl -u qadam-proxy -n 50

# Check AI service
sudo systemctl status qadam-ai
sudo journalctl -u qadam-ai -n 50

# Test direct AI service
curl -X POST http://localhost:5001/api/solve-question \
  -H "Content-Type: application/json" \
  -d '{"question_text":"test","subject":"Math","solution_type":"high-level"}'

# Check if parameter is logged
sudo journalctl -u qadam-ai -f | grep "solution_type"
```

---

## 📝 Verification Checklist

After deployment, verify:

- [ ] Frontend sends `solution_type` in request (check DevTools)
- [ ] Proxy forwards `solution_type` to AI service (check proxy logs)
- [ ] AI service receives `solution_type` (check AI logs)
- [ ] High-level bypasses Wolfram (check logs for "High-level mode")
- [ ] High-level returns plain text (no headings)
- [ ] Step-by-step uses Wolfram (check logs for "Intelligent Question Solver")
- [ ] Step-by-step returns markdown (with headings)
- [ ] Response times are correct (1-2s vs 5-8s)

---

## 🚀 Deployment Steps

### **1. Deploy Backend Changes**

```bash
# SSH to VM
ssh azureuser@130.107.48.166

# Pull backend-ai branch
cd /home/azureuser/ai/
git fetch origin backend-ai
git checkout backend-ai
git pull origin backend-ai

# Restart AI service
sudo systemctl restart qadam-ai
sudo systemctl status qadam-ai
```

---

### **2. Verify Proxy Configuration**

```bash
# Check proxy code
cd /home/azureuser/proxy/
cat app.py | grep -A 20 "solve-question"

# Ensure it forwards entire request body
# Should see: json=data or similar
```

---

### **3. Test Integration**

```bash
# Test high-level
curl -X POST http://localhost:5001/api/solve-question \
  -H "Content-Type: application/json" \
  -d '{"question_text":"What is 2+2?","subject":"Math","solution_type":"high-level"}'

# Check logs
sudo journalctl -u qadam-ai -n 20 | grep "solution_type"
```

---

### **4. Test from Frontend**

1. Open frontend: `https://zealous-ocean-06e22b51e.3.azurestaticapps.net`
2. Select "High-Level" from dropdown
3. Submit a question
4. Verify:
   - Fast response
   - Plain text output
   - No section headings

---

## 📊 Expected Behavior Summary

| Solution Type | Model | Wolfram | Response Time | Format | Headings |
|--------------|-------|---------|---------------|--------|----------|
| **high-level** | 8B | ❌ No | 1-2 sec | Plain text | ❌ No |
| **step-by-step** | 70B | ✅ Yes | 5-8 sec | Markdown | ✅ Yes |

---

## 🎯 Summary

### **Current Status:**

✅ **Frontend:** Correctly sends `solution_type`  
✅ **Backend:** Correctly processes `solution_type`  
❓ **Proxy:** Needs verification that it forwards parameter

### **Action Items:**

1. ✅ Deploy backend-ai branch to AI VM
2. ❓ Verify proxy forwards `solution_type`
3. ✅ Test with curl (direct to AI service)
4. ❓ Test with frontend (through proxy)
5. ❓ Check logs to confirm correct path is taken

### **If Still Not Working:**

Check in this order:
1. Browser DevTools → Verify frontend sends parameter
2. Proxy logs → Verify proxy receives parameter
3. AI service logs → Verify AI service receives parameter
4. AI service logs → Verify correct path is taken (high-level vs step-by-step)

---

**The integration should work once backend-ai is deployed and proxy is verified!** 🚀
