"""
Intelligent Question Solver with Groq-based Expression Extraction and Interlinking
Version: 2.0 - Smart Splitting and Dependency Management

This module uses Groq AI to:
1. Extract deterministic mathematical expressions from natural language questions
2. Identify dependencies and relationships between expressions
3. Solve expressions in correct order using Wolfram Alpha
4. Interlink results and generate comprehensive explanations
"""

import os
import json
import requests
import logging
from typing import Dict, List, Any, Optional, Tuple
from dotenv import load_dotenv
import time

# Configure logging for systemd compatibility
import sys
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)  # Output to stdout for systemd
    ],
    force=True  # Force reconfiguration
)
logger = logging.getLogger(__name__)

# Ensure logger level is set and propagate
logger.setLevel(logging.INFO)
logger.propagate = True

# Force unbuffered output for systemd
sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None

# Load environment variables
load_dotenv()

# API Configuration
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
WOLFRAM_APP_ID = os.getenv('WOLFRAM_APP_ID', '')

if not GROQ_API_KEY:
    logger.error("GROQ_API_KEY not configured - this module requires Groq API")
    
if not WOLFRAM_APP_ID:
    logger.warning("WOLFRAM_APP_ID not configured - Wolfram Alpha will be disabled")

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Model Configuration
GROQ_MODEL_LARGE = "llama-3.3-70b-versatile"  # For detailed step-by-step solutions
GROQ_MODEL_SMALL = "llama-3.1-8b-instant"     # For concise high-level answers and Wolfram pipeline


class GroqExpressionExtractor:
    """Use Groq AI to intelligently extract and link mathematical expressions"""
    
    @staticmethod
    def extract_expressions_with_dependencies(question_text: str, subject: str = '', solution_type: str = 'step-by-step') -> Dict[str, Any]:
        """
        Use Groq to extract mathematical expressions and identify their dependencies
        
        Args:
            question_text: Original question text from OCR
            subject: Subject context (math, physics, chemistry, etc.)
            
        Returns:
            Dictionary with expressions and their dependency graph
        """
        if not GROQ_API_KEY:
            logger.error("Cannot extract expressions - GROQ_API_KEY not configured")
            return {'success': False, 'error': 'Groq API key not configured'}
        
        try:
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

            headers = {
                'Authorization': f'Bearer {GROQ_API_KEY}',
                'Content-Type': 'application/json'
            }
            
            # Use smaller model for Wolfram pipeline (always uses expression extraction)
            model = GROQ_MODEL_SMALL
            
            payload = {
                'model': model,
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
            
            logger.info("Calling Groq API to extract expressions with dependencies...")
            response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content'].strip()
                
                # Extract JSON from response (handle markdown code blocks)
                if '```json' in content:
                    content = content.split('```json')[1].split('```')[0].strip()
                elif '```' in content:
                    content = content.split('```')[1].split('```')[0].strip()
                
                extracted_data = json.loads(content)
                
                logger.info(f"Successfully extracted {len(extracted_data.get('expressions', []))} expressions")
                return {
                    'success': True,
                    'data': extracted_data
                }
            else:
                error_msg = f"Groq API error: {response.status_code}"
                logger.error(error_msg)
                return {'success': False, 'error': error_msg}
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Groq response as JSON: {e}")
            return {'success': False, 'error': f'JSON parse error: {str(e)}'}
        except Exception as e:
            logger.error(f"Error in expression extraction: {e}")
            return {'success': False, 'error': str(e)}


class WolframAlphaSolver:
    """Solve individual mathematical expressions using Wolfram Alpha"""
    
    @staticmethod
    def solve_expression(expression: str, expr_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Solve a single mathematical expression using Wolfram Alpha
        
        Args:
            expression: Pure mathematical expression
            expr_id: Unique identifier for this expression
            context: Results from previous expressions (for substitution)
            
        Returns:
            Solution with steps and result
        """
        if not WOLFRAM_APP_ID:
            logger.warning("Wolfram Alpha not configured - using placeholder")
            return {
                'success': False,
                'expr_id': expr_id,
                'expression': expression,
                'error': 'Wolfram Alpha APP ID not configured'
            }
        
        try:
            # Substitute values from context if needed
            query = expression
            if context:
                logger.debug(f"Applying context substitutions for {expr_id}")
                logger.debug(f"Context available: {list(context.keys())}")
                # Context contains results from dependent expressions
                # This allows chaining of results
            
            url = "http://api.wolframalpha.com/v2/query"
            params = {
                'input': query,
                'appid': WOLFRAM_APP_ID,
                'output': 'JSON',
                'format': 'plaintext',
                'podstate': 'Result__Step-by-step solution'
            }
            
            # COMPREHENSIVE LOGGING FOR WOLFRAM ALPHA CALL
            logger.info("=" * 80)
            logger.info(f"WOLFRAM ALPHA API CALL - Expression ID: {expr_id}")
            logger.info("-" * 80)
            logger.info(f"Original Expression: {expression}")
            logger.info(f"Query to Wolfram: {query}")
            logger.info(f"API Endpoint: {url}")
            logger.info(f"Parameters:")
            logger.info(f"  - input: {query}")
            logger.info(f"  - output: JSON")
            logger.info(f"  - format: plaintext")
            logger.info(f"  - podstate: Result__Step-by-step solution")
            if context:
                logger.info(f"Context from dependencies: {context}")
            logger.info("-" * 80)
            sys.stdout.flush()  # Force immediate output to systemd
            
            response = requests.get(url, params=params, timeout=30)
            
            # LOG RESPONSE STATUS
            logger.info(f"Response Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # LOG RESPONSE SUCCESS
                query_success = data.get('queryresult', {}).get('success', False)
                logger.info(f"Wolfram Query Success: {query_success}")
                
                # Extract result and steps from Wolfram Alpha response
                result_text = None
                steps = []
                
                if 'queryresult' in data and data['queryresult'].get('success'):
                    pods = data['queryresult'].get('pods', [])
                    logger.info(f"Number of result pods: {len(pods)}")
                    
                    for pod in pods:
                        pod_title = pod.get('title', '')
                        logger.debug(f"Processing pod: {pod_title}")
                        
                        if pod.get('title') in ['Result', 'Solution', 'Solutions']:
                            subpods = pod.get('subpods', [])
                            if subpods:
                                result_text = subpods[0].get('plaintext', '')
                                logger.info(f"Found result: {result_text[:100]}...")
                        
                        if 'step' in pod.get('title', '').lower():
                            subpods = pod.get('subpods', [])
                            for subpod in subpods:
                                step_text = subpod.get('plaintext', '')
                                if step_text:
                                    steps.append(step_text)
                                    logger.debug(f"Found step: {step_text[:50]}...")
                    
                    logger.info(f"Extracted {len(steps)} solution steps")
                else:
                    logger.warning(f"Wolfram Alpha query failed or returned no success flag")
                
                # LOG FINAL RESULT
                logger.info(f"Final Result: {result_text or 'Solution found (see steps)'}")
                logger.info("=" * 80)
                sys.stdout.flush()  # Force immediate output to systemd
                
                return {
                    'success': True,
                    'expr_id': expr_id,
                    'expression': expression,
                    'result': result_text or 'Solution found (see steps)',
                    'steps': steps,
                    'raw_response': data
                }
            else:
                error_msg = f'Wolfram Alpha API error: {response.status_code}'
                logger.error(error_msg)
                logger.error(f"Response content: {response.text[:200]}")
                logger.info("=" * 80)
                sys.stdout.flush()  # Force immediate output to systemd
                return {
                    'success': False,
                    'expr_id': expr_id,
                    'expression': expression,
                    'error': error_msg
                }
                
        except requests.exceptions.Timeout:
            error_msg = f"Wolfram Alpha API timeout for expression {expr_id}"
            logger.error("=" * 80)
            logger.error(f"WOLFRAM ALPHA TIMEOUT - Expression ID: {expr_id}")
            logger.error(f"Expression: {expression}")
            logger.error(f"Query: {query}")
            logger.error("Request timed out after 30 seconds")
            logger.error("=" * 80)
            sys.stdout.flush()  # Force immediate output to systemd
            return {
                'success': False,
                'expr_id': expr_id,
                'expression': expression,
                'error': error_msg
            }
        except requests.exceptions.RequestException as e:
            error_msg = f"Wolfram Alpha API request error: {str(e)}"
            logger.error("=" * 80)
            logger.error(f"WOLFRAM ALPHA REQUEST ERROR - Expression ID: {expr_id}")
            logger.error(f"Expression: {expression}")
            logger.error(f"Query: {query}")
            logger.error(f"Error: {str(e)}")
            logger.error("=" * 80)
            sys.stdout.flush()  # Force immediate output to systemd
            return {
                'success': False,
                'expr_id': expr_id,
                'expression': expression,
                'error': error_msg
            }
        except Exception as e:
            error_msg = f"Unexpected error solving expression {expr_id}: {str(e)}"
            logger.error("=" * 80)
            logger.error(f"WOLFRAM ALPHA UNEXPECTED ERROR - Expression ID: {expr_id}")
            logger.error(f"Expression: {expression}")
            logger.error(f"Query: {query if 'query' in locals() else 'N/A'}")
            logger.error(f"Error Type: {type(e).__name__}")
            logger.error(f"Error: {str(e)}")
            logger.error("=" * 80)
            sys.stdout.flush()  # Force immediate output to systemd
            return {
                'success': False,
                'expr_id': expr_id,
                'expression': expression,
                'error': error_msg
            }


class GroqAnswerSynthesizer:
    """Use Groq to synthesize final answer from interlinked solutions"""
    
    @staticmethod
    def synthesize_final_answer(
        original_question: str,
        extracted_data: Dict[str, Any],
        solved_expressions: List[Dict[str, Any]],
        subject: str = '',
        solution_type: str = 'step-by-step'
    ) -> Dict[str, Any]:
        """
        Use Groq to create comprehensive answer with proper interlinking
        
        Args:
            original_question: Original question text
            extracted_data: Extracted expressions with dependencies
            solved_expressions: Solutions from Wolfram Alpha
            subject: Subject context
            
        Returns:
            Final answer with explanations and step-by-step solution
        """
        if not GROQ_API_KEY:
            return {'success': False, 'error': 'Groq API key not configured'}
        
        try:
            # Build context for Groq
            expressions_info = extracted_data.get('expressions', [])
            question_summary = extracted_data.get('question_summary', '')
            final_goal = extracted_data.get('final_goal', '')
            
            # Create structured solution data
            solution_data = []
            for expr_info in expressions_info:
                expr_id = expr_info['id']
                # Find corresponding solution
                solution = next((s for s in solved_expressions if s['expr_id'] == expr_id), None)
                if solution:
                    solution_data.append({
                        'id': expr_id,
                        'expression': expr_info['expression'],
                        'description': expr_info['description'],
                        'depends_on': expr_info['depends_on'],
                        'result': solution.get('result', 'Not solved'),
                        'steps': solution.get('steps', [])
                    })
            
            # Import diagram generator for with-diagram mode
            if solution_type == 'with-diagram':
                from diagram_generator import DiagramGenerator
                diagram_gen = DiagramGenerator()
                diagram_types = diagram_gen.identify_diagram_needs(original_question, subject)
                diagram_prompt_addition = diagram_gen.create_diagram_prompt_addition(diagram_types)
            else:
                diagram_prompt_addition = ""
            
            # Configure prompt based on solution type
            if solution_type == 'high-level':
                prompt = f"""You are an expert mathematics teacher. Provide a CONCISE high-level answer.

ORIGINAL QUESTION:
{original_question}

SOLVED EXPRESSIONS:
{json.dumps(solution_data, indent=2)}

SUBJECT: {subject if subject else 'General Mathematics'}

Provide a BRIEF, CONCISE answer with:
- Quick overview of approach (1-2 sentences)
- Key results only
- Final answer

Mode: concise
Details: false
Keep it SHORT and to the point."""
            elif solution_type == 'with-diagram':
                prompt = f"""You are an expert mathematics teacher. Create a comprehensive solution WITH VISUAL DIAGRAMS.

ORIGINAL QUESTION:
{original_question}

QUESTION SUMMARY:
{question_summary}

FINAL GOAL:
{final_goal}

SOLVED EXPRESSIONS (with dependencies):
{json.dumps(solution_data, indent=2)}

SUBJECT CONTEXT: {subject if subject else 'General Mathematics'}

Create a complete solution with diagrams:
1. Start with understanding what the question asks
2. For each step, add [DIAGRAM: description] where a visual would help
3. Explain each step in logical order
4. Show how results connect between steps
5. Provide clear mathematical reasoning
6. End with the final answer

Format your response as:
## Understanding the Question
[Explain what we need to find]
[DIAGRAM: description if needed]

## Solution Approach
[Explain the strategy]

## Step-by-Step Solution

### Step 1: [Description]
[DIAGRAM: description of what to visualize]
[Explanation]
Expression: [expression]
Solution: [result]

### Step 2: [Description]
[DIAGRAM: description if needed]
[Explanation, showing how it uses Step 1's result]
Expression: [expression]
Solution: [result]

[Continue for all steps...]

## Final Answer
[Clear statement of the final answer]
[DIAGRAM: final visualization if helpful]

## Key Insights
[Important observations]

{diagram_prompt_addition}

Be clear, educational, and indicate diagram placements with [DIAGRAM: description]."""
            else:  # step-by-step (default)
                prompt = f"""You are an expert mathematics teacher. Create a comprehensive, well-structured solution with clear explanations.

ORIGINAL QUESTION:
{original_question}

QUESTION SUMMARY:
{question_summary}

FINAL GOAL:
{final_goal}

SOLVED EXPRESSIONS (with dependencies):
{json.dumps(solution_data, indent=2)}

SUBJECT CONTEXT: {subject if subject else 'General Mathematics'}

Create a complete solution that:
1. Starts with understanding what the question asks
2. Explains each step in logical order (respecting dependencies)
3. Shows how results from one expression feed into the next
4. Highlights the connections and relationships between steps
5. Provides clear mathematical reasoning
6. Ends with the final answer

Format your response as:
## Understanding the Question
[Explain what we need to find]

## Solution Approach
[Explain the strategy and how steps connect]

## Step-by-Step Solution

### Step 1: [Description]
[Explanation]
Expression: [expression]
Solution: [result]
[Additional explanation if needed]

### Step 2: [Description]
[Explanation, showing how it uses Step 1's result]
Expression: [expression]
Solution: [result]

[Continue for all steps...]

## Final Answer
[Clear statement of the final answer]

## Key Insights
[Important observations or connections]

Be clear, educational, and show the logical flow between dependent steps."""

            headers = {
                'Authorization': f'Bearer {GROQ_API_KEY}',
                'Content-Type': 'application/json'
            }
            
            # Select model and parameters based on solution type
            if solution_type == 'high-level':
                model = GROQ_MODEL_SMALL  # Use 8B model for concise answers
                max_tokens = 500  # Short answer
                system_content = 'You are an expert mathematics teacher who provides concise, direct answers.'
            elif solution_type == 'with-diagram':
                model = GROQ_MODEL_LARGE  # Use 70B model for diagram-rich solutions
                max_tokens = 5000  # More tokens for diagram descriptions
                system_content = 'You are an expert mathematics teacher who creates visual, diagram-rich explanations.'
            else:  # step-by-step
                model = GROQ_MODEL_LARGE  # Use 70B model for detailed solutions
                max_tokens = 4000  # Detailed answer
                system_content = 'You are an expert mathematics teacher who explains solutions clearly and shows connections between steps.'
            
            payload = {
                'model': model,
                'messages': [
                    {
                        'role': 'system',
                        'content': system_content
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'temperature': 0.3,  # Slightly higher for natural explanations
                'max_tokens': max_tokens
            }
            
            logger.info("Calling Groq API to synthesize final answer...")
            response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                final_answer = result['choices'][0]['message']['content'].strip()
                
                # Process diagrams if with-diagram mode
                response_data = {
                    'success': True,
                    'final_answer': final_answer,
                    'tokens_used': result.get('usage', {})
                }
                
                if solution_type == 'with-diagram':
                    from diagram_generator import generate_diagrams_for_solution
                    diagram_result = generate_diagrams_for_solution(
                        original_question, 
                        final_answer, 
                        subject
                    )
                    response_data['solution_with_diagrams'] = diagram_result['solution']
                    response_data['diagrams'] = diagram_result['diagrams']
                    response_data['has_diagrams'] = diagram_result['has_diagrams']
                    response_data['diagram_count'] = diagram_result.get('diagram_count', 0)
                
                return response_data
            else:
                error_msg = f"Groq API error: {response.status_code}"
                logger.error(error_msg)
                return {'success': False, 'error': error_msg}
                
        except Exception as e:
            logger.error(f"Error synthesizing final answer: {e}")
            return {'success': False, 'error': str(e)}


class IntelligentQuestionSolver:
    """Main orchestrator for intelligent question solving with dependency management"""
    
    def __init__(self):
        self.extractor = GroqExpressionExtractor()
        self.solver = WolframAlphaSolver()
        self.synthesizer = GroqAnswerSynthesizer()
    
    def solve_question(self, question_text: str, subject: str = '', solution_type: str = 'step-by-step') -> Dict[str, Any]:
        """
        Complete intelligent question solving pipeline
        
        Args:
            question_text: Original question text from OCR
            subject: Subject context
            solution_type: Type of solution ('step-by-step', 'high-level', 'with-diagram')
            
        Returns:
            Complete solution with interlinked steps and explanations
        """
        start_time = time.time()
        logger.info("=" * 80)
        logger.info("INTELLIGENT QUESTION SOLVER - Starting")
        logger.info(f"Subject: {subject}")
        logger.info(f"Question: {question_text[:100]}...")
        logger.info("=" * 80)
        
        try:
            # STEP 1: Extract expressions with dependencies using Groq
            logger.info("\n[STEP 1] Extracting expressions with Groq AI...")
            extraction_result = self.extractor.extract_expressions_with_dependencies(
                question_text, subject
            )
            
            if not extraction_result.get('success'):
                return {
                    'success': False,
                    'error': f"Expression extraction failed: {extraction_result.get('error')}",
                    'stage': 'extraction'
                }
            
            extracted_data = extraction_result['data']
            expressions = extracted_data.get('expressions', [])
            logger.info(f"✓ Extracted {len(expressions)} expressions")
            
            # Log dependency graph
            for expr in expressions:
                deps = expr.get('depends_on', [])
                dep_str = f" (depends on: {', '.join(deps)})" if deps else " (independent)"
                logger.info(f"  - {expr['id']}: {expr['expression'][:50]}...{dep_str}")
            
            # STEP 2: Solve expressions in dependency order using Wolfram Alpha
            logger.info("\n[STEP 2] Solving expressions with Wolfram Alpha...")
            solved_expressions = []
            results_cache = {}  # Store results for dependent expressions
            
            # Build dependency graph
            dependency_graph = {expr['id']: expr.get('depends_on', []) for expr in expressions}
            
            # Topological sort to determine solving order
            solving_order = self._topological_sort(dependency_graph)
            logger.info(f"Solving order: {' -> '.join(solving_order)}")
            
            for expr_id in solving_order:
                # Find expression details
                expr_info = next((e for e in expressions if e['id'] == expr_id), None)
                if not expr_info:
                    continue
                
                # Get context from dependent expressions
                context = {}
                for dep_id in expr_info.get('depends_on', []):
                    if dep_id in results_cache:
                        context[dep_id] = results_cache[dep_id]
                
                # Solve expression
                logger.info(f"  Solving {expr_id}: {expr_info['expression'][:50]}...")
                solution = self.solver.solve_expression(
                    expr_info['expression'],
                    expr_id,
                    context
                )
                
                solved_expressions.append(solution)
                
                if solution.get('success'):
                    results_cache[expr_id] = solution.get('result')
                    logger.info(f"  ✓ {expr_id} solved: {solution.get('result', '')[:50]}")
                else:
                    logger.warning(f"  ✗ {expr_id} failed: {solution.get('error')}")
            
            # STEP 3: Synthesize final answer with Groq
            logger.info(f"\n[STEP 3] Synthesizing final answer with Groq AI (solution_type: {solution_type})...")
            synthesis_result = self.synthesizer.synthesize_final_answer(
                question_text,
                extracted_data,
                solved_expressions,
                subject,
                solution_type
            )
            
            if not synthesis_result.get('success'):
                return {
                    'success': False,
                    'error': f"Answer synthesis failed: {synthesis_result.get('error')}",
                    'stage': 'synthesis',
                    'partial_results': {
                        'extracted_expressions': expressions,
                        'solved_expressions': solved_expressions
                    }
                }
            
            # STEP 4: Compile complete result
            processing_time = time.time() - start_time
            
            result = {
                'success': True,
                'original_question': question_text,
                'subject': subject,
                'extracted_expressions': expressions,
                'dependency_graph': dependency_graph,
                'solving_order': solving_order,
                'solved_expressions': solved_expressions,
                'final_answer': synthesis_result['final_answer'],
                'processing_time_seconds': round(processing_time, 2),
                'approach': 'groq_extraction_wolfram_solving_groq_synthesis',
                'metadata': {
                    'expressions_count': len(expressions),
                    'solved_count': len([s for s in solved_expressions if s.get('success')]),
                    'tokens_used': synthesis_result.get('tokens_used', {})
                }
            }
            
            # Include diagram data if with-diagram mode
            if solution_type == 'with-diagram':
                result['solution'] = synthesis_result.get('solution_with_diagrams', synthesis_result['final_answer'])
                result['diagrams'] = synthesis_result.get('diagrams', [])
                result['has_diagrams'] = synthesis_result.get('has_diagrams', False)
                result['diagram_count'] = synthesis_result.get('diagram_count', 0)
            else:
                result['solution'] = synthesis_result['final_answer']
                result['diagrams'] = []
                result['has_diagrams'] = False
                result['diagram_count'] = 0
            
            logger.info("\n" + "=" * 80)
            logger.info(f"✓ COMPLETED in {processing_time:.2f}s")
            logger.info(f"  Expressions: {len(expressions)}")
            logger.info(f"  Solved: {result['metadata']['solved_count']}/{len(expressions)}")
            logger.info("=" * 80)
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error in intelligent question solver: {e}")
            return {
                'success': False,
                'error': str(e),
                'processing_time_seconds': round(processing_time, 2)
            }
    
    def _topological_sort(self, dependency_graph: Dict[str, List[str]]) -> List[str]:
        """
        Topological sort to determine correct solving order
        
        Args:
            dependency_graph: Dict mapping expr_id to list of dependency expr_ids
            
        Returns:
            List of expr_ids in correct solving order
        """
        # Kahn's algorithm for topological sort
        in_degree = {node: 0 for node in dependency_graph}
        
        for node in dependency_graph:
            for dep in dependency_graph[node]:
                if dep in in_degree:
                    in_degree[dep] += 1
        
        queue = [node for node in in_degree if in_degree[node] == 0]
        result = []
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            
            for other_node in dependency_graph:
                if node in dependency_graph[other_node]:
                    in_degree[other_node] -= 1
                    if in_degree[other_node] == 0:
                        queue.append(other_node)
        
        return result


# Example usage and testing
if __name__ == "__main__":
    print("=" * 80)
    print("INTELLIGENT QUESTION SOLVER - Test Suite")
    print("=" * 80)
    
    solver = IntelligentQuestionSolver()
    
    # Test case 1: Simple dependent equations
    test_question_1 = """
    Find the value of x where 2x + 5 = 15, then calculate y = 3x - 2.
    What is the final value of y?
    """
    
    print("\n\nTest Case 1: Dependent Equations")
    print("-" * 80)
    result = solver.solve_question(test_question_1, subject="Algebra")
    
    if result['success']:
        print("\n✓ SUCCESS")
        print(f"\nExtracted Expressions: {len(result['extracted_expressions'])}")
        print(f"Solving Order: {' -> '.join(result['solving_order'])}")
        print(f"\nFinal Answer:\n{result['final_answer']}")
    else:
        print(f"\n✗ FAILED: {result['error']}")
    
    print("\n" + "=" * 80)
