"""Tests for src/prediction/generator.py"""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock

from src.prediction.generator import PredictionGenerator, prediction_generator


class TestPredictionGenerator:
    """Test cases for PredictionGenerator class."""
    
    @patch('src.prediction.generator.azure_client')
    def test_init(self, mock_azure_client):
        """Test PredictionGenerator initialization."""
        generator = PredictionGenerator()
        assert generator.client == mock_azure_client
    
    @patch('src.prediction.generator.azure_client')
    @patch('src.prediction.generator.format_financial_context')
    @patch('src.prediction.generator.format_conversation_history')
    def test_generate_prediction_success(self, mock_format_history, mock_format_context, mock_azure_client):
        """Test successful prediction generation."""
        # Setup mocks
        mock_format_context.return_value = "Financial context"
        mock_format_history.return_value = "Conversation history"
        mock_azure_client.get_system_prompt.return_value = "System prompt"
        mock_azure_client.create_chat_completion.return_value = '{"program": "add(100, 200)", "answer": 300}'
        
        # Test data
        financial_report = {"table": [["Revenue", "300"]]}
        conversation_history = [{"question": "Previous question", "expected_answer": 100}]
        current_question = "What is the total?"
        
        generator = PredictionGenerator()
        result = generator.generate_prediction(financial_report, conversation_history, current_question)
        
        # Verify result
        assert result["predicted_program"] == "add(100, 200)"
        assert result["predicted_answer"] == 300.0
        
        # Verify mocks were called
        mock_format_context.assert_called_once_with(financial_report)
        mock_format_history.assert_called_once_with(conversation_history)
        mock_azure_client.create_chat_completion.assert_called_once()
    
    @patch('src.prediction.generator.azure_client')
    def test_generate_prediction_api_error(self, mock_azure_client):
        """Test prediction generation with API error."""
        # Setup mock to raise exception
        mock_azure_client.get_system_prompt.return_value = "System prompt"
        mock_azure_client.create_chat_completion.side_effect = Exception("API error")
        
        generator = PredictionGenerator()
        result = generator.generate_prediction({}, [], "Test question")
        
        # Should return default values on error
        assert result["predicted_program"] == ""
        assert result["predicted_answer"] == 0.0
    
    @patch('src.prediction.generator.azure_client')
    def test_generate_prediction_json_response(self, mock_azure_client):
        """Test prediction with valid JSON response."""
        mock_azure_client.get_system_prompt.return_value = "System prompt"
        mock_azure_client.create_chat_completion.return_value = '''
        {
            "program": "divide(500, 1000)",
            "answer": 0.5
        }
        '''
        
        generator = PredictionGenerator()
        result = generator.generate_prediction({}, [], "What is the ratio?")
        
        assert result["predicted_program"] == "divide(500, 1000)"
        assert result["predicted_answer"] == 0.5
    
    @patch('src.prediction.generator.azure_client')
    @patch('src.prediction.generator.parse_program_answer_from_text')
    def test_generate_prediction_fallback_parsing(self, mock_parse_fallback, mock_azure_client):
        """Test prediction with fallback parsing."""
        # Setup mocks
        mock_azure_client.get_system_prompt.return_value = "System prompt"
        mock_azure_client.create_chat_completion.return_value = "Invalid JSON response"
        mock_parse_fallback.return_value = ("fallback_program", 42.0)
        
        generator = PredictionGenerator()
        result = generator.generate_prediction({}, [], "Test question")
        
        # Should use fallback parsing
        assert result["predicted_program"] == "fallback_program"
        assert result["predicted_answer"] == 42.0
        mock_parse_fallback.assert_called_once_with("Invalid JSON response")
    
    def test_create_user_message(self):
        """Test user message creation."""
        generator = PredictionGenerator()
        
        context = "Financial data context"
        history_text = "Previous Q&A"
        current_question = "What is the revenue?"
        
        message = generator._create_user_message(context, history_text, current_question)
        
        assert "Financial data context" in message
        assert "Previous Q&A" in message
        assert "What is the revenue?" in message
        assert "JSON format" in message
        assert '"program"' in message
        assert '"answer"' in message
    
    def test_parse_response_valid_json(self):
        """Test parsing valid JSON response."""
        generator = PredictionGenerator()
        
        response = '{"program": "multiply(10, 5)", "answer": 50}'
        result = generator._parse_response(response)
        
        assert result["predicted_program"] == "multiply(10, 5)"
        assert result["predicted_answer"] == 50.0
    
    def test_parse_response_json_with_extra_text(self):
        """Test parsing JSON response with extra text."""
        generator = PredictionGenerator()
        
        response = '''
        Here is my analysis:
        {"program": "subtract(1000, 750)", "answer": 250}
        Hope this helps!
        '''
        result = generator._parse_response(response)
        
        assert result["predicted_program"] == "subtract(1000, 750)"
        assert result["predicted_answer"] == 250.0
    
    @patch('src.prediction.generator.parse_program_answer_from_text')
    def test_parse_response_invalid_json_fallback(self, mock_parse_fallback):
        """Test parsing response with invalid JSON using fallback."""
        mock_parse_fallback.return_value = ("extracted_program", 123.0)
        
        generator = PredictionGenerator()
        response = "This is not JSON at all"
        result = generator._parse_response(response)
        
        assert result["predicted_program"] == "extracted_program"
        assert result["predicted_answer"] == 123.0
        mock_parse_fallback.assert_called_once_with(response)
    
    def test_parse_response_missing_fields(self):
        """Test parsing JSON response with missing fields."""
        generator = PredictionGenerator()
        
        # Missing 'answer' field
        response = '{"program": "test_program"}'
        result = generator._parse_response(response)
        
        assert result["predicted_program"] == "test_program"
        assert result["predicted_answer"] == 0.0
        
        # Missing 'program' field
        response2 = '{"answer": 456}'
        result2 = generator._parse_response(response2)
        
        assert result2["predicted_program"] == ""
        assert result2["predicted_answer"] == 456.0
    
    def test_parse_response_empty_json(self):
        """Test parsing empty JSON response."""
        generator = PredictionGenerator()
        
        response = '{}'
        result = generator._parse_response(response)
        
        assert result["predicted_program"] == ""
        assert result["predicted_answer"] == 0.0
    
    @patch('src.prediction.generator.azure_client')
    def test_generate_prediction_with_complex_data(self, mock_azure_client):
        """Test prediction generation with complex input data."""
        mock_azure_client.get_system_prompt.return_value = "System prompt"
        mock_azure_client.create_chat_completion.return_value = '{"program": "complex_calc()", "answer": 12345.67}'
        
        # Complex financial report
        financial_report = {
            'pre_text': ['Company ABC', 'Q4 2023 Results'],
            'table': [
                ['Account', 'Amount'],
                ['Revenue', '1000000'],
                ['Expenses', '750000'],
                ['Net Income', '250000']
            ],
            'post_text': ['Note: All figures in USD']
        }
        
        # Complex conversation history
        conversation_history = [
            {
                'question': 'What was the total revenue?',
                'expected_program': '1000000',
                'expected_answer': 1000000.0
            },
            {
                'question': 'What is the profit margin?',
                'expected_program': 'divide(250000, 1000000)',
                'expected_answer': 0.25
            }
        ]
        
        current_question = "What is the revenue growth rate compared to last year?"
        
        generator = PredictionGenerator()
        result = generator.generate_prediction(financial_report, conversation_history, current_question)
        
        assert result["predicted_program"] == "complex_calc()"
        assert result["predicted_answer"] == 12345.67
    
    @patch('src.prediction.generator.azure_client')
    def test_generate_prediction_empty_inputs(self, mock_azure_client):
        """Test prediction generation with empty inputs."""
        mock_azure_client.get_system_prompt.return_value = "System prompt"
        mock_azure_client.create_chat_completion.return_value = '{"program": "", "answer": 0}'
        
        generator = PredictionGenerator()
        result = generator.generate_prediction({}, [], "")
        
        assert result["predicted_program"] == ""
        assert result["predicted_answer"] == 0.0


class TestGlobalPredictionGenerator:
    """Test cases for global prediction_generator instance."""
    
    def test_global_generator_exists(self):
        """Test that global prediction_generator instance exists."""
        assert prediction_generator is not None
        assert isinstance(prediction_generator, PredictionGenerator)
    
    def test_global_generator_methods(self):
        """Test that global generator has expected methods."""
        assert hasattr(prediction_generator, 'generate_prediction')
        assert callable(prediction_generator.generate_prediction)
        
        assert hasattr(prediction_generator, '_create_user_message')
        assert callable(prediction_generator._create_user_message)
        
        assert hasattr(prediction_generator, '_parse_response')
        assert callable(prediction_generator._parse_response)


class TestPredictionGeneratorIntegration:
    """Integration test cases for PredictionGenerator."""
    
    @patch('src.prediction.generator.azure_client')
    def test_full_prediction_flow(self, mock_azure_client):
        """Test full prediction generation flow."""
        # Setup mock responses
        mock_azure_client.get_system_prompt.return_value = "You are a financial expert."
        mock_azure_client.create_chat_completion.return_value = '''
        Based on the financial data provided:
        {
            "program": "add(revenue, other_income)",
            "answer": 105000
        }
        '''
        
        # Input data
        financial_report = {
            'table': [
                ['Item', 'Amount'],
                ['Revenue', '100000'],
                ['Other Income', '5000']
            ]
        }
        
        conversation_history = [
            {
                'question': 'What is the main revenue?',
                'expected_program': '100000',
                'expected_answer': 100000.0
            }
        ]
        
        current_question = "What is the total income including other sources?"
        
        # Generate prediction
        generator = PredictionGenerator()
        result = generator.generate_prediction(
            financial_report, 
            conversation_history, 
            current_question
        )
        
        # Verify result
        assert result["predicted_program"] == "add(revenue, other_income)"
        assert result["predicted_answer"] == 105000.0
        
        # Verify the API was called with proper message structure
        call_args = mock_azure_client.create_chat_completion.call_args
        messages = call_args[0][0]  # First positional argument
        
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        
        user_content = messages[1]["content"]
        assert "FINANCIAL REPORT CONTEXT:" in user_content
        assert "PREVIOUS CONVERSATION:" in user_content
        assert current_question in user_content