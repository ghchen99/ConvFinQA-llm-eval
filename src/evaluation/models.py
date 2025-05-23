# src/evaluation/models.py
"""Data models for evaluation results."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class EvaluationResult:
    """Result of a single prediction evaluation."""
    question_id: str
    question: str
    expected_answer: float
    predicted_answer: float
    expected_program: str
    predicted_program: str
    answer_correct: bool
    program_correct: bool
    reasoning: str
    error: Optional[str] = None


@dataclass
class EvaluationSummary:
    """Summary statistics for evaluation results."""
    total: int
    answer_correct: int
    program_correct: int
    both_correct: int
    answer_accuracy: float
    program_accuracy: float
    overall_accuracy: float

    @classmethod
    def from_results(cls, results: list[EvaluationResult]) -> 'EvaluationSummary':
        """Create summary from evaluation results."""
        total = len(results)
        answer_correct = sum(1 for r in results if r.answer_correct)
        program_correct = sum(1 for r in results if r.program_correct)
        both_correct = sum(1 for r in results if r.answer_correct and r.program_correct)
        
        return cls(
            total=total,
            answer_correct=answer_correct,
            program_correct=program_correct,
            both_correct=both_correct,
            answer_accuracy=round(answer_correct / total * 100, 2) if total > 0 else 0,
            program_accuracy=round(program_correct / total * 100, 2) if total > 0 else 0,
            overall_accuracy=round(both_correct / total * 100, 2) if total > 0 else 0
        )