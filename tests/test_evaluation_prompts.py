"""Tests for src/evaluation/prompts.py"""

import pytest
from src.evaluation.prompts import EvaluationPrompts


class TestEvaluationPrompts:
    """Test cases for EvaluationPrompts class."""
    
    def test_create_evaluation_prompt_basic(self):
        """Test creating basic evaluation prompt."""
        prompt = EvaluationPrompts.create_evaluation_prompt(
            question="What is the revenue?",
            expected_answer=100000.0,
            predicted_answer=100000.0,
            expected_program="100000",
            predicted_program="100000"
        )
        
        assert isinstance(prompt, str)
        assert "What is the revenue?" in prompt
        assert "100000.0" in prompt
        assert "100000" in prompt
        assert "answer_correct" in prompt
        assert "program_correct" in prompt
        assert "reasoning" in prompt
    
    def test_create_evaluation_prompt_with_calculations(self):
        """Test creating evaluation prompt with calculations."""
        prompt = EvaluationPrompts.create_evaluation_prompt(
            question="What is the profit margin?",
            expected_answer=0.25,
            predicted_answer=25.0,
            expected_program="divide(profit, revenue)",
            predicted_program="multiply(divide(profit, revenue), 100)"
        )
        
        assert "What is the profit margin?" in prompt
        assert "0.25" in prompt
        assert "25.0" in prompt
        assert "divide(profit, revenue)" in prompt
        assert "multiply(divide(profit, revenue), 100)" in prompt
        assert "percentage formats" in prompt
        assert "0.14 = 14%" in prompt
    
    def test_create_evaluation_prompt_with_different_formats(self):
        """Test prompt handles different answer formats."""
        prompt = EvaluationPrompts.create_evaluation_prompt(
            question="Calculate the ratio",
            expected_answer=0.14,
            predicted_answer=14.0,
            expected_program="divide(28, 200)",
            predicted_program="multiply(divide(28, 200), 100)"
        )
        
        # Should mention format equivalence
        assert "different formats" in prompt or "equivalent" in prompt
        assert "0.14 and 14.0" in prompt
        assert "14%" in prompt
    
    def test_create_evaluation_prompt_fields_present(self):
        """Test that all required fields are present in the prompt."""
        prompt = EvaluationPrompts.create_evaluation_prompt(
            question="Test question",
            expected_answer=42.0,
            predicted_answer=42.5,
            expected_program="test_program",
            predicted_program="predicted_program"
        )
        
        # Check all input values are included
        assert "Test question" in prompt
        assert "42.0" in prompt
        assert "42.5" in prompt
        assert "test_program" in prompt
        assert "predicted_program" in prompt
        
        # Check expected response format is specified
        assert "answer_correct: true/false" in prompt
        assert "program_correct: true/false" in prompt
        assert "reasoning: Brief explanation" in prompt
    
    def test_create_evaluation_prompt_instructions(self):
        """Test that prompt contains proper evaluation instructions."""
        prompt = EvaluationPrompts.create_evaluation_prompt(
            question="Sample question",
            expected_answer=1.0,
            predicted_answer=1.0,
            expected_program="sample",
            predicted_program="sample"
        )
        
        # Check evaluation criteria are mentioned
        assert "predicted answer correct" in prompt
        assert "predicted program correct" in prompt
        assert "functionally equivalent" in prompt
        assert "decimal vs percentage" in prompt
    
    def test_get_system_prompt(self):
        """Test getting system prompt."""
        system_prompt = EvaluationPrompts.get_system_prompt()
        
        assert isinstance(system_prompt, str)
        assert len(system_prompt) > 0
        assert "financial analyst" in system_prompt.lower()
        assert "JSON" in system_prompt
    
    def test_system_prompt_content(self):
        """Test system prompt contains expected content."""
        system_prompt = EvaluationPrompts.get_system_prompt()
        
        # Should be concise and focused on JSON response
        assert "financial analyst" in system_prompt.lower()
        assert "valid JSON" in system_prompt
        # Should be relatively short for a system prompt
        assert len(system_prompt) < 200
    
    def test_create_evaluation_prompt_edge_cases(self):
        """Test evaluation prompt with edge case values."""
        # Test with zero values
        prompt = EvaluationPrompts.create_evaluation_prompt(
            question="What is zero?",
            expected_answer=0.0,
            predicted_answer=0.0,
            expected_program="0",
            predicted_program="zero()"
        )
        
        assert "0.0" in prompt
        assert "zero()" in prompt
        
        # Test with negative values
        prompt2 = EvaluationPrompts.create_evaluation_prompt(
            question="What is the loss?",
            expected_answer=-1000.0,
            predicted_answer=-1000.0,
            expected_program="subtract(0, 1000)",
            predicted_program="-1000"
        )
        
        assert "-1000.0" in prompt2
        assert "subtract(0, 1000)" in prompt2
    
    def test_create_evaluation_prompt_empty_programs(self):
        """Test evaluation prompt with empty program strings."""
        prompt = EvaluationPrompts.create_evaluation_prompt(
            question="Simple lookup",
            expected_answer=500.0,
            predicted_answer=500.0,
            expected_program="",
            predicted_program=""
        )
        
        assert "Simple lookup" in prompt
        assert "500.0" in prompt
        # Empty strings should still be included in the prompt structure
        assert "Expected Program:" in prompt
        assert "Predicted Program:" in prompt
    
    def test_create_evaluation_prompt_long_question(self):
        """Test evaluation prompt with long question text."""
        long_question = (
            "What is the year-over-year percentage change in net income "
            "from continuing operations, excluding extraordinary items and "
            "accounting for currency exchange rate fluctuations?"
        )
        
        prompt = EvaluationPrompts.create_evaluation_prompt(
            question=long_question,
            expected_answer=12.5,
            predicted_answer=12.5,
            expected_program="complex_calculation()",
            predicted_program="complex_calculation()"
        )
        
        assert long_question in prompt
        assert "12.5" in prompt
        assert "complex_calculation()" in prompt
    
    def test_static_methods(self):
        """Test that prompt methods are static and can be called without instance."""
        # Should be able to call without creating instance
        prompt = EvaluationPrompts.create_evaluation_prompt(
            "test", 1.0, 1.0, "test", "test"
        )
        assert isinstance(prompt, str)
        
        system_prompt = EvaluationPrompts.get_system_prompt()
        assert isinstance(system_prompt, str)
        
        # Should also work with instance
        prompts = EvaluationPrompts()
        prompt2 = prompts.create_evaluation_prompt(
            "test", 1.0, 1.0, "test", "test"
        )
        system_prompt2 = prompts.get_system_prompt()
        
        # Results should be the same
        assert prompt == prompt2
        assert system_prompt == system_prompt2