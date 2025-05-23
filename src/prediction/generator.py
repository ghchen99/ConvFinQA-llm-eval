"""Prediction generation for financial QA."""

import json
from typing import Dict, Any, List
from src.api.azure_client import azure_client
from src.data.formatter import format_financial_context, format_conversation_history
from src.utils.text_utils import extract_json_from_text, parse_program_answer_from_text
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


class PredictionGenerator:
    """Handles prediction generation for financial QA questions."""
    
    def __init__(self):
        """Initialize the prediction generator."""
        self.client = azure_client
    
    def generate_prediction(
        self,
        financial_report: Dict[str, Any],
        conversation_history: List[Dict],
        current_question: str
    ) -> Dict[str, Any]:
        """Generate prediction for a single question.
        
        Args:
            financial_report: Financial report data
            conversation_history: Previous conversation turns
            current_question: Current question to answer
            
        Returns:
            Dictionary containing predicted_program and predicted_answer
        """
        logger.info(f"Generating prediction for question: '{current_question}'")
        logger.debug(f"Conversation history length: {len(conversation_history)}")
        
        try:
            # Format the context
            context = format_financial_context(financial_report)
            history_text = format_conversation_history(conversation_history)
            
            # Create the user message
            user_message = self._create_user_message(context, history_text, current_question)
            logger.debug(f"User message length: {len(user_message)} characters")
            
            # Get system prompt
            system_prompt = self.client.get_system_prompt()
            
            # Create messages
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            # Get response from Azure OpenAI
            response_text = self.client.create_chat_completion(messages)
            
            # Parse the response
            prediction = self._parse_response(response_text)
            
            logger.info(f"Successfully generated prediction: {prediction}")
            return prediction
            
        except Exception as e:
            logger.error(f"Error generating prediction: {e}", exc_info=True)
            return {
                "predicted_program": "",
                "predicted_answer": 0.0
            }
    
    def _create_user_message(
        self,
        context: str,
        history_text: str,
        current_question: str
    ) -> str:
        """Create the user message for the API call.
        
        Args:
            context: Formatted financial context
            history_text: Formatted conversation history
            current_question: Current question
            
        Returns:
            Formatted user message
        """
        return f"""{context}
{history_text}
CURRENT QUESTION: {current_question}

Please provide:
1. A "program" showing the calculation steps or direct lookup
2. A numerical "answer"

Respond in this exact JSON format:
{{
    "program": "your_program_here",
    "answer": your_numerical_answer_here
}}"""
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the API response to extract program and answer.
        
        Args:
            response_text: Raw response from the API
            
        Returns:
            Dictionary with predicted_program and predicted_answer
        """
        # Try to extract JSON from response
        try:
            json_str = extract_json_from_text(response_text)
            if json_str:
                result = json.loads(json_str)
                prediction = {
                    "predicted_program": result.get("program", ""),
                    "predicted_answer": float(result.get("answer", 0.0))
                }
                logger.info(f"Successfully parsed JSON response: {prediction}")
                return prediction
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}")
        
        # Fallback: try to extract program and answer from text
        logger.info("Attempting fallback parsing")
        program, answer = parse_program_answer_from_text(response_text)
        
        prediction = {
            "predicted_program": program,
            "predicted_answer": answer
        }
        logger.info(f"Fallback parsing result: {prediction}")
        return prediction


# Global generator instance
prediction_generator = PredictionGenerator()