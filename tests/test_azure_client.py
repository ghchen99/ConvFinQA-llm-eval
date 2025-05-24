"""Tests for src/api/azure_client.py"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from openai import AzureOpenAI

from src.api.azure_client import AzureOpenAIClient, azure_client


class TestAzureOpenAIClient:
    """Test cases for AzureOpenAIClient class."""
    
    @patch('src.api.azure_client.config')
    @patch('src.api.azure_client.AzureOpenAI')
    def test_init_success(self, mock_azure_openai, mock_config):
        """Test successful initialization."""
        # Mock config
        mock_config.azure_openai.validate.return_value = None
        mock_config.azure_openai.api_key = 'test-key'
        mock_config.azure_openai.endpoint = 'https://test.openai.azure.com'
        mock_config.azure_openai.api_version = '2024-02-01'
        mock_config.azure_openai.deployment_name = 'test-deployment'
        
        # Create client
        client = AzureOpenAIClient()
        
        # Verify initialization
        mock_config.azure_openai.validate.assert_called_once()
        mock_azure_openai.assert_called_once_with(
            api_key='test-key',
            azure_endpoint='https://test.openai.azure.com',
            api_version='2024-02-01'
        )
        assert client.client == mock_azure_openai.return_value
    
    @patch('src.api.azure_client.config')
    def test_init_validation_failure(self, mock_config):
        """Test initialization with validation failure."""
        mock_config.azure_openai.validate.side_effect = ValueError("Missing API key")
        
        with pytest.raises(ValueError, match="Missing API key"):
            AzureOpenAIClient()
    
    @patch('src.api.azure_client.config')
    @patch('src.api.azure_client.AzureOpenAI')
    def test_create_chat_completion_success(self, mock_azure_openai, mock_config):
        """Test successful chat completion."""
        # Setup mocks
        mock_config.azure_openai.validate.return_value = None
        mock_config.azure_openai.deployment_name = 'test-deployment'
        mock_config.max_tokens = 1000
        mock_config.temperature = 0.1
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"answer": 42}'
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_azure_openai.return_value = mock_client
        
        # Create client and make request
        client = AzureOpenAIClient()
        messages = [{"role": "user", "content": "test question"}]
        result = client.create_chat_completion(messages)
        
        # Verify result
        assert result == '{"answer": 42}'
        mock_client.chat.completions.create.assert_called_once_with(
            messages=messages,
            max_tokens=1000,
            temperature=0.1,
            model='test-deployment'
        )
    
    @patch('src.api.azure_client.config')
    @patch('src.api.azure_client.AzureOpenAI')
    def test_create_chat_completion_with_json_format(self, mock_azure_openai, mock_config):
        """Test chat completion with JSON response format."""
        # Setup mocks
        mock_config.azure_openai.validate.return_value = None
        mock_config.azure_openai.deployment_name = 'test-deployment'
        mock_config.max_tokens = 1000
        mock_config.temperature = 0.1
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"answer": 42}'
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_azure_openai.return_value = mock_client
        
        # Create client and make request with JSON format
        client = AzureOpenAIClient()
        messages = [{"role": "user", "content": "test question"}]
        result = client.create_chat_completion(messages, json=True)
        
        # Verify result and parameters
        assert result == '{"answer": 42}'
        mock_client.chat.completions.create.assert_called_once_with(
            messages=messages,
            max_tokens=1000,
            temperature=0.1,
            model='test-deployment',
            response_format={"type": "json_object"}
        )
    
    @patch('src.api.azure_client.config')
    @patch('src.api.azure_client.AzureOpenAI')
    def test_create_chat_completion_with_custom_params(self, mock_azure_openai, mock_config):
        """Test chat completion with custom parameters."""
        # Setup mocks
        mock_config.azure_openai.validate.return_value = None
        mock_config.azure_openai.deployment_name = 'test-deployment'
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = 'Custom response'
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_azure_openai.return_value = mock_client
        
        # Create client and make request with custom parameters
        client = AzureOpenAIClient()
        messages = [{"role": "user", "content": "test question"}]
        result = client.create_chat_completion(
            messages, 
            max_tokens=500, 
            temperature=0.5
        )
        
        # Verify custom parameters are used
        assert result == 'Custom response'
        mock_client.chat.completions.create.assert_called_once_with(
            messages=messages,
            max_tokens=500,
            temperature=0.5,
            model='test-deployment'
        )
    
    @patch('src.api.azure_client.config')
    @patch('src.api.azure_client.AzureOpenAI')
    def test_create_chat_completion_api_error(self, mock_azure_openai, mock_config):
        """Test chat completion with API error."""
        # Setup mocks
        mock_config.azure_openai.validate.return_value = None
        
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_azure_openai.return_value = mock_client
        
        # Create client and make request
        client = AzureOpenAIClient()
        messages = [{"role": "user", "content": "test question"}]
        
        with pytest.raises(Exception, match="API Error"):
            client.create_chat_completion(messages)
    
    @patch('src.api.azure_client.config')
    @patch('src.api.azure_client.AzureOpenAI')
    def test_get_system_prompt(self, mock_azure_openai, mock_config):
        """Test system prompt retrieval."""
        mock_config.azure_openai.validate.return_value = None
        
        client = AzureOpenAIClient()
        system_prompt = client.get_system_prompt()
        
        # Verify system prompt contains expected content
        assert isinstance(system_prompt, str)
        assert len(system_prompt) > 0
        assert "financial analysis expert" in system_prompt.lower()
        assert "program" in system_prompt.lower()
        assert "answer" in system_prompt.lower()
    
    @patch('src.api.azure_client.config')
    @patch('src.api.azure_client.AzureOpenAI')
    def test_response_content_stripping(self, mock_azure_openai, mock_config):
        """Test that response content is properly stripped."""
        # Setup mocks
        mock_config.azure_openai.validate.return_value = None
        mock_config.azure_openai.deployment_name = 'test-deployment'
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '  \n  response with whitespace  \n  '
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_azure_openai.return_value = mock_client
        
        # Create client and make request
        client = AzureOpenAIClient()
        messages = [{"role": "user", "content": "test"}]
        result = client.create_chat_completion(messages)
        
        # Verify response is stripped
        assert result == 'response with whitespace'


class TestGlobalAzureClient:
    """Test cases for global azure_client instance."""
    
    def test_global_client_exists(self):
        """Test that global azure_client instance exists."""
        assert azure_client is not None
        assert isinstance(azure_client, AzureOpenAIClient)
    
    @patch('src.api.azure_client.config')
    @patch('src.api.azure_client.AzureOpenAI')
    def test_global_client_methods(self, mock_azure_openai, mock_config):
        """Test that global client has expected methods."""
        mock_config.azure_openai.validate.return_value = None
        
        assert hasattr(azure_client, 'create_chat_completion')
        assert hasattr(azure_client, 'get_system_prompt')
        assert callable(azure_client.create_chat_completion)
        assert callable(azure_client.get_system_prompt)