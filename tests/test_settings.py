"""Tests for config/settings.py"""

import os
import pytest
from unittest.mock import patch, MagicMock
import tempfile
import shutil

from config.settings import AzureOpenAIConfig, AppConfig, config


class TestAzureOpenAIConfig:
    """Test cases for AzureOpenAIConfig class."""
    
    def test_init_with_env_vars(self):
        """Test initialization with environment variables."""
        with patch.dict(os.environ, {
            'AZURE_OPENAI_API_KEY': 'test-key',
            'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
            'AZURE_OPENAI_API_VERSION': '2024-03-01',
            'AZURE_OPENAI_MODEL_NAME': 'gpt-4',
            'AZURE_OPENAI_DEPLOYMENT_NAME': 'test-deployment'
        }):
            config_obj = AzureOpenAIConfig()
            assert config_obj.api_key == 'test-key'
            assert config_obj.endpoint == 'https://test.openai.azure.com'
            assert config_obj.api_version == '2024-03-01'
            assert config_obj.model_name == 'gpt-4'
            assert config_obj.deployment_name == 'test-deployment'
    
    def test_init_with_default_api_version(self):
        """Test initialization with default API version."""
        with patch.dict(os.environ, {
            'AZURE_OPENAI_API_KEY': 'test-key',
            'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
            'AZURE_OPENAI_DEPLOYMENT_NAME': 'test-deployment'
        }, clear=True):
            config_obj = AzureOpenAIConfig()
            assert config_obj.api_version == '2024-02-01'
    
    def test_validate_success(self):
        """Test successful validation."""
        with patch.dict(os.environ, {
            'AZURE_OPENAI_API_KEY': 'test-key',
            'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
            'AZURE_OPENAI_DEPLOYMENT_NAME': 'test-deployment'
        }):
            config_obj = AzureOpenAIConfig()
            config_obj.validate()  # Should not raise
    
    def test_validate_missing_api_key(self):
        """Test validation with missing API key."""
        with patch.dict(os.environ, {
            'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
            'AZURE_OPENAI_DEPLOYMENT_NAME': 'test-deployment'
        }, clear=True):
            config_obj = AzureOpenAIConfig()
            with pytest.raises(ValueError, match="Missing required Azure OpenAI configuration"):
                config_obj.validate()
    
    def test_validate_missing_endpoint(self):
        """Test validation with missing endpoint."""
        with patch.dict(os.environ, {
            'AZURE_OPENAI_API_KEY': 'test-key',
            'AZURE_OPENAI_DEPLOYMENT_NAME': 'test-deployment'
        }, clear=True):
            config_obj = AzureOpenAIConfig()
            with pytest.raises(ValueError, match="Missing required Azure OpenAI configuration"):
                config_obj.validate()
    
    def test_validate_missing_deployment_name(self):
        """Test validation with missing deployment name."""
        with patch.dict(os.environ, {
            'AZURE_OPENAI_API_KEY': 'test-key',
            'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com'
        }, clear=True):
            config_obj = AzureOpenAIConfig()
            with pytest.raises(ValueError, match="Missing required Azure OpenAI configuration"):
                config_obj.validate()


class TestAppConfig:
    """Test cases for AppConfig class."""
    
    def test_init_default_values(self):
        """Test initialization with default values."""
        with patch.dict(os.environ, {
            'AZURE_OPENAI_API_KEY': 'test-key',
            'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
            'AZURE_OPENAI_DEPLOYMENT_NAME': 'test-deployment'
        }):
            config_obj = AppConfig()
            
            assert config_obj.data_dir == "data"
            assert config_obj.input_dir == os.path.join("data", "input")
            assert config_obj.output_dir == os.path.join("data", "output")
            assert config_obj.logs_dir == "logs"
            assert config_obj.max_tokens == 1000
            assert config_obj.temperature == 0.1
            assert config_obj.batch_size == 10
            assert config_obj.retry_attempts == 3
            assert config_obj.retry_delay == 1.0
    
    def test_default_file_paths(self):
        """Test default file paths."""
        with patch.dict(os.environ, {
            'AZURE_OPENAI_API_KEY': 'test-key',
            'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
            'AZURE_OPENAI_DEPLOYMENT_NAME': 'test-deployment'
        }):
            config_obj = AppConfig()
            
            expected_input = os.path.join("data", "input", "processed_train.json")
            expected_output = os.path.join("data", "output", "predictions.json")
            
            assert config_obj.default_input_file == expected_input
            assert config_obj.default_output_file == expected_output
    
    @patch('os.makedirs')
    def test_ensure_directories(self, mock_makedirs):
        """Test directory creation."""
        with patch.dict(os.environ, {
            'AZURE_OPENAI_API_KEY': 'test-key',
            'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
            'AZURE_OPENAI_DEPLOYMENT_NAME': 'test-deployment'
        }):
            config_obj = AppConfig()
            config_obj.ensure_directories()
            
            expected_dirs = ["data", "data/input", "data/output", "logs"]
            for expected_dir in expected_dirs:
                mock_makedirs.assert_any_call(expected_dir, exist_ok=True)
    
    def test_ensure_directories_integration(self):
        """Test actual directory creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(os.environ, {
                'AZURE_OPENAI_API_KEY': 'test-key',
                'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com',
                'AZURE_OPENAI_DEPLOYMENT_NAME': 'test-deployment'
            }):
                config_obj = AppConfig()
                # Override paths to use temp directory
                config_obj.data_dir = os.path.join(temp_dir, "data")
                config_obj.input_dir = os.path.join(temp_dir, "data", "input")
                config_obj.output_dir = os.path.join(temp_dir, "data", "output")
                config_obj.logs_dir = os.path.join(temp_dir, "logs")
                
                config_obj.ensure_directories()
                
                assert os.path.exists(config_obj.data_dir)
                assert os.path.exists(config_obj.input_dir)
                assert os.path.exists(config_obj.output_dir)
                assert os.path.exists(config_obj.logs_dir)


class TestGlobalConfig:
    """Test cases for global config instance."""
    
    def test_global_config_exists(self):
        """Test that global config instance exists."""
        assert config is not None
        assert isinstance(config, AppConfig)
    
    def test_global_config_azure_openai(self):
        """Test that global config has azure_openai attribute."""
        assert hasattr(config, 'azure_openai')
        assert isinstance(config.azure_openai, AzureOpenAIConfig)