"""
AI Question Solver Client for Proxy Service
Integrates with the AI service (backend-ai) to solve questions intelligently

This module acts as a client to call the AI service which:
1. Uses Groq AI to extract mathematical expressions
2. Identifies dependencies between expressions
3. Solves expressions with Wolfram Alpha
4. Synthesizes comprehensive answers with Groq AI
"""

import os
import requests
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# AI Service Configuration
# In production, this would be the URL of the deployed AI service
AI_SERVICE_URL = os.getenv('AI_SERVICE_URL', 'http://localhost:8001')

# For development, we can import directly if AI module is available
try:
    import sys
    import os
    # Add ai directory to path
    ai_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ai')
    if os.path.exists(ai_path):
        sys.path.insert(0, ai_path)
        from intelligent_question_solver import IntelligentQuestionSolver
        AI_MODULE_AVAILABLE = True
        logger.info("AI module available for direct import")
    else:
        AI_MODULE_AVAILABLE = False
        logger.info("AI module not available - will use HTTP API")
except ImportError:
    AI_MODULE_AVAILABLE = False
    logger.info("AI module not available - will use HTTP API")


class AIQuestionSolverClient:
    """
    Client to interact with AI Question Solver service
    Can work in two modes:
    1. Direct import (development) - imports AI module directly
    2. HTTP API (production) - calls AI service via HTTP
    """
    
    def __init__(self, mode: str = 'auto'):
        """
        Initialize AI Question Solver Client
        
        Args:
            mode: 'auto', 'direct', or 'api'
                - auto: Use direct if available, otherwise API
                - direct: Force direct import (development)
                - api: Force HTTP API (production)
        """
        self.mode = mode
        self.solver = None
        
        if mode == 'direct' or (mode == 'auto' and AI_MODULE_AVAILABLE):
            try:
                self.solver = IntelligentQuestionSolver()
                self.mode = 'direct'
                logger.info("Using direct AI module import")
            except Exception as e:
                logger.warning(f"Failed to initialize direct AI module: {e}")
                self.mode = 'api'
        else:
            self.mode = 'api'
            logger.info(f"Using AI service API at {AI_SERVICE_URL}")
    
    def solve_question(self, question_text: str, subject: str = '') -> Dict[str, Any]:
        """
        Solve a question using the AI service
        
        Args:
            question_text: Original question text from OCR
            subject: Subject context (math, physics, chemistry, etc.)
            
        Returns:
            Complete solution with interlinked steps and explanations
        """
        if self.mode == 'direct':
            return self._solve_direct(question_text, subject)
        else:
            return self._solve_via_api(question_text, subject)
    
    def _solve_direct(self, question_text: str, subject: str) -> Dict[str, Any]:
        """Solve question using direct AI module import"""
        try:
            logger.info(f"Solving question directly (subject: {subject})")
            result = self.solver.solve_question(question_text, subject)
            return result
        except Exception as e:
            logger.error(f"Error in direct AI solving: {e}")
            return {
                'success': False,
                'error': f'AI solving error: {str(e)}',
                'mode': 'direct'
            }
    
    def _solve_via_api(self, question_text: str, subject: str) -> Dict[str, Any]:
        """Solve question using HTTP API to AI service"""
        try:
            url = f"{AI_SERVICE_URL}/api/solve-question"
            
            payload = {
                'question_text': question_text,
                'subject': subject
            }
            
            logger.info(f"Calling AI service API: {url}")
            response = requests.post(url, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                result['mode'] = 'api'
                return result
            else:
                error_msg = f"AI service error: {response.status_code}"
                logger.error(error_msg)
                return {
                    'success': False,
                    'error': error_msg,
                    'mode': 'api'
                }
        except requests.exceptions.Timeout:
            logger.error("AI service request timed out")
            return {
                'success': False,
                'error': 'AI service timeout',
                'mode': 'api'
            }
        except Exception as e:
            logger.error(f"Error calling AI service: {e}")
            return {
                'success': False,
                'error': f'AI service error: {str(e)}',
                'mode': 'api'
            }


def solve_question_with_ai(question_text: str, subject: str = '') -> Dict[str, Any]:
    """
    Convenience function to solve a question using AI service
    
    Args:
        question_text: Original question text from OCR
        subject: Subject context
        
    Returns:
        Complete solution with interlinked steps
    """
    client = AIQuestionSolverClient(mode='auto')
    return client.solve_question(question_text, subject)


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 80)
    print("AI Question Solver Client - Test")
    print("=" * 80)
    
    # Test question
    test_question = """
    Find the value of x where 2x + 5 = 15, then calculate y = 3x - 2.
    What is the final value of y?
    """
    
    print(f"\nQuestion: {test_question.strip()}")
    print("\nSolving...")
    
    result = solve_question_with_ai(test_question, subject="Algebra")
    
    if result.get('success'):
        print(f"\n✓ SUCCESS (mode: {result.get('mode', 'unknown')})")
        print(f"\nProcessing time: {result.get('processing_time_seconds', 0)}s")
        print(f"\nExtracted expressions: {len(result.get('extracted_expressions', []))}")
        print(f"Solving order: {' -> '.join(result.get('solving_order', []))}")
        print(f"\nFinal Answer:\n{result.get('final_answer', 'No answer')}")
    else:
        print(f"\n✗ FAILED: {result.get('error')}")
        print(f"Mode: {result.get('mode', 'unknown')}")
    
    print("\n" + "=" * 80)
