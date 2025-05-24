"""Tests for src/utils/validation.py"""

import os
import json
import pytest
import tempfile
from unittest.mock import patch, mock_open, MagicMock

from src.utils.validation import (
    validate_environment,
    validate_input_file,
    validate_data_structure,
    validate_dataset
)


class TestValidateEnvironment:
    """Test cases for validate_environment function."""
    
    @patch('src.utils.validation.config')
    def test_validate_environment_success(self, mock_config):
        """Test successful environment validation."""
        mock_config.azure_openai.validate.return_value = None
        
        # Should not raise any exception
        validate_environment()
        mock_config.azure_openai.validate.assert_called_once()
    
    @patch('src.utils.validation.config')
    def test_validate_environment_failure(self, mock_config):
        """Test environment validation failure."""
        mock_config.azure_openai.validate.side_effect = ValueError("Missing API key")
        
        with pytest.raises(ValueError, match="Missing API key"):
            validate_environment()


class TestValidateInputFile:
    """Test cases for validate_input_file function."""
    
    def test_validate_input_file_not_found(self):
        """Test validation with non-existent file."""
        with pytest.raises(FileNotFoundError):
            validate_input_file("non_existent_file.json")
    
    def test_validate_input_file_success(self):
        """Test successful file validation."""
        test_data = [
            {"id": "1", "data": "test1"},
            {"id": "2", "data": "test2"}
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_file = f.name
        
        try:
            # Should not raise any exception
            validate_input_file(temp_file)
        finally:
            os.unlink(temp_file)
    
    def test_validate_input_file_invalid_json(self):
        """Test validation with invalid JSON."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json content")
            temp_file = f.name
        
        try:
            with pytest.raises(json.JSONDecodeError):
                validate_input_file(temp_file)
        finally:
            os.unlink(temp_file)
    
    def test_validate_input_file_not_array(self):
        """Test validation with JSON that's not an array."""
        test_data = {"not": "an array"}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_file = f.name
        
        try:
            with pytest.raises(ValueError, match="must contain a JSON array"):
                validate_input_file(temp_file)
        finally:
            os.unlink(temp_file)
    
    def test_validate_input_file_empty_array(self):
        """Test validation with empty array."""
        test_data = []
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_file = f.name
        
        try:
            with pytest.raises(ValueError, match="contains no data"):
                validate_input_file(temp_file)
        finally:
            os.unlink(temp_file)
    
    def test_validate_input_file_encoding(self):
        """Test validation with UTF-8 encoded file."""
        test_data = [{"id": "1", "text": "测试数据"}]  # Chinese characters
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False)
            temp_file = f.name
        
        try:
            # Should handle UTF-8 properly
            validate_input_file(temp_file)
        finally:
            os.unlink(temp_file)


class TestValidateDataStructure:
    """Test cases for validate_data_structure function."""
    
    def test_validate_complete_structure(self):
        """Test validation of complete, valid data structure."""
        item = {
            'id': 'test-1',
            'financial_report': {
                'table': [['Header1', 'Header2'], ['Value1', 'Value2']],
                'pre_text': ['Some text'],
                'post_text': ['More text']
            },
            'conversation': [
                {
                    'question': 'What is the revenue?',
                    'expected_answer': 1000,
                    'expected_program': '1000'
                }
            ]
        }
        
        errors = validate_data_structure(item, 0)
        assert len(errors) == 0
    
    def test_validate_missing_required_fields(self):
        """Test validation with missing required fields."""
        item = {
            'financial_report': {},
            # Missing 'id' and 'conversation'
        }
        
        errors = validate_data_structure(item, 0)
        
        assert len(errors) == 2
        assert any("Missing required field 'id'" in error for error in errors)
        assert any("Missing required field 'conversation'" in error for error in errors)
    
    def test_validate_invalid_financial_report(self):
        """Test validation with invalid financial_report structure."""
        item = {
            'id': 'test-1',
            'financial_report': "not a dict",  # Should be dict
            'conversation': []
        }
        
        errors = validate_data_structure(item, 1)
        
        assert len(errors) == 1
        assert "Item 1: 'financial_report' must be a dictionary" in errors[0]
    
    def test_validate_invalid_conversation(self):
        """Test validation with invalid conversation structure."""
        item = {
            'id': 'test-1',
            'financial_report': {},
            'conversation': "not a list"  # Should be list
        }
        
        errors = validate_data_structure(item, 2)
        
        assert len(errors) == 1
        assert "Item 2: 'conversation' must be a list" in errors[0]
    
    def test_validate_invalid_conversation_turns(self):
        """Test validation with invalid conversation turn structure."""
        item = {
            'id': 'test-1',
            'financial_report': {},
            'conversation': [
                "not a dict",  # Should be dict
                {},  # Missing 'question'
                {'question': 'Valid question'}  # Valid
            ]
        }
        
        errors = validate_data_structure(item, 3)
        
        assert len(errors) == 2
        assert "Item 3, Turn 0: Turn must be a dictionary" in errors[0]
        assert "Item 3, Turn 1: Missing 'question' field" in errors[1]
    
    def test_validate_empty_item(self):
        """Test validation with completely empty item."""
        item = {}
        
        errors = validate_data_structure(item, 0)
        
        assert len(errors) == 3  # Missing all required fields
        required_fields = ['id', 'financial_report', 'conversation']
        for field in required_fields:
            assert any(f"Missing required field '{field}'" in error for error in errors)
    
    def test_validate_minimal_valid_structure(self):
        """Test validation with minimal valid structure."""
        item = {
            'id': 'minimal',
            'financial_report': {},
            'conversation': []
        }
        
        errors = validate_data_structure(item, 0)
        assert len(errors) == 0


class TestValidateDataset:
    """Test cases for validate_dataset function."""
    
    def test_validate_dataset_success(self):
        """Test successful dataset validation."""
        data = [
            {
                'id': 'item-1',
                'financial_report': {'table': []},
                'conversation': [{'question': 'Q1?'}]
            },
            {
                'id': 'item-2',
                'financial_report': {},
                'conversation': [
                    {'question': 'Q2a?'},
                    {'question': 'Q2b?'}
                ]
            }
        ]
        
        result = validate_dataset(data)
        assert result is True
    
    def test_validate_dataset_with_errors(self):
        """Test dataset validation with errors."""
        data = [
            {
                'id': 'valid-item',
                'financial_report': {},
                'conversation': [{'question': 'Valid?'}]
            },
            {
                # Missing required fields
                'financial_report': {}
            },
            "not a dict"  # Invalid item type
        ]
        
        result = validate_dataset(data)
        assert result is False
    
    def test_validate_empty_dataset(self):
        """Test validation of empty dataset."""
        data = []
        
        result = validate_dataset(data)
        assert result is True  # Empty dataset is technically valid
    
    def test_validate_dataset_mixed_validity(self):
        """Test dataset with mix of valid and invalid items."""
        data = [
            {
                'id': 'valid',
                'financial_report': {},
                'conversation': [{'question': 'Valid?'}]
            },
            {
                'id': 'invalid-conversation',
                'financial_report': {},
                'conversation': "not a list"
            },
            {
                'financial_report': {},
                'conversation': []
                # Missing 'id'
            }
        ]
        
        result = validate_dataset(data)
        assert result is False
    
    def test_validate_dataset_non_dict_items(self):
        """Test dataset with non-dictionary items."""
        data = [
            {'id': 'valid', 'financial_report': {}, 'conversation': []},
            "string item",
            123,
            None,
            []
        ]
        
        result = validate_dataset(data)
        assert result is False
    
    @patch('src.utils.validation.logger')
    def test_validate_dataset_logging(self, mock_logger):
        """Test that validation errors are properly logged."""
        data = [
            "not a dict",
            {'financial_report': {}}  # Missing id and conversation
        ]
        
        result = validate_dataset(data)
        
        assert result is False
        # Should log validation failure and errors
        mock_logger.error.assert_called()
        
        # Check that error messages were logged
        logged_calls = [call.args[0] for call in mock_logger.error.call_args_list]
        assert any("Dataset validation failed" in call for call in logged_calls)
    
    def test_validate_dataset_error_limit(self):
        """Test that error logging is limited to prevent spam."""
        # Create dataset with many errors
        data = ["not a dict"] * 15  # 15 invalid items
        
        with patch('src.utils.validation.logger') as mock_logger:
            result = validate_dataset(data)
            
            assert result is False
            
            # Should log "Dataset validation failed" plus up to 10 individual errors
            # plus potentially a "... and X more errors" message
            error_calls = mock_logger.error.call_args_list
            assert len(error_calls) <= 12  # 1 main + 10 individual + 1 summary
    
    def test_validate_large_dataset(self):
        """Test validation of larger dataset."""
        # Create 100 valid items
        data = []
        for i in range(100):
            data.append({
                'id': f'item-{i}',
                'financial_report': {'data': f'report-{i}'},
                'conversation': [{'question': f'Question {i}?'}]
            })
        
        result = validate_dataset(data)
        assert result is True
    
    def test_validate_dataset_complex_structures(self):
        """Test validation of dataset with complex nested structures."""
        data = [
            {
                'id': 'complex-item',
                'financial_report': {
                    'table': [
                        ['Header1', 'Header2'],
                        ['Value1', 'Value2']
                    ],
                    'pre_text': ['Introduction', 'Context'],
                    'post_text': ['Conclusion']
                },
                'conversation': [
                    {
                        'question': 'What is the total revenue?',
                        'expected_answer': 100000,
                        'expected_program': 'lookup(revenue)'
                    },
                    {
                        'question': 'What is the profit margin?',
                        'expected_answer': 0.15,
                        'expected_program': 'divide(profit, revenue)'
                    }
                ]
            }
        ]
        
        result = validate_dataset(data)
        assert result is True