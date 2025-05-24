"""Tests for src/utils/text_utils.py"""

import pytest
from unittest.mock import patch

from src.utils.text_utils import (
    extract_numbers_from_text,
    clean_number,
    extract_json_from_text,
    parse_program_answer_from_text
)


class TestExtractNumbersFromText:
    """Test cases for extract_numbers_from_text function."""
    
    def test_extract_decimal_numbers(self):
        """Test extracting decimal numbers."""
        text = "The rate is 3.14 and the percentage is 25.5."
        numbers = extract_numbers_from_text(text)
        
        assert "3.14" in numbers
        assert "25.5" in numbers
    
    def test_extract_currency_amounts(self):
        """Test extracting currency amounts."""
        text = "The total was $1,234.56 and the tax was $123.45."
        numbers = extract_numbers_from_text(text)
        
        # Should extract dollar amounts
        dollar_amounts = [n for n in numbers if '$' in n]
        assert len(dollar_amounts) >= 2
        assert any('1,234.56' in n for n in dollar_amounts)
        assert any('123.45' in n for n in dollar_amounts)
    
    def test_extract_numbers_with_commas(self):
        """Test extracting numbers with comma separators."""
        text = "The budget is 1,000,000 and costs are 250,500."
        numbers = extract_numbers_from_text(text)
        
        assert any('1,000,000' in n for n in numbers)
        assert any('250,500' in n for n in numbers)
    
    def test_extract_negative_numbers_parentheses(self):
        """Test extracting negative numbers in parentheses."""
        text = "Profit was 1000 but loss was (500) last quarter."
        numbers = extract_numbers_from_text(text)
        
        assert "1000" in numbers
        assert any('500' in n and '(' in n for n in numbers)
    
    def test_extract_mixed_formats(self):
        """Test extracting various number formats together."""
        text = "Revenue: $12,345.67, Loss: (1,234), Rate: 5.5%, Count: 100"
        numbers = extract_numbers_from_text(text)
        
        # Should find multiple numbers in different formats
        assert len(numbers) >= 3
        assert any('12,345.67' in n for n in numbers)
        assert any('1,234' in n for n in numbers)
        assert any('5.5' in n for n in numbers)
        assert "100" in numbers
    
    def test_extract_no_numbers(self):
        """Test text with no numbers."""
        text = "This text contains no numerical values at all."
        numbers = extract_numbers_from_text(text)
        
        assert len(numbers) == 0
    
    def test_extract_empty_text(self):
        """Test empty text."""
        text = ""
        numbers = extract_numbers_from_text(text)
        
        assert len(numbers) == 0


class TestCleanNumber:
    """Test cases for clean_number function."""
    
    def test_clean_simple_number(self):
        """Test cleaning simple number string."""
        result = clean_number("123")
        assert result == 123.0
    
    def test_clean_decimal_number(self):
        """Test cleaning decimal number string."""
        result = clean_number("123.45")
        assert result == 123.45
    
    def test_clean_currency_number(self):
        """Test cleaning currency formatted number."""
        result = clean_number("$1,234.56")
        assert result == 1234.56
    
    def test_clean_number_with_commas(self):
        """Test cleaning number with comma separators."""
        result = clean_number("1,000,000")
        assert result == 1000000.0
    
    def test_clean_negative_parentheses(self):
        """Test cleaning negative number in parentheses."""
        result = clean_number("(500)")
        assert result == 500.0  # Note: parentheses are removed but not converted to negative
    
    def test_clean_number_with_spaces(self):
        """Test cleaning number with spaces."""
        result = clean_number(" 1 2 3 ")
        assert result == 123.0
    
    def test_clean_complex_format(self):
        """Test cleaning complex formatted number."""
        result = clean_number("$ 12,345.67 ")
        assert result == 12345.67
    
    def test_clean_invalid_number(self):
        """Test cleaning invalid number string."""
        result = clean_number("not-a-number")
        assert result == 0.0
    
    def test_clean_empty_string(self):
        """Test cleaning empty string."""
        result = clean_number("")
        assert result == 0.0
    
    def test_clean_multiple_dots(self):
        """Test cleaning invalid number with multiple decimal points."""
        result = clean_number("12.34.56")
        assert result == 0.0
    
    def test_clean_only_symbols(self):
        """Test cleaning string with only symbols."""
        result = clean_number("$,.()")
        assert result == 0.0


class TestExtractJsonFromText:
    """Test cases for extract_json_from_text function."""
    
    def test_extract_simple_json(self):
        """Test extracting simple JSON from text."""
        text = 'Here is the result: {"answer": 42, "program": "test"}'
        json_str = extract_json_from_text(text)
        
        assert json_str == '{"answer": 42, "program": "test"}'
    
    def test_extract_json_with_nested_objects(self):
        """Test extracting JSON with nested objects."""
        text = 'Result: {"data": {"value": 100}, "status": "ok"}'
        json_str = extract_json_from_text(text)
        
        assert json_str == '{"data": {"value": 100}, "status": "ok"}'
    
    def test_extract_json_with_arrays(self):
        """Test extracting JSON with arrays."""
        text = 'Data: {"items": [1, 2, 3], "count": 3}'
        json_str = extract_json_from_text(text)
        
        assert json_str == '{"items": [1, 2, 3], "count": 3}'
    
    def test_extract_no_json(self):
        """Test text with no JSON."""
        text = "This text has no JSON objects in it at all."
        json_str = extract_json_from_text(text)
        
        assert json_str == ""
    
    def test_extract_malformed_json(self):
        """Test text with malformed JSON-like content."""
        text = "Here is data: {answer: 42, program: test}"  # Missing quotes
        json_str = extract_json_from_text(text)
        
        # Should still extract the braces content
        assert json_str == "{answer: 42, program: test}"
    
    def test_extract_empty_json(self):
        """Test extracting empty JSON object."""
        text = "Empty result: {}"
        json_str = extract_json_from_text(text)
        
        assert json_str == "{}"


class TestParseProgramAnswerFromText:
    """Test cases for parse_program_answer_from_text function."""
    
    def test_parse_complete_response(self):
        """Test parsing complete program and answer from text."""
        text = '''The calculation is:
        "program": "add(100, 200)",
        "answer": 300
        That's the result.'''
        
        program, answer = parse_program_answer_from_text(text)
        
        assert program == "add(100, 200)"
        assert answer == 300.0
    
    def test_parse_json_format(self):
        """Test parsing from JSON-formatted text."""
        text = '{"program": "multiply(5, 10)", "answer": 50}'
        program, answer = parse_program_answer_from_text(text)
        
        assert program == "multiply(5, 10)"
        assert answer == 50.0
    
    def test_parse_decimal_answer(self):
        """Test parsing decimal answer."""
        text = '"program": "divide(1, 3)", "answer": 0.33333'
        program, answer = parse_program_answer_from_text(text)
        
        assert program == "divide(1, 3)"
        assert answer == 0.33333
    
    def test_parse_negative_answer(self):
        """Test parsing negative answer."""
        text = '"program": "subtract(10, 20)", "answer": -10'
        program, answer = parse_program_answer_from_text(text)
        
        assert program == "subtract(10, 20)"
        assert answer == -10.0
    
    def test_parse_missing_program(self):
        """Test parsing when program is missing."""
        text = '"answer": 42'
        program, answer = parse_program_answer_from_text(text)
        
        assert program == ""
        assert answer == 42.0
    
    def test_parse_missing_answer(self):
        """Test parsing when answer is missing."""
        text = '"program": "lookup(revenue)"'
        program, answer = parse_program_answer_from_text(text)
        
        assert program == "lookup(revenue)"
        assert answer == 0.0
    
    def test_parse_both_missing(self):
        """Test parsing when both program and answer are missing."""
        text = "This text has no program or answer fields."
        program, answer = parse_program_answer_from_text(text)
        
        assert program == ""
        assert answer == 0.0
    
    def test_parse_empty_text(self):
        """Test parsing empty text."""
        text = ""
        program, answer = parse_program_answer_from_text(text)
        
        assert program == ""
        assert answer == 0.0
    
    def test_parse_multiple_matches(self):
        """Test parsing when there are multiple matches (should use first)."""
        text = '''
        First: "program": "add(1, 2)", "answer": 3
        Second: "program": "multiply(2, 3)", "answer": 6
        '''
        program, answer = parse_program_answer_from_text(text)
        
        assert program == "add(1, 2)"
        assert answer == 3.0