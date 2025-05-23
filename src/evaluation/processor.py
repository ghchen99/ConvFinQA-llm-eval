# src/evaluation/processor.py
"""Main evaluation processor."""

import json
import os
from typing import List, Dict, Any
from src.evaluation.judge import LLMJudge
from src.evaluation.models import EvaluationResult, EvaluationSummary
from src.evaluation.reporter import EvaluationReporter
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class EvaluationProcessor:
    """Main processor for evaluation tasks."""
    
    def __init__(self):
        """Initialize the evaluation processor."""
        self.judge = LLMJudge()
        self.reporter = EvaluationReporter()
    
    def load_predictions(self, input_file: str) -> List[Dict[str, Any]]:
        """Load predictions from JSON file."""
        try:
            with open(input_file, 'r') as f:
                predictions_data = json.load(f)
            logger.info(f"Loaded {len(predictions_data)} prediction items")
            return predictions_data
        except FileNotFoundError:
            logger.error(f"Predictions file not found: {input_file}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing predictions JSON: {e}")
            raise
    
    def evaluate_all_predictions(self, predictions_data: List[Dict[str, Any]]) -> List[EvaluationResult]:
        """Evaluate all predictions in the dataset."""
        all_results = []
        
        for item_idx, item in enumerate(predictions_data):
            logger.info(f"Processing item {item_idx + 1}/{len(predictions_data)}: {item.get('id', 'unknown')}")
            
            # Process each conversation in the item
            conversations = item.get('conversation', [])
            for conv_idx, _ in enumerate(conversations):
                logger.info(f"  Evaluating conversation {conv_idx + 1}/{len(conversations)}")
                
                result = self.judge.evaluate_prediction(item, conv_idx)
                all_results.append(result)
                
                # Log result
                self._log_evaluation_result(result)
        
        return all_results
    
    def _log_evaluation_result(self, result: EvaluationResult) -> None:
        """Log individual evaluation result."""
        answer_status = "✓" if result.answer_correct else "✗"
        program_status = "✓" if result.program_correct else "✗"
        logger.info(f"  Answer: {answer_status} | Program: {program_status}")
        logger.info(f"  Expected: {result.expected_answer} | Predicted: {result.predicted_answer}")
        if result.reasoning:
            logger.info(f"  Reasoning: {result.reasoning}")
    
    def process_evaluation(self, input_file: str, output_dir: str) -> EvaluationSummary:
        """Process complete evaluation pipeline."""
        logger.info("Starting LLM Judge evaluation")
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Load predictions
        predictions_data = self.load_predictions(input_file)
        
        # Evaluate all predictions
        all_results = self.evaluate_all_predictions(predictions_data)
        
        # Generate summary
        summary = EvaluationSummary.from_results(all_results)
        
        # Save results and generate report
        results_file = self.reporter.save_results(all_results, summary, output_dir)
        self.reporter.print_summary(summary, results_file)
        
        return summary