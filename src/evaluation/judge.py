# src/evaluation/judge.py
"""LLM-based evaluation judge."""

import json
from typing import Dict, Any
from src.api.azure_client import azure_client
from src.evaluation.models import EvaluationResult
from src.evaluation.prompts import EvaluationPrompts
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class LLMJudge:
    """LLM-based evaluation of financial calculation predictions."""
    
    def __init__(self):
        """Initialize the LLM judge."""
        self.client = azure_client
        self.prompts = EvaluationPrompts()
    
    def evaluate_prediction(
        self, 
        item: Dict[str, Any], 
        conversation_idx: int
    ) -> EvaluationResult:
        """Evaluate a single prediction using the LLM judge."""
        try:
            # Extract conversation data
            conv_item = item['conversation'][conversation_idx]
            question = conv_item['question']
            expected_answer = float(conv_item['expected_answer'])
            predicted_answer = float(conv_item['predicted_answer'])
            expected_program = conv_item.get('expected_program', '')
            predicted_program = conv_item.get('predicted_program', '')
            
            # Create evaluation prompt
            prompt = self.prompts.create_evaluation_prompt(
                question, expected_answer, predicted_answer, 
                expected_program, predicted_program
            )
            
            # Get LLM evaluation
            messages = [
                {"role": "system", "content": self.prompts.get_system_prompt()},
                {"role": "user", "content": prompt}
            ]
            
            eval_data = self.client.create_chat_completion(
                messages, 
                temperature=0.1, 
                json=True,
            )
            
            # Handle string response if needed
            if isinstance(eval_data, str):
                eval_data = json.loads(eval_data)
            
            return EvaluationResult(
                question_id=f"{item['id']}-{conversation_idx}",
                question=question,
                expected_answer=expected_answer,
                predicted_answer=predicted_answer,
                expected_program=expected_program,
                predicted_program=predicted_program,
                answer_correct=eval_data.get('answer_correct', False),
                program_correct=eval_data.get('program_correct', False),
                reasoning=eval_data.get('reasoning', '')
            )
                
        except Exception as e:
            logger.error(f"Error evaluating prediction: {e}")
            return self._create_error_result(item, conversation_idx, str(e))
    
    def _create_error_result(
        self, 
        item: Dict[str, Any], 
        conversation_idx: int, 
        error_msg: str
    ) -> EvaluationResult:
        """Create an error result when evaluation fails."""
        conv_item = item.get('conversation', [{}])[conversation_idx] if conversation_idx < len(item.get('conversation', [])) else {}
        
        return EvaluationResult(
            question_id=f"{item.get('id', 'unknown')}-{conversation_idx}",
            question=conv_item.get('question', 'unknown'),
            expected_answer=conv_item.get('expected_answer', 0),
            predicted_answer=conv_item.get('predicted_answer', 0),
            expected_program=conv_item.get('expected_program', ''),
            predicted_program=conv_item.get('predicted_program', ''),
            answer_correct=False,
            program_correct=False,
            reasoning="Evaluation failed due to error",
            error=error_msg
        )
