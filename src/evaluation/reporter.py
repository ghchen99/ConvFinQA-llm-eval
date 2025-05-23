# src/evaluation/reporter.py
"""Evaluation reporting and output generation."""

import json
import os
from datetime import datetime
from typing import List
from src.evaluation.models import EvaluationResult, EvaluationSummary
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class EvaluationReporter:
    """Handles evaluation reporting and output generation."""
    
    def save_results(
        self, 
        results: List[EvaluationResult], 
        summary: EvaluationSummary,
        output_dir: str
    ) -> str:
        """Save evaluation results to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Prepare results data
        results_data = {
            "timestamp": timestamp,
            "summary": {
                "total": summary.total,
                "answer_correct": summary.answer_correct,
                "program_correct": summary.program_correct,
                "both_correct": summary.both_correct,
                "answer_accuracy": summary.answer_accuracy,
                "program_accuracy": summary.program_accuracy,
                "overall_accuracy": summary.overall_accuracy
            },
            "results": [self._result_to_dict(r) for r in results]
        }
        
        # Save to file
        results_file = os.path.join(output_dir, f"evaluation_results_{timestamp}.json")
        with open(results_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        logger.info(f"Results saved to: {results_file}")
        return results_file
    
    def _result_to_dict(self, result: EvaluationResult) -> dict:
        """Convert EvaluationResult to dictionary."""
        return {
            "question_id": result.question_id,
            "question": result.question,
            "expected_answer": result.expected_answer,
            "predicted_answer": result.predicted_answer,
            "expected_program": result.expected_program,
            "predicted_program": result.predicted_program,
            "answer_correct": result.answer_correct,
            "program_correct": result.program_correct,
            "reasoning": result.reasoning,
            "error": result.error
        }
    
    def print_summary(self, summary: EvaluationSummary, results_file: str) -> None:
        """Print evaluation summary to console."""
        print("\n" + "="*50)
        print("EVALUATION SUMMARY")
        print("="*50)
        print(f"Total Questions: {summary.total}")
        print(f"Answer Accuracy: {summary.answer_correct}/{summary.total} ({summary.answer_accuracy:.1f}%)")
        print(f"Program Accuracy: {summary.program_correct}/{summary.total} ({summary.program_accuracy:.1f}%)")
        print(f"Both Correct: {summary.both_correct}/{summary.total} ({summary.overall_accuracy:.1f}%)")
        print(f"\nResults saved to: {results_file}")
        print("="*50)
    
    def generate_detailed_report(
        self, 
        results: List[EvaluationResult], 
        summary: EvaluationSummary,
        output_dir: str
    ) -> str:
        """Generate a detailed HTML report (optional enhancement)."""
        # This could be implemented later for better visualization
        pass