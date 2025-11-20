# 🤖 AI Service - Groq API Prompts and Templates

## Overview

The AI service uses **Groq API** with the **Llama 3.3 70B Versatile** model for question solving.

**Model:** `llama-3.3-70b-versatile`  
**API:** Groq Chat Completions API  
**Files:** `intelligent_question_solver.py`, `ai_helpers.py`, `app.py`

---

## 🎯 Main System Architecture

### **Two Solving Approaches:**

1. **Intelligent Question Solver** (Primary)
   - Uses Groq AI to extract mathematical expressions
   - Solves expressions with Wolfram Alpha
   - Interlinks results with AI-generated explanations

2. **Basic Solution Generator** (Fallback)
   - Direct Groq API call for complete solution
   - Used when intelligent solver fails or is disabled

---

## 📝 Prompt Templates

### **1. Intelligent Question Solver - Expression Extraction**

**File:** `intelligent_question_solver.py` (Lines 76-135)

**Purpose:** Extract pure mathematical expressions from question text

**System Prompt:**
```
You are a mathematical expression extraction expert. Always return valid JSON only.
```

**User Prompt Template:**
```python
prompt = f"""You are a mathematical expression analyzer. Your task is to extract ONLY the pure mathematical expressions from the given question text and identify their dependencies.

IMPORTANT RULES:
1. Extract ONLY mathematical expressions (equations, formulas, calculations)
2. Remove ALL natural language, questions, and explanations
3. Each expression should be deterministic and solvable
4. Identify which expressions depend on results from other expressions
5. Assign a unique ID to each expression
6. Specify dependencies as array of expression IDs

Subject Context: {subject if subject else 'General Mathematics'}

Question Text:
{question_text}

Return ONLY a JSON object in this exact format:
{{
  "expressions": [
    {{
      "id": "expr_1",
      "expression": "pure mathematical expression here",
      "type": "equation|integral|derivative|limit|etc",
      "description": "brief description of what this calculates",
      "depends_on": []
    }},
    {{
      "id": "expr_2",
      "expression": "another expression",
      "type": "equation",
      "description": "brief description",
      "depends_on": ["expr_1"]
    }}
  ],
  "question_summary": "brief summary of what the question asks",
  "final_goal": "what needs to be found or proven"
}}

Example for "Find x where 2x + 5 = 15, then calculate y = 3x - 2":
{{
  "expressions": [
    {{
      "id": "expr_1",
      "expression": "2x + 5 = 15",
      "type": "equation",
      "description": "solve for x",
      "depends_on": []
    }},
    {{
      "id": "expr_2",
      "expression": "y = 3x - 2",
      "type": "equation",
      "description": "calculate y using x from expr_1",
      "depends_on": ["expr_1"]
    }}
  ],
  "question_summary": "Find x from equation, then use it to calculate y",
  "final_goal": "Find the value of y"
}}

Now analyze the given question and return ONLY the JSON object."""
```

**API Configuration:**
```python
{
    'model': 'llama-3.3-70b-versatile',
    'messages': [
        {
            'role': 'system',
            'content': 'You are a mathematical expression extraction expert. Always return valid JSON only.'
        },
        {
            'role': 'user',
            'content': prompt
        }
    ],
    'temperature': 0.1,  # Low temperature for consistent extraction
    'max_tokens': 2000
}
```

---

### **2. Intelligent Question Solver - Solution Generation**

**File:** `intelligent_question_solver.py` (Lines 400+)

**Purpose:** Generate comprehensive solution with interlinked results

**System Prompt:**
```
You are an expert academic tutor. Provide clear, detailed explanations.
```

**User Prompt Template:**
```python
prompt = f"""Generate a comprehensive solution for this question using the solved expressions below.

Original Question:
{question_text}

Subject: {subject}

Solved Expressions:
{solved_expressions_text}

Instructions:
1. Explain the approach and methodology
2. Show how each expression was solved
3. Interlink the results (show how later expressions use earlier results)
4. Provide step-by-step reasoning
5. Include the final answer clearly marked as "FINAL ANSWER:"

Use proper mathematical notation with LaTeX:
- Inline math: $expression$
- Display math: $$expression$$

Generate a complete, well-structured solution:"""
```

**API Configuration:**
```python
{
    'model': 'llama-3.3-70b-versatile',
    'messages': [
        {
            'role': 'system',
            'content': 'You are an expert academic tutor. Provide clear, detailed explanations.'
        },
        {
            'role': 'user',
            'content': prompt
        }
    ],
    'temperature': 0.7,  # Higher temperature for creative explanations
    'max_tokens': 2000
}
```

---

### **3. Basic Solution Generator (Fallback)**

**File:** `ai_helpers.py` (Lines 211-242)

**Purpose:** Generate complete solution in one API call

**Prompt Template:**
```python
context_section = f'Context from textbook:\n{context}\n' if context else ''

prompt = f"""You are an expert tutor. Generate a detailed solution for the following question.

Subject: {subject if subject else 'General'}

Question:
{question_text}

{context_section}

Provide a step-by-step solution with:
1. Understanding the question
2. Key concepts
3. Step-by-step solution
4. Final answer

Solution:"""
```

**API Configuration:**
```python
{
    'model': 'llama-3.3-70b-versatile',
    'messages': [
        {
            'role': 'user',
            'content': prompt
        }
    ],
    'temperature': 0.7,
    'max_tokens': 1500
}
```

---

## 🔧 API Call Implementation

### **Groq API Call Function**

**File:** `ai_helpers.py` (Lines 100-150)

```python
def generate_with_groq(prompt, max_tokens=1000, temperature=0.7):
    """
    Generate text using Groq API
    
    Args:
        prompt: Input prompt
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature (0.0-1.0)
    
    Returns:
        Generated text
    """
    if not groq_client:
        return "Error: Groq API not configured. Please set GROQ_API_KEY environment variable."
    
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ Error calling Groq API: {e}")
        return f"Error generating response: {str(e)}"
```

---

## 🎨 Solution Type Handling

The frontend sends a `solution_type` parameter:
- `step-by-step` - Detailed solution
- `high-level` - Quick overview
- `with-diagram` - Includes visual aids

**Current Implementation:**
The solution type is **NOT yet integrated** into the prompts. All solutions are generated with the same detailed approach.

**Recommended Enhancement:**

```python
def get_solution_instructions(solution_type):
    """Get instructions based on solution type"""
    instructions = {
        "step-by-step": """
Provide a DETAILED step-by-step solution with:
- Clear explanation of each step
- Intermediate calculations shown
- Reasoning for each decision
- Mathematical notation for all expressions
- Final answer clearly marked
""",
        "high-level": """
Provide a CONCISE high-level solution with:
- Brief overview of the approach
- Key steps only (no detailed calculations)
- Main concepts involved
- Final answer
Keep it short and to the point.
""",
        "with-diagram": """
Provide a solution WITH VISUAL AIDS:
- Step-by-step explanation
- ASCII diagrams where helpful
- Visual representations of concepts
- Graphs or charts (as ASCII art)
- Final answer clearly marked
"""
    }
    return instructions.get(solution_type, instructions["step-by-step"])
```

---

## 📊 Complete Flow

### **Request Flow:**

```
1. Frontend sends question
   ↓
2. Backend receives at /api/solve-question
   ↓
3. Check if Intelligent Solver available
   ↓
4. IF Intelligent Solver:
   a. Extract expressions with Groq
   b. Solve expressions with Wolfram Alpha
   c. Generate explanation with Groq
   ↓
5. ELSE Basic Solver:
   a. Generate complete solution with Groq
   ↓
6. Format solution
   ↓
7. Return to frontend
```

### **API Endpoints:**

**Main Endpoint:** `/api/solve-question`

**Request Body:**
```json
{
  "question_text": "Find the derivative of x^2 + 3x + 2",
  "subject": "Mathematics",
  "context": "",
  "use_intelligent_solver": true
}
```

**Response:**
```json
{
  "success": true,
  "solution": "formatted solution text",
  "raw_solution": "unformatted solution",
  "extracted_expressions": [...],
  "dependency_graph": {...},
  "solving_order": [...],
  "solved_expressions": [...],
  "solver_type": "intelligent",
  "processing_time_seconds": 3.5
}
```

---

## 🔑 Environment Variables

**File:** `.env`

```bash
# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here

# Wolfram Alpha Configuration
WOLFRAM_APP_ID=your_wolfram_app_id_here

# Model Configuration (optional)
GROQ_MODEL=llama-3.3-70b-versatile
```

---

## 📈 Model Parameters

### **Expression Extraction:**
- **Model:** `llama-3.3-70b-versatile`
- **Temperature:** `0.1` (low for consistency)
- **Max Tokens:** `2000`
- **Purpose:** Extract structured data (JSON)

### **Solution Generation:**
- **Model:** `llama-3.3-70b-versatile`
- **Temperature:** `0.7` (higher for creativity)
- **Max Tokens:** `1500-2000`
- **Purpose:** Generate explanations

### **Why Llama 3.3 70B?**
- Large parameter count (70B) for complex reasoning
- Versatile - good at both structured extraction and creative writing
- Fast inference via Groq's LPU architecture
- Good at mathematical content

---

## 🎯 Prompt Engineering Best Practices

### **Used in Current Implementation:**

1. **Clear Role Definition**
   - "You are a mathematical expression analyzer"
   - "You are an expert academic tutor"

2. **Explicit Instructions**
   - "Extract ONLY mathematical expressions"
   - "Return ONLY a JSON object"

3. **Examples Provided**
   - JSON format example
   - Sample question with expected output

4. **Structured Output**
   - JSON schema specified
   - Field descriptions included

5. **Context Inclusion**
   - Subject context provided
   - Question text included

### **Potential Improvements:**

1. **Add Few-Shot Examples**
   - Include 2-3 complete examples
   - Show edge cases

2. **Integrate Solution Type**
   - Modify prompt based on user preference
   - Adjust detail level dynamically

3. **Add Constraints**
   - Maximum solution length
   - Required sections
   - Formatting rules

4. **Error Handling**
   - Specify what to do if question is unclear
   - How to handle unsolvable problems

---

## 🧪 Testing the Prompts

### **Test Expression Extraction:**

```bash
curl -X POST http://130.107.48.166:5001/api/solve-question \
  -H "Content-Type: application/json" \
  -d '{
    "question_text": "Find x where 2x + 5 = 15",
    "subject": "Mathematics",
    "use_intelligent_solver": true
  }'
```

### **Test Basic Solver:**

```bash
curl -X POST http://130.107.48.166:5001/api/solve-question \
  -H "Content-Type: application/json" \
  -d '{
    "question_text": "Explain photosynthesis",
    "subject": "Biology",
    "use_intelligent_solver": false
  }'
```

---

## 📝 Summary

### **Key Prompts:**

1. **Expression Extraction Prompt**
   - Extracts mathematical expressions as JSON
   - Temperature: 0.1
   - Max tokens: 2000

2. **Solution Generation Prompt**
   - Creates comprehensive explanations
   - Temperature: 0.7
   - Max tokens: 2000

3. **Basic Solution Prompt**
   - Fallback for non-mathematical questions
   - Temperature: 0.7
   - Max tokens: 1500

### **Model Used:**
- **Llama 3.3 70B Versatile** via Groq API

### **Integration Points:**
- Frontend → `/api/solve-question`
- Intelligent Solver → Groq + Wolfram Alpha
- Basic Solver → Groq only

---

## 🔄 Next Steps for Enhancement

1. **Integrate Solution Type**
   - Modify prompts based on `solution_type` parameter
   - Add conditional instructions

2. **Add Subject-Specific Prompts**
   - Physics: Include units, diagrams
   - Chemistry: Include molecular structures
   - Math: Include proofs, theorems

3. **Improve Error Handling**
   - Better prompts for unclear questions
   - Fallback strategies

4. **Add Prompt Versioning**
   - Track prompt changes
   - A/B test different prompts
   - Measure solution quality

---

**All prompts are now documented and ready for enhancement!** 🚀
