"""Tests for src/evaluation/models.py"""

import pytest
from src.evaluation.models import EvaluationResult, EvaluationSummary


class TestEvaluationResult:
    """Test cases for EvaluationResult dataclass."""
    
    def test_evaluation_result_creation(self):
        """Test creating an EvaluationResult instance."""
        result = EvaluationResult(
            question_id="test-1",
            question="What is 2+2?",
            expected_answer=4.0,
            predicted_answer=4.0,
            expected_program="add(2, 2)",
            predicted_program="add(2, 2)",
            answer_correct=True,
            program_correct=True,
            reasoning="Both answer and program are correct"
        )
        
        assert result.question_id == "test-1"
        assert result.question == "What is 2+2?"
        assert result.expected_answer == 4.0
        assert result.predicted_answer == 4.0
        assert result.expected_program == "add(2, 2)"
        assert result.predicted_program == "add(2, 2)"
        assert result.answer_correct is True
        assert result.program_correct is True
        assert result.reasoning == "Both answer and program are correct"
        assert result.error is None
    
    def test_evaluation_result_with_error(self):
        """Test creating an EvaluationResult with error."""
        result = EvaluationResult(
            question_id="test-error",
            question="Failed question",
            expected_answer=0.0,
            predicted_answer=0.0,
            expected_program="",
            predicted_program="",
            answer_correct=False,
            program_correct=False,
            reasoning="Evaluation failed",
            error="API timeout"
        )
        
        assert result.error == "API timeout"
        assert result.answer_correct is False
        assert result.program_correct is False
    
    def test_evaluation_result_defaults(self):
        """Test EvaluationResult with default values."""
        result = EvaluationResult(
            question_id="test-default",
            question="Test question",
            expected_answer=1.0,
            predicted_answer=1.0,
            expected_program="test",
            predicted_program="test",
            answer_correct=True,
            program_correct=True,
            reasoning="Test"
        )
        
        # error should default to None
        assert result.error is None


class TestEvaluationSummary:
    """Test cases for EvaluationSummary dataclass."""
    
    def test_evaluation_summary_creation(self):
        """Test creating an EvaluationSummary instance."""
        summary = EvaluationSummary(
            total=10,
            answer_correct=8,
            program_correct=7,
            both_correct=6,
            answer_accuracy=80.0,
            program_accuracy=70.0,
            overall_accuracy=60.0
        )
        
        assert summary.total == 10
        assert summary.answer_correct == 8
        assert summary.program_correct == 7
        assert summary.both_correct == 6
        assert summary.answer_accuracy == 80.0
        assert summary.program_accuracy == 70.0
        assert summary.overall_accuracy == 60.0
    
    def test_from_results_all_correct(self):
        """Test creating summary from results where all are correct."""
        results = [
            EvaluationResult(
                question_id="1", question="Q1", expected_answer=1.0, predicted_answer=1.0,
                expected_program="1", predicted_program="1", answer_correct=True,
                program_correct=True, reasoning="Correct"
            ),
            EvaluationResult(
                question_id="2", question="Q2", expected_answer=2.0, predicted_answer=2.0,
                expected_program="2", predicted_program="2", answer_correct=True,
                program_correct=True, reasoning="Correct"
            ),
            EvaluationResult(
                question_id="3", question="Q3", expected_answer=3.0, predicted_answer=3.0,
                expected_program="3", predicted_program="3", answer_correct=True,
                program_correct=True, reasoning="Correct"
            )
        ]
        
        summary = EvaluationSummary.from_results(results)
        
        assert summary.total == 3
        assert summary.answer_correct == 3
        assert summary.program_correct == 3
        assert summary.both_correct == 3
        assert summary.answer_accuracy == 100.0
        assert summary.program_accuracy == 100.0
        assert summary.overall_accuracy == 100.0
    
    def test_from_results_mixed_correctness(self):
        """Test creating summary from results with mixed correctness."""
        results = [
            EvaluationResult(
                question_id="1", question="Q1", expected_answer=1.0, predicted_answer=1.0,
                expected_program="1", predicted_program="1", answer_correct=True,
                program_correct=True, reasoning="Both correct"
            ),
            EvaluationResult(
                question_id="2", question="Q2", expected_answer=2.0, predicted_answer=2.0,
                expected_program="2", predicted_program="wrong", answer_correct=True,
                program_correct=False, reasoning="Answer correct, program wrong"
            ),
            EvaluationResult(
                question_id="3", question="Q3", expected_answer=3.0, predicted_answer=4.0,
                expected_program="3", predicted_program="3", answer_correct=False,
                program_correct=True, reasoning="Answer wrong, program correct"
            ),
            EvaluationResult(
                question_id="4", question="Q4", expected_answer=4.0, predicted_answer=5.0,
                expected_program="4", predicted_program="wrong", answer_correct=False,
                program_correct=False, reasoning="Both wrong"
            )
        ]
        
        summary = EvaluationSummary.from_results(results)
        
        assert summary.total == 4
        assert summary.answer_correct == 2  # Q1, Q2
        assert summary.program_correct == 2  # Q1, Q3
        assert summary.both_correct == 1  # Q1 only
        assert summary.answer_accuracy == 50.0  # 2/4 * 100
        assert summary.program_accuracy == 50.0  # 2/4 * 100
        assert summary.overall_accuracy == 25.0  # 1/4 * 100
    
    def test_from_results_all_incorrect(self):
        """Test creating summary from results where all are incorrect."""
        results = [
            EvaluationResult(
                question_id="1", question="Q1", expected_answer=1.0, predicted_answer=2.0,
                expected_program="1", predicted_program="wrong", answer_correct=False,
                program_correct=False, reasoning="Wrong"
            ),
            EvaluationResult(
                question_id="2", question="Q2", expected_answer=2.0, predicted_answer=3.0,
                expected_program="2", predicted_program="wrong", answer_correct=False,
                program_correct=False, reasoning="Wrong"
            )
        ]
        
        summary = EvaluationSummary.from_results(results)
        
        assert summary.total == 2
        assert summary.answer_correct == 0
        assert summary.program_correct == 0
        assert summary.both_correct == 0
        assert summary.answer_accuracy == 0.0
        assert summary.program_accuracy == 0.0
        assert summary.overall_accuracy == 0.0
    
    def test_from_results_empty_list(self):
        """Test creating summary from empty results list."""
        results = []
        
        summary = EvaluationSummary.from_results(results)
        
        assert summary.total == 0
        assert summary.answer_correct == 0
        assert summary.program_correct == 0
        assert summary.both_correct == 0
        assert summary.answer_accuracy == 0.0
        assert summary.program_accuracy == 0.0
        assert summary.overall_accuracy == 0.0
    
    def test_from_results_accuracy_rounding(self):
        """Test that accuracy values are properly rounded."""
        # Create 3 results with 1 correct answer, 2 correct programs, 1 both correct
        results = [
            EvaluationResult(
                question_id="1", question="Q1", expected_answer=1.0, predicted_answer=1.0,
                expected_program="1", predicted_program="1", answer_correct=True,
                program_correct=True, reasoning="Correct"
            ),
            EvaluationResult(
                question_id="2", question="Q2", expected_answer=2.0, predicted_answer=3.0,
                expected_program="2", predicted_program="2", answer_correct=False,
                program_correct=True, reasoning="Program correct"
            ),
            EvaluationResult(
                question_id="3", question="Q3", expected_answer=3.0, predicted_answer=4.0,
                expected_program="3", predicted_program="wrong", answer_correct=False,
                program_correct=False, reasoning="Both wrong"
            )
        ]
        
        summary = EvaluationSummary.from_results(results)
        
        # 1/3 = 0.333... should round to 33.33
        assert summary.answer_accuracy == 33.33
        # 2/3 = 0.666... should round to 66.67
        assert summary.program_accuracy == 66.67
        # 1/3 = 0.333... should round to 33.33
        assert summary.overall_accuracy == 33.33
    
    def test_from_results_single_result(self):
        """Test creating summary from single result."""
        results = [
            EvaluationResult(
                question_id="1", question="Q1", expected_answer=1.0, predicted_answer=1.0,
                expected_program="1", predicted_program="wrong", answer_correct=True,
                program_correct=False, reasoning="Answer only correct"
            )
        ]
        
        summary = EvaluationSummary.from_results(results)
        
        assert summary.total == 1
        assert summary.answer_correct == 1
        assert summary.program_correct == 0
        assert summary.both_correct == 0
        assert summary.answer_accuracy == 100.0
        assert summary.program_accuracy == 0.0
        assert summary.overall_accuracy == 0.0