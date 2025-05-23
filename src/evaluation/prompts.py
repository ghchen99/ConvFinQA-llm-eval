# src/evaluation/prompts.py
"""Prompt templates for LLM evaluation."""


class EvaluationPrompts:
    """Collection of prompts for LLM-based evaluation."""
    
    @staticmethod
    def create_evaluation_prompt(
        question: str, 
        expected_answer: float, 
        predicted_answer: float,
        expected_program: str, 
        predicted_program: str
    ) -> str:
        """Create evaluation prompt for the LLM judge."""
        return f"""Evaluate this financial calculation prediction:

Question: {question}
Expected Answer: {expected_answer}
Predicted Answer: {predicted_answer}
Expected Program: {expected_program}
Predicted Program: {predicted_program}

Determine:
1. Is the predicted answer correct? (Consider decimal vs percentage formats - e.g., 0.14 = 14%)
2. Is the predicted program correct? (Consider functionally equivalent calculations)

Important: Answers may be equivalent even if in different formats:
- 0.14 and 14.0 both represent 14%
- Programs may be equivalent with different percentage conversions

Respond with:
- answer_correct: true/false
- program_correct: true/false  
- reasoning: Brief explanation of why answers/programs are correct or incorrect, especially for format differences"""

    @staticmethod
    def get_system_prompt() -> str:
        """Get the system prompt for evaluation."""
        return "You are a financial analyst. Respond only with valid JSON."

