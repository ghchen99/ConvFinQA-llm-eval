"""Tests for src/data/formatter.py"""

import json
import pytest
from unittest.mock import patch

from src.data.formatter import (
    format_table_as_json_objects,
    format_financial_context,
    format_conversation_history
)


class TestFormatTableAsJsonObjects:
    """Test cases for format_table_as_json_objects function."""
    
    def test_simple_table(self):
        """Test formatting a simple table."""
        table = [
            ['Name', 'Value'],
            ['Revenue', '1000'],
            ['Expenses', '500']
        ]
        
        result = format_table_as_json_objects(table)
        parsed = json.loads(result)
        
        expected = [
            {'Name': 'Revenue', 'Value': 1000},
            {'Name': 'Expenses', 'Value': 500}
        ]
        
        assert parsed == expected
    
    def test_table_with_float_values(self):
        """Test table with decimal values."""
        table = [
            ['Item', 'Price', 'Tax'],
            ['Product A', '99.99', '7.50'],
            ['Product B', '150.00', '12.00']
        ]
        
        result = format_table_as_json_objects(table)
        parsed = json.loads(result)
        
        expected = [
            {'Item': 'Product A', 'Price': 99.99, 'Tax': 7.5},
            {'Item': 'Product B', 'Price': 150.0, 'Tax': 12.0}
        ]
        
        assert parsed == expected
    
    def test_table_with_currency_values(self):
        """Test table with currency formatting."""
        table = [
            ['Account', 'Balance'],
            ['Checking', '$1,234.56'],
            ['Savings', '$10,000.00']
        ]
        
        result = format_table_as_json_objects(table)
        parsed = json.loads(result)
        
        expected = [
            {'Account': 'Checking', 'Balance': 1234.56},
            {'Account': 'Savings', 'Balance': 10000.0}
        ]
        
        assert parsed == expected
    
    def test_table_with_negative_values_parentheses(self):
        """Test table with negative values in parentheses."""
        table = [
            ['Account', 'Change'],
            ['Assets', '1000'],
            ['Liabilities', '(500)'],
            ['Equity', '(250.50)']
        ]
        
        result = format_table_as_json_objects(table)
        parsed = json.loads(result)
        
        expected = [
            {'Account': 'Assets', 'Change': 1000},
            {'Account': 'Liabilities', 'Change': -500},
            {'Account': 'Equity', 'Change': -250.5}
        ]
        
        assert parsed == expected
    
    def test_table_with_mixed_data_types(self):
        """Test table with mixed data types."""
        table = [
            ['Name', 'Amount', 'Status', 'Rate'],
            ['Item 1', '1,000', 'Active', '5.5'],
            ['Item 2', '(200)', 'Inactive', 'N/A'],
            ['Item 3', '0', 'Pending', '10.25']
        ]
        
        result = format_table_as_json_objects(table)
        parsed = json.loads(result)
        
        expected = [
            {'Name': 'Item 1', 'Amount': 1000, 'Status': 'Active', 'Rate': 5.5},
            {'Name': 'Item 2', 'Amount': -200, 'Status': 'Inactive', 'Rate': 'N/A'},
            {'Name': 'Item 3', 'Amount': 0, 'Status': 'Pending', 'Rate': 10.25}
        ]
        
        assert parsed == expected
    
    def test_table_with_missing_values(self):
        """Test table with missing values in rows."""
        table = [
            ['Col1', 'Col2', 'Col3'],
            ['A', 'B'],  # Missing Col3
            ['X', 'Y', 'Z'],
            ['P']  # Missing Col2 and Col3
        ]
        
        result = format_table_as_json_objects(table)
        parsed = json.loads(result)
        
        expected = [
            {'Col1': 'A', 'Col2': 'B', 'Col3': ''},
            {'Col1': 'X', 'Col2': 'Y', 'Col3': 'Z'},
            {'Col1': 'P', 'Col2': '', 'Col3': ''}
        ]
        
        assert parsed == expected
    
    def test_empty_table(self):
        """Test empty table."""
        table = []
        result = format_table_as_json_objects(table)
        assert result == ""
    
    def test_table_with_only_headers(self):
        """Test table with only headers."""
        table = [['Header1', 'Header2']]
        result = format_table_as_json_objects(table)
        assert result == ""
    
    def test_invalid_conversion_fallback(self):
        """Test that invalid number conversion falls back to string."""
        table = [
            ['Name', 'Value'],
            ['Item', 'not-a-number'],
            ['Other', '1.2.3']  # Invalid number format
        ]
        
        result = format_table_as_json_objects(table)
        parsed = json.loads(result)
        
        expected = [
            {'Name': 'Item', 'Value': 'not-a-number'},
            {'Name': 'Other', 'Value': '1.2.3'}
        ]
        
        assert parsed == expected


class TestFormatFinancialContext:
    """Test cases for format_financial_context function."""
    
    def test_complete_financial_report(self):
        """Test formatting with all sections."""
        financial_report = {
            'pre_text': ['Company overview', 'Financial highlights'],
            'table': [
                ['Account', 'Amount'],
                ['Revenue', '100000'],
                ['Expenses', '75000']
            ],
            'post_text': ['Notes', 'Disclaimers']
        }
        
        result = format_financial_context(financial_report)
        
        assert 'FINANCIAL REPORT CONTEXT:' in result
        assert 'Background Information:' in result
        assert 'Company overview' in result
        assert 'Financial highlights' in result
        assert 'Financial Data (JSON):' in result
        assert '"Account": "Revenue"' in result
        assert '"Amount": 100000' in result
        assert 'Additional Information:' in result
        assert 'Notes' in result
        assert 'Disclaimers' in result
    
    def test_financial_report_with_table_only(self):
        """Test formatting with only table data."""
        financial_report = {
            'table': [
                ['Metric', 'Value'],
                ['Assets', '50000'],
                ['Liabilities', '30000']
            ]
        }
        
        result = format_financial_context(financial_report)
        
        assert 'FINANCIAL REPORT CONTEXT:' in result
        assert 'Financial Data (JSON):' in result
        assert '"Metric": "Assets"' in result
        assert '"Value": 50000' in result
        assert 'Background Information:' not in result
        assert 'Additional Information:' not in result
    
    def test_financial_report_with_pre_text_only(self):
        """Test formatting with only pre-text."""
        financial_report = {
            'pre_text': ['Introduction', 'Summary']
        }
        
        result = format_financial_context(financial_report)
        
        assert 'FINANCIAL REPORT CONTEXT:' in result
        assert 'Background Information:' in result
        assert 'Introduction' in result
        assert 'Summary' in result
        assert 'Financial Data (JSON):' not in result
    
    def test_financial_report_with_post_text_only(self):
        """Test formatting with only post-text."""
        financial_report = {
            'post_text': ['Footnotes', 'Contact info']
        }
        
        result = format_financial_context(financial_report)
        
        assert 'FINANCIAL REPORT CONTEXT:' in result
        assert 'Additional Information:' in result
        assert 'Footnotes' in result
        assert 'Contact info' in result
    
    def test_empty_financial_report(self):
        """Test formatting with empty financial report."""
        financial_report = {}
        
        result = format_financial_context(financial_report)
        
        assert result == 'FINANCIAL REPORT CONTEXT:\n\n'
    
    def test_financial_report_with_empty_table(self):
        """Test formatting with empty table."""
        financial_report = {
            'table': [],
            'pre_text': ['Some text']
        }
        
        result = format_financial_context(financial_report)
        
        assert 'Background Information:' in result
        assert 'Some text' in result
        # Empty table should not add JSON section
        assert 'Financial Data (JSON):' not in result


class TestFormatConversationHistory:
    """Test cases for format_conversation_history function."""
    
    def test_conversation_history_complete(self):
        """Test formatting complete conversation history."""
        conversation_history = [
            {
                'question': 'What is the revenue?',
                'expected_program': '100000',
                'expected_answer': 100000.0
            },
            {
                'question': 'What is the profit margin?',
                'expected_program': 'divide(25000, 100000)',
                'expected_answer': 0.25
            }
        ]
        
        result = format_conversation_history(conversation_history)
        
        assert 'PREVIOUS CONVERSATION:' in result
        assert 'Q1: What is the revenue?' in result
        assert 'Program: 100000' in result
        assert 'Answer: 100000.0' in result
        assert 'Q2: What is the profit margin?' in result
        assert 'Program: divide(25000, 100000)' in result
        assert 'Answer: 0.25' in result
    
    def test_conversation_history_missing_fields(self):
        """Test formatting conversation history with missing fields."""
        conversation_history = [
            {
                'question': 'What is the total?'
                # Missing expected_program and expected_answer
            },
            {
                'question': 'What is the percentage?',
                'expected_program': 'multiply(0.15, 100)'
                # Missing expected_answer
            }
        ]
        
        result = format_conversation_history(conversation_history)
        
        assert 'Q1: What is the total?' in result
        assert 'Program: N/A' in result
        assert 'Answer: N/A' in result
        assert 'Q2: What is the percentage?' in result
        assert 'Program: multiply(0.15, 100)' in result
        assert 'Answer: N/A' in result
    
    def test_empty_conversation_history(self):
        """Test formatting empty conversation history."""
        conversation_history = []
        
        result = format_conversation_history(conversation_history)
        
        assert result == ""
    
    def test_none_conversation_history(self):
        """Test formatting None conversation history."""
        conversation_history = None
        
        result = format_conversation_history(conversation_history)
        
        assert result == ""
    
    def test_single_conversation_turn(self):
        """Test formatting single conversation turn."""
        conversation_history = [
            {
                'question': 'What is the balance?',
                'expected_program': '75000',
                'expected_answer': 75000.0
            }
        ]
        
        result = format_conversation_history(conversation_history)
        
        assert 'PREVIOUS CONVERSATION:' in result
        assert 'Q1: What is the balance?' in result
        assert 'Program: 75000' in result
        assert 'Answer: 75000.0' in result
        # Should not have Q2
        assert 'Q2:' not in result