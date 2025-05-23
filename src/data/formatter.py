"""Data formatting utilities for financial reports."""

import json
from typing import List, Dict, Any
from src.utils.logging_config import get_logger

logger = get_logger(__name__)


def format_table_as_json_objects(table: List[List]) -> str:
    """Convert table to JSON array of objects - most readable for AI.
    
    Args:
        table: 2D list where first row contains headers
        
    Returns:
        JSON string representation of the table
    """
    if not table or len(table) < 2:
        return ""
    
    headers = table[0]
    rows = table[1:]
    
    # Convert to array of objects
    json_data = []
    for row in rows:
        row_obj = {}
        for i, header in enumerate(headers):
            value = row[i] if i < len(row) else ""
            
            # Try to convert numbers
            if isinstance(value, str) and value.strip():
                clean_val = value.replace(',', '').replace('$', '').strip()
                
                # Handle negative numbers in parentheses
                if '(' in value and ')' in value:
                    clean_val = clean_val.replace('(', '').replace(')', '')
                    if clean_val.replace('.', '').replace('-', '').isdigit():
                        try:
                            value = -float(clean_val) if '.' in clean_val else -int(clean_val)
                        except:
                            pass
                elif clean_val.replace('.', '').replace('-', '').isdigit():
                    try:
                        value = float(clean_val) if '.' in clean_val else int(clean_val)
                    except:
                        pass  # Keep as string if conversion fails
            
            row_obj[header] = value
        json_data.append(row_obj)
    
    return json.dumps(json_data, indent=2)


def format_financial_context(financial_report: Dict[str, Any]) -> str:
    """Format the financial report data into a readable context with JSON tables.
    
    Args:
        financial_report: Dictionary containing financial report data
        
    Returns:
        Formatted context string
    """
    logger.debug("Formatting financial context")
    
    context = "FINANCIAL REPORT CONTEXT:\n\n"
    
    # Add pre-text
    if 'pre_text' in financial_report:
        logger.debug(f"Adding {len(financial_report['pre_text'])} pre-text items")
        context += "Background Information:\n"
        for text in financial_report['pre_text']:
            context += f"- {text}\n"
        context += "\n"
    
    # Add table data as JSON
    if 'table' in financial_report and financial_report['table']:
        table = financial_report['table']
        logger.debug(f"Converting table with {len(table)} rows to JSON")
        context += "Financial Data (JSON):\n"
        json_table = format_table_as_json_objects(table)
        context += json_table + "\n\n"
    
    # Add post-text
    if 'post_text' in financial_report:
        logger.debug(f"Adding {len(financial_report['post_text'])} post-text items")
        context += "Additional Information:\n"
        for text in financial_report['post_text']:
            context += f"- {text}\n"
    
    logger.debug(f"Formatted context length: {len(context)} characters")
    return context


def format_conversation_history(conversation_history: List[Dict]) -> str:
    """Format conversation history for context.
    
    Args:
        conversation_history: List of previous conversation turns
        
    Returns:
        Formatted conversation history string
    """
    if not conversation_history:
        return ""
    
    history_text = "\nPREVIOUS CONVERSATION:\n"
    for i, qa in enumerate(conversation_history):
        history_text += f"Q{i+1}: {qa['question']}\n"
        history_text += f"Program: {qa.get('expected_program', 'N/A')}\n"
        history_text += f"Answer: {qa.get('expected_answer', 'N/A')}\n\n"
    
    return history_text