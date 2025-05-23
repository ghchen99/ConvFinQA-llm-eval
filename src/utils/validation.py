"""Validation utilities for input data and environment."""

import os
import json
from typing import List
from config.settings import config
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


def validate_environment() -> None:
    """Validate that all required environment variables are set.
    
    Raises:
        ValueError: If required environment variables are missing
    """
    try:
        config.azure_openai.validate()
        logger.info("All required environment variables are set")
    except ValueError as e:
        logger.error(f"Environment validation failed: {e}")
        print(f"Error: {e}")
        print("Please set these in your .env file.")
        raise


def validate_input_file(file_path: str) -> None:
    """Validate that input file exists and is readable.
    
    Args:
        file_path: Path to input file
        
    Raises:
        FileNotFoundError: If input file doesn't exist
        json.JSONDecodeError: If input file is not valid JSON
    """
    if not os.path.exists(file_path):
        logger.error(f"Input file {file_path} not found")
        print(f"Error: Input file {file_path} not found.")
        print("Please make sure the file exists and the path is correct.")
        raise FileNotFoundError(f"Input file {file_path} not found")
    
    logger.info(f"Input file found: {file_path}")
    
    # Validate JSON format
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            raise ValueError("Input file must contain a JSON array")
        
        if len(data) == 0:
            raise ValueError("Input file contains no data")
        
        logger.info(f"Input file validation passed: {len(data)} items found")
        
    except json.JSONDecodeError as e:
        logger.error(f"Input file is not valid JSON: {e}")
        print(f"Error: Input file is not valid JSON: {e}")
        raise
    except Exception as e:
        logger.error(f"Error validating input file: {e}")
        print(f"Error validating input file: {e}")
        raise


def validate_data_structure(item: dict, item_idx: int) -> List[str]:
    """Validate the structure of a data item.
    
    Args:
        item: Data item to validate
        item_idx: Index of the item for error reporting
        
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    
    # Check required top-level fields
    required_fields = ['id', 'financial_report', 'conversation']
    for field in required_fields:
        if field not in item:
            errors.append(f"Item {item_idx}: Missing required field '{field}'")
    
    # Validate financial_report structure
    if 'financial_report' in item:
        financial_report = item['financial_report']
        if not isinstance(financial_report, dict):
            errors.append(f"Item {item_idx}: 'financial_report' must be a dictionary")
    
    # Validate conversation structure
    if 'conversation' in item:
        conversation = item['conversation']
        if not isinstance(conversation, list):
            errors.append(f"Item {item_idx}: 'conversation' must be a list")
        else:
            for turn_idx, turn in enumerate(conversation):
                if not isinstance(turn, dict):
                    errors.append(f"Item {item_idx}, Turn {turn_idx}: Turn must be a dictionary")
                elif 'question' not in turn:
                    errors.append(f"Item {item_idx}, Turn {turn_idx}: Missing 'question' field")
    
    return errors


def validate_dataset(data: list) -> bool:
    """Validate the entire dataset structure.
    
    Args:
        data: List of data items to validate
        
    Returns:
        True if validation passes, False otherwise
    """
    logger.info(f"Validating dataset with {len(data)} items")
    
    all_errors = []
    
    for item_idx, item in enumerate(data):
        if not isinstance(item, dict):
            all_errors.append(f"Item {item_idx}: Must be a dictionary")
            continue
        
        item_errors = validate_data_structure(item, item_idx)
        all_errors.extend(item_errors)
    
    if all_errors:
        logger.error("Dataset validation failed:")
        for error in all_errors[:10]:  # Log first 10 errors
            logger.error(f"  {error}")
        if len(all_errors) > 10:
            logger.error(f"  ... and {len(all_errors) - 10} more errors")
        return False
    
    logger.info("Dataset validation passed")
    return True