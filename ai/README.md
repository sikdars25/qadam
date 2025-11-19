# Intelligent Question Solver

## Overview

A sophisticated question-solving system that uses **Groq AI** for intelligent expression extraction and answer synthesis, combined with **Wolfram Alpha** for deterministic mathematical solving.

## Architecture

### 🎯 **New Approach: Smart Splitting with Dependency Management**

```
┌─────────────────────────────────────────────────────────────────┐
│                     ORIGINAL QUESTION TEXT                       │
│  "Find x where 2x + 5 = 15, then calculate y = 3x - 2"         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              STEP 1: GROQ AI - EXPRESSION EXTRACTION            │
│  ✓ Removes natural language                                     │
│  ✓ Extracts pure mathematical expressions                       │
│  ✓ Identifies dependencies between expressions                  │
│  ✓ Creates dependency graph                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EXTRACTED EXPRESSIONS                         │
│  expr_1: "2x + 5 = 15"           [independent]                 │
│  expr_2: "y = 3x - 2"            [depends on: expr_1]          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│         STEP 2: TOPOLOGICAL SORT - DETERMINE ORDER              │
│  Solving Order: expr_1 → expr_2                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│        STEP 3: WOLFRAM ALPHA - SOLVE IN DEPENDENCY ORDER        │
│  ┌──────────────────────────────────────────────────────┐      │
│  │ expr_1: "2x + 5 = 15"                                │      │
│  │ → Wolfram Alpha → Result: x = 5                      │      │
│  └──────────────────────────────────────────────────────┘      │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────┐      │
│  │ expr_2: "y = 3x - 2" (with x = 5 from expr_1)       │      │
│  │ → Wolfram Alpha → Result: y = 13                     │      │
│  └──────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│         STEP 4: GROQ AI - SYNTHESIZE FINAL ANSWER               │
│  ✓ Receives all solved expressions with dependencies            │
│  ✓ Creates comprehensive explanation                            │
│  ✓ Shows how results interlink                                  │
│  ✓ Provides step-by-step solution                               │
│  ✓ Highlights key insights                                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FINAL ANSWER                                │
│  ## Understanding the Question                                   │
│  We need to find x first, then use it to calculate y.          │
│                                                                  │
│  ## Step-by-Step Solution                                       │
│  ### Step 1: Solve for x                                        │
│  Expression: 2x + 5 = 15                                        │
│  Solution: x = 5                                                │
│                                                                  │
│  ### Step 2: Calculate y using x                                │
│  Expression: y = 3x - 2                                         │
│  Substituting x = 5: y = 3(5) - 2 = 13                         │
│                                                                  │
│  ## Final Answer: y = 13                                        │
└─────────────────────────────────────────────────────────────────┘
```

## Key Features

### ✅ **Intelligent Expression Extraction**
- Uses Groq AI to understand question context
- Extracts **only** deterministic mathematical expressions
- Removes all natural language and question text
- **No raw question text sent to Wolfram Alpha**

### ✅ **Dependency Management**
- Identifies which expressions depend on others
- Creates dependency graph
- Uses topological sort for correct solving order
- Passes results between dependent expressions

### ✅ **Interlinked Solutions**
- Not just serial array of independent solutions
- Results from one expression feed into the next
- Maintains context throughout solving process
- Handles complex multi-step problems

### ✅ **Comprehensive Explanations**
- Groq AI synthesizes final answer
- Shows logical flow between steps
- Explains how results connect
- Educational and clear presentation

## Components

### 1. **GroqExpressionExtractor**
```python
# Extracts expressions with dependencies
result = extractor.extract_expressions_with_dependencies(question_text, subject)

# Returns:
{
  "expressions": [
    {
      "id": "expr_1",
      "expression": "2x + 5 = 15",
      "type": "equation",
      "description": "solve for x",
      "depends_on": []
    },
    {
      "id": "expr_2",
      "expression": "y = 3x - 2",
      "type": "equation",
      "description": "calculate y using x",
      "depends_on": ["expr_1"]
    }
  ],
  "question_summary": "Find x, then calculate y",
  "final_goal": "Find the value of y"
}
```

### 2. **WolframAlphaSolver**
```python
# Solves individual expressions
solution = solver.solve_expression(expression, expr_id, context)

# Context contains results from dependent expressions
# Allows chaining of results
```

### 3. **GroqAnswerSynthesizer**
```python
# Creates comprehensive final answer
answer = synthesizer.synthesize_final_answer(
    original_question,
    extracted_data,
    solved_expressions,
    subject
)

# Returns formatted explanation with:
# - Understanding of question
# - Step-by-step solution
# - Interlinking of results
# - Final answer
# - Key insights
```

### 4. **IntelligentQuestionSolver**
```python
# Main orchestrator
solver = IntelligentQuestionSolver()
result = solver.solve_question(question_text, subject)

# Handles complete pipeline:
# 1. Extract expressions (Groq)
# 2. Determine solving order (Topological sort)
# 3. Solve expressions (Wolfram Alpha)
# 4. Synthesize answer (Groq)
```

## Usage

### Basic Usage

```python
from intelligent_question_solver import IntelligentQuestionSolver

# Initialize solver
solver = IntelligentQuestionSolver()

# Solve a question
question = "Find x where 2x + 5 = 15, then calculate y = 3x - 2"
result = solver.solve_question(question, subject="Algebra")

if result['success']:
    print(result['final_answer'])
    print(f"Solved in {result['processing_time_seconds']}s")
else:
    print(f"Error: {result['error']}")
```

### Advanced Usage

```python
# Access detailed information
result = solver.solve_question(question, subject="Physics")

# View extracted expressions
for expr in result['extracted_expressions']:
    print(f"{expr['id']}: {expr['expression']}")
    print(f"  Depends on: {expr['depends_on']}")

# View solving order
print(f"Solving order: {' -> '.join(result['solving_order'])}")

# View individual solutions
for solution in result['solved_expressions']:
    print(f"{solution['expr_id']}: {solution['result']}")
    print(f"  Steps: {solution['steps']}")

# View final synthesized answer
print(result['final_answer'])
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Required: Groq API Key
GROQ_API_KEY=your_groq_api_key_here

# Required: Wolfram Alpha App ID
WOLFRAM_APP_ID=your_wolfram_app_id_here
```

### Get API Keys

**Groq API:**
1. Visit https://console.groq.com
2. Sign up or log in
3. Go to API Keys section
4. Create a new API key
5. Copy to `.env` file

**Wolfram Alpha:**
1. Visit https://products.wolframalpha.com/api
2. Sign up for a free account
3. Create a new app
4. Copy the App ID to `.env` file

## Advantages Over Previous Approach

### ❌ **Old Approach:**
- Split by simple regex (`.`, `!`, `?`)
- Sent entire sentences to Wolfram Alpha
- No dependency management
- Serial processing without context
- Natural language mixed with math

### ✅ **New Approach:**
- Intelligent extraction with Groq AI
- Only pure mathematical expressions to Wolfram
- Full dependency graph and ordering
- Context-aware solving with result chaining
- Clean separation of concerns

## Example Scenarios

### Scenario 1: Simple Dependent Equations
```
Question: "Find x where 2x + 5 = 15, then calculate y = 3x - 2"

Extraction:
  expr_1: "2x + 5 = 15" (independent)
  expr_2: "y = 3x - 2" (depends on expr_1)

Solving Order: expr_1 → expr_2

Solutions:
  expr_1: x = 5
  expr_2: y = 13 (using x = 5)

Final Answer: y = 13
```

### Scenario 2: Complex Physics Problem
```
Question: "A ball is thrown upward with velocity 20 m/s. 
Find the maximum height reached, then calculate the time 
to return to ground level."

Extraction:
  expr_1: "h = (v²)/(2g)" where v=20, g=9.8
  expr_2: "t = 2v/g" (depends on expr_1 for validation)

Solving Order: expr_1 → expr_2

Solutions:
  expr_1: h = 20.4 meters
  expr_2: t = 4.08 seconds

Final Answer: Maximum height is 20.4m, returns in 4.08s
```

### Scenario 3: Multi-Step Calculus
```
Question: "Find the derivative of f(x) = x³ + 2x², 
then find critical points, then determine if they are 
maxima or minima."

Extraction:
  expr_1: "d/dx(x³ + 2x²)"
  expr_2: "3x² + 4x = 0" (depends on expr_1)
  expr_3: "d²/dx²(x³ + 2x²)" (depends on expr_1)
  expr_4: "Evaluate second derivative at critical points" 
          (depends on expr_2 and expr_3)

Solving Order: expr_1 → expr_2 → expr_3 → expr_4

Solutions: [Interlinked step-by-step]
```

## Testing

Run the built-in test suite:

```bash
python intelligent_question_solver.py
```

## Integration with OCR Service

```python
# In your OCR processing pipeline:
from ai.intelligent_question_solver import IntelligentQuestionSolver

# After OCR extraction
ocr_text = extract_text_from_image(image)

# Solve with intelligent solver
solver = IntelligentQuestionSolver()
result = solver.solve_question(ocr_text, subject="Mathematics")

# Return to user
return {
    'ocr_text': ocr_text,
    'solution': result['final_answer'],
    'processing_time': result['processing_time_seconds']
}
```

## Performance

- **Expression Extraction**: ~2-3 seconds (Groq API)
- **Per Expression Solving**: ~1-2 seconds (Wolfram Alpha)
- **Answer Synthesis**: ~3-5 seconds (Groq API)
- **Total**: ~6-15 seconds for typical questions

## Error Handling

The system gracefully handles:
- Missing API keys (returns clear error)
- Groq API failures (returns extraction error)
- Wolfram Alpha failures (attempts fallback)
- Invalid JSON responses (parsing errors)
- Circular dependencies (topological sort handles)

## Logging

Comprehensive logging at each stage:
```
[STEP 1] Extracting expressions with Groq AI...
  ✓ Extracted 3 expressions
  - expr_1: 2x + 5 = 15 (independent)
  - expr_2: y = 3x - 2 (depends on: expr_1)

[STEP 2] Solving expressions with Wolfram Alpha...
  Solving order: expr_1 -> expr_2
  Solving expr_1: 2x + 5 = 15...
  ✓ expr_1 solved: x = 5
  Solving expr_2: y = 3x - 2...
  ✓ expr_2 solved: y = 13

[STEP 3] Synthesizing final answer with Groq AI...
  ✓ Final answer generated

✓ COMPLETED in 8.45s
```

## License

Part of the CBSE Qadam project.
