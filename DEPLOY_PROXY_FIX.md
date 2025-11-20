# 🚀 Deploy Proxy Fix - Solution Type Forwarding

## Issue Found & Fixed

**Root Cause:** The proxy was NOT forwarding the `solution_type` parameter to the AI service!

**Branch:** `backend-proxy`  
**Commit:** `ef930a3`

---

## 🔍 What Was Wrong

### **The Problem:**

```
Frontend → Proxy → AI Service

Frontend sends:
{
  "question_text": "...",
  "subject": "Math",
  "solution_type": "high-level"  ✅ Sent
}

Proxy forwards:
{
  "question_text": "...",
  "subject": "Math",
  "context": ""
  // ❌ solution_type was MISSING!
}

AI Service receives:
{
  "solution_type": undefined → defaults to "step-by-step"
}
```

**Result:** Always used step-by-step, even when high-level was selected.

---

## ✅ What Was Fixed

### **File 1: `proxy/ai_client.py`**

**Before:**
```python
def solve_question_via_vm(question_text: str, subject: str = '', context: str = '') -> str:
    payload = {
        'question_text': question_text,
        'subject': subject,
        'context': context
        # ❌ Missing solution_type
    }
```

**After:**
```python
def solve_question_via_vm(question_text: str, subject: str = '', context: str = '', solution_type: str = 'step-by-step') -> str:
    payload = {
        'question_text': question_text,
        'subject': subject,
        'context': context,
        'solution_type': solution_type  # ✅ Now included
    }
```

---

### **File 2: `proxy/app.py`**

**Updated 2 endpoints:**

#### **Endpoint 1: `/solve-question` (Frontend, No Auth)**

**Before:**
```python
solution = solve_question_via_vm(
    question_text=question_text,
    subject=subject or "",
    context=chapter_context or ""
    # ❌ Missing solution_type
)
```

**After:**
```python
solution_type = data.get('solution_type', 'step-by-step')  # ✅ Extract

print(f"🎓 Solving question... (solution_type: {solution_type})")  # ✅ Log

solution = solve_question_via_vm(
    question_text=question_text,
    subject=subject or "",
    context=chapter_context or "",
    solution_type=solution_type  # ✅ Pass to AI service
)
```

---

#### **Endpoint 2: `/api/solve-question` (Authenticated)**

**Before:**
```python
solution = solve_question_via_vm(
    question_text=question_text,
    subject=subject or "",
    context=chapter_context or ""
    # ❌ Missing solution_type
)
```

**After:**
```python
solution_type = data.get('solution_type', 'step-by-step')  # ✅ Extract

print(f"🎓 Solving question... (solution_type: {solution_type})")  # ✅ Log

solution = solve_question_via_vm(
    question_text=question_text,
    subject=subject or "",
    context=chapter_context or "",
    solution_type=solution_type  # ✅ Pass to AI service
)
```

---

## 🔄 Complete Flow (After Fix)

```
Frontend (React)
    ↓
    POST /solve-question
    Body: { question_text, subject, solution_type: "high-level" }
    ↓
Proxy (130.107.48.166:443)
    ↓
    Extract: solution_type = data.get('solution_type', 'step-by-step')
    Log: "Solving question... (solution_type: high-level)"
    ↓
    Call: solve_question_via_vm(..., solution_type="high-level")
    ↓
AI Service (130.107.48.166:5001)
    ↓
    Receive: { question_text, subject, context, solution_type: "high-level" }
    ↓
    IF solution_type == "high-level":
        - Bypass Wolfram
        - Use 8B model
        - Concise prompt
        - Max tokens: 500
    ELSE:
        - Use Wolfram
        - Use 70B model
        - Detailed prompt
        - Max tokens: 4000
    ↓
Return solution
```

---

## 🚀 Deployment Steps

### **Step 1: Deploy Proxy Code**

```bash
# SSH to VM
ssh azureuser@130.107.48.166

# Navigate to proxy directory
cd /home/azureuser/proxy/

# Pull latest backend-proxy branch
git fetch origin backend-proxy
git checkout backend-proxy
git pull origin backend-proxy

# Verify changes
grep -n "solution_type" ai_client.py
grep -n "solution_type" app.py

# Should see solution_type parameter in both files
```

---

### **Step 2: Restart Proxy Service**

```bash
# Restart proxy
sudo systemctl restart qadam-proxy

# Check status
sudo systemctl status qadam-proxy

# Should show: "active (running)"
```

---

### **Step 3: Verify Deployment**

```bash
# Check proxy logs
sudo journalctl -u qadam-proxy -f

# In another terminal, test with curl
curl -X POST https://130.107.48.166/solve-question \
  -H "Content-Type: application/json" \
  -k \
  -d '{
    "question_text": "What is 2+2?",
    "subject": "Mathematics",
    "solution_type": "high-level"
  }'

# Proxy logs should show:
# "🎓 Solving question... (solution_type: high-level)"
```

---

### **Step 4: Check AI Service Logs**

```bash
# In another terminal, watch AI service logs
sudo journalctl -u qadam-ai -f

# Should see:
# "🤖 High-level mode: Using direct Groq API (bypassing Wolfram)"
# "📝 Using basic solution generator (solution_type: high-level)"
```

---

## 🧪 Testing

### **Test 1: High-Level via Proxy**

```bash
curl -X POST https://130.107.48.166/solve-question \
  -H "Content-Type: application/json" \
  -k \
  -d '{
    "question_text": "What is the derivative of x^2?",
    "subject": "Mathematics",
    "solution_type": "high-level"
  }' | jq .
```

**Expected:**
- Fast response (~1-2 sec)
- Plain text output (no headings)
- Concise answer
- Proxy logs: `(solution_type: high-level)`
- AI logs: `High-level mode: Using direct Groq API`

---

### **Test 2: Step-by-Step via Proxy**

```bash
curl -X POST https://130.107.48.166/solve-question \
  -H "Content-Type: application/json" \
  -k \
  -d '{
    "question_text": "What is the derivative of x^2?",
    "subject": "Mathematics",
    "solution_type": "step-by-step"
  }' | jq .
```

**Expected:**
- Slower response (~5-8 sec)
- Markdown formatted (with headings)
- Detailed explanation
- Proxy logs: `(solution_type: step-by-step)`
- AI logs: `Using Intelligent Question Solver with Groq + Wolfram Alpha`

---

### **Test 3: From Frontend**

1. Open: `https://zealous-ocean-06e22b51e.3.azurestaticapps.net`
2. Select **"High-Level"** from dropdown
3. Submit question: "What is 2+2?"
4. Verify:
   - ✅ Fast response
   - ✅ Plain text (no headings)
   - ✅ Concise answer

5. Select **"Step-by-Step"**
6. Submit same question
7. Verify:
   - ✅ Detailed response
   - ✅ Markdown headings
   - ✅ Comprehensive explanation

---

## 📊 Verification Checklist

After deployment:

- [ ] Proxy code updated (check git log)
- [ ] Proxy service restarted
- [ ] Proxy logs show `solution_type` parameter
- [ ] AI service logs show correct mode (high-level vs step-by-step)
- [ ] High-level returns fast, concise answers
- [ ] Step-by-step returns detailed, formatted answers
- [ ] Frontend dropdown works correctly
- [ ] Both options produce different outputs

---

## 🔍 Debugging

### **If Still Not Working:**

**1. Check Proxy Logs:**
```bash
sudo journalctl -u qadam-proxy -n 50 | grep solution_type
```

**Should see:**
```
Solving question... (solution_type: high-level)
```

**If NOT present:** Proxy code not deployed correctly

---

**2. Check AI Service Logs:**
```bash
sudo journalctl -u qadam-ai -n 50 | grep solution_type
```

**Should see:**
```
📋 Request parameters:
   - solution_type: high-level
🤖 High-level mode: Using direct Groq API
```

**If NOT present:** Parameter not reaching AI service

---

**3. Check Proxy Code:**
```bash
cd /home/azureuser/proxy/
git branch  # Should show * backend-proxy
git log -1  # Should show commit ef930a3
grep "solution_type" ai_client.py  # Should find parameter
grep "solution_type" app.py  # Should find extraction
```

---

**4. Manual Test:**
```bash
# Test proxy → AI forwarding
curl -X POST http://localhost:5001/api/solve-question \
  -H "Content-Type: application/json" \
  -d '{
    "question_text": "test",
    "subject": "Math",
    "solution_type": "high-level"
  }'

# Check AI logs immediately
sudo journalctl -u qadam-ai -n 10
```

---

## 📝 Summary

### **What Was Fixed:**

1. ✅ **ai_client.py:** Added `solution_type` parameter
2. ✅ **app.py:** Extract and forward `solution_type` (2 endpoints)
3. ✅ **Logging:** Added solution_type to log messages

### **What This Enables:**

- ✅ High-level mode: 8B model, no Wolfram, fast, concise
- ✅ Step-by-step mode: 70B model, Wolfram, detailed, comprehensive
- ✅ User choice respected from frontend to AI service
- ✅ Complete integration working end-to-end

### **Deployment:**

```bash
# Quick deploy script
ssh azureuser@130.107.48.166 << 'EOF'
cd /home/azureuser/proxy/
git fetch origin backend-proxy
git checkout backend-proxy
git pull origin backend-proxy
sudo systemctl restart qadam-proxy
sudo systemctl status qadam-proxy
echo "✅ Proxy deployed and restarted"
EOF
```

---

**The proxy fix is complete and ready to deploy!** 🚀

After deploying this, the complete flow will work:
- Frontend sends `solution_type`
- Proxy forwards `solution_type`
- AI service processes based on `solution_type`
- User gets the correct type of answer
