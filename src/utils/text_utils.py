"""Text processing utilities."""

import re
from typing import List
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


def extract_numbers_from_text(text: str) -> List[str]:
    """Extract numeric values from text, handling various formats.
    
    Args:
        text: Input text to extract numbers from
        
    Returns:
        List of extracted number strings
    """
    logger.debug(f"Extracting numbers from text: {text[:100]}...")
    
    # Pattern to match numbers including decimals, negatives, and numbers in parentheses
    patterns = [
        r'\$\s*[\d,]+\.?\d*',  # Dollar amounts
        r'[\d,]+\.?\d*',       # Regular numbers
        r'\(\s*[\d,]+\.?\d*\s*\)',  # Numbers in parentheses (negative)
    ]
    
    numbers = []
    for pattern in patterns:
        matches = re.findall(pattern, text)
        numbers.extend(matches)
    
    logger.debug(f"Extracted {len(numbers)} numbers: {numbers}")
    return numbers


def clean_number(num_str: str) -> float:
    """Clean and convert number string to float.
    
    Args:
        num_str: Number string to clean and convert
        
    Returns:
        Converted float value, or 0.0 if conversion fails
    """
    logger.debug(f"Cleaning number: {num_str}")
    
    # Remove dollar signs, commas, spaces, and parentheses
    cleaned = re.sub(r'[\$,\s\(\)]', '', num_str)
    try:
        result = float(cleaned)
        logger.debug(f"Cleaned number result: {result}")
        return result
    except ValueError as e:
        logger.warning(f"Failed to convert '{num_str}' to float: {e}")
        return 0.0


def extract_json_from_text(text: str) -> str:
    """Extract JSON string from text response.
    
    Args:
        text: Text containing JSON
        
    Returns:
        Extracted JSON string, or empty string if not found
    """
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    return json_match.group() if json_match else ""


def parse_program_answer_from_text(text: str) -> tuple[str, float]:
    """Parse program and answer from text response as fallback.
    
    Args:
        text: Response text to parse
        
    Returns:
        Tuple of (program, answer)
    """
    program_match = re.search(r'"program":\s*"([^"]*)"', text)
    answer_match = re.search(r'"answer":\s*([0-9.-]+)', text)
    
    program = program_match.group(1) if program_match else ""
    answer = float(answer_match.group(1)) if answer_match else 0.0
    
    return program, answer