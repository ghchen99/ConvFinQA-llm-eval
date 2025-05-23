import os
import json
import logging
from datetime import datetime
from openai import AzureOpenAI
from dotenv import load_dotenv
import re
from typing import List, Dict, Any

load_dotenv()

# Setup logging
def setup_logging():
    """Setup logging configuration."""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Create timestamp for log filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f'logs/financial_qa_prediction_{timestamp}.log'
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()  # Also log to console
        ]
    )
    
    # Create logger
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized. Log file: {log_filename}")
    return logger

# Initialize logger
logger = setup_logging()

# Load environment variables from .env file
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_MODEL_NAME = os.getenv("AZURE_OPENAI_MODEL_NAME")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

logger.info("Environment variables loaded")
logger.info(f"Azure OpenAI Endpoint: {AZURE_OPENAI_ENDPOINT}")
logger.info(f"Deployment Name: {AZURE_OPENAI_DEPLOYMENT_NAME}")
logger.info(f"API Version: {AZURE_OPENAI_API_VERSION}")

client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version=AZURE_OPENAI_API_VERSION
)

logger.info("Azure OpenAI client initialized successfully")

def extract_numbers_from_text(text: str) -> List[str]:
    """Extract numeric values from text, handling various formats."""
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
    """Clean and convert number string to float."""
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

def format_table_as_json_objects(table: List[List]) -> str:
    """Convert table to JSON array of objects - most readable for AI."""
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
    """Format the financial report data into a readable context with JSON tables."""
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

def create_system_prompt() -> str:
    """Create the system prompt for financial QA."""
    return """You are a financial analysis expert specialized in answering questions about financial reports and performing calculations.

Your task is to:
1. Analyze financial report data (text and tables)
2. Answer questions about specific financial metrics
3. Generate both a "program" (calculation steps) and a numerical answer

For the "program" field:
- If the answer is a direct lookup from the data, just return the number (e.g., "206588")
- If calculation is needed, show the operation (e.g., "subtract(206588, 181001)" or "divide(25587, 181001)")
- For multi-step calculations, separate with commas and use #0, #1, etc. to reference previous results
- Common operations: add(), subtract(), multiply(), divide()

For the "answer" field:
- Always return a numerical value (float)
- Round to appropriate decimal places (typically 4-5 decimal places for percentages)

Examples:
- Direct lookup: program="206588", answer=206588.0
- Simple calculation: program="subtract(206588, 181001)", answer=25587.0
- Multi-step: program="subtract(206588, 181001), divide(#0, 181001)", answer=0.14136

Be precise with numbers and calculations. Pay attention to context from previous questions in multi-turn conversations."""

def generate_prediction(financial_report: Dict[str, Any], conversation_history: List[Dict], current_question: str) -> Dict[str, Any]:
    """Generate prediction for a single question."""
    
    logger.info(f"Generating prediction for question: '{current_question}'")
    logger.debug(f"Conversation history length: {len(conversation_history)}")
    
    # Format the financial context
    context = format_financial_context(financial_report)
    
    # Build conversation history
    history_text = ""
    if conversation_history:
        history_text = "\nPREVIOUS CONVERSATION:\n"
        for i, qa in enumerate(conversation_history):
            history_text += f"Q{i+1}: {qa['question']}\n"
            history_text += f"Program: {qa.get('expected_program', 'N/A')}\n"
            history_text += f"Answer: {qa.get('expected_answer', 'N/A')}\n\n"
    
    # Create the user message
    user_message = f"""{context}

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

    logger.debug(f"User message length: {len(user_message)} characters")

    try:
        logger.info("Sending request to Azure OpenAI")
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": create_system_prompt()
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            max_tokens=1000,
            temperature=0.1,  # Low temperature for consistent numerical results
            model=AZURE_OPENAI_DEPLOYMENT_NAME
        )
        
        logger.info("Received response from Azure OpenAI")
        
        # Parse the response
        response_text = response.choices[0].message.content.strip()
        logger.debug(f"Raw response: {response_text}")
        
        # Try to extract JSON from response
        try:
            # Look for JSON in the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
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
        program_match = re.search(r'"program":\s*"([^"]*)"', response_text)
        answer_match = re.search(r'"answer":\s*([0-9.-]+)', response_text)
        
        program = program_match.group(1) if program_match else ""
        answer = float(answer_match.group(1)) if answer_match else 0.0
        
        prediction = {
            "predicted_program": program,
            "predicted_answer": answer
        }
        logger.info(f"Fallback parsing result: {prediction}")
        return prediction
        
    except Exception as e:
        logger.error(f"Error generating prediction: {e}", exc_info=True)
        return {
            "predicted_program": "",
            "predicted_answer": 0.0
        }

def process_financial_qa_dataset(input_file: str, output_file: str, max_items: int = None):
    """Process the entire dataset and generate predictions."""
    
    logger.info(f"Starting dataset processing")
    logger.info(f"Input file: {input_file}")
    logger.info(f"Output file: {output_file}")
    if max_items:
        logger.info(f"Processing only first {max_items} items")
    else:
        logger.info("Processing all items in dataset")
    
    # Load the input data
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Successfully loaded {len(data)} items from input file")
        
        # Limit to first n items if specified
        if max_items and max_items > 0:
            original_count = len(data)
            data = data[:max_items]
            logger.info(f"Limited dataset from {original_count} to {len(data)} items")
            
    except Exception as e:
        logger.error(f"Failed to load input file: {e}")
        raise
    
    results = []
    total_turns = 0
    successful_predictions = 0
    failed_predictions = 0
    
    for item_idx, item in enumerate(data):
        item_id = item.get('id', f'item_{item_idx}')
        logger.info(f"Processing item {item_idx + 1}/{len(data)}: {item_id}")
        
        financial_report = item['financial_report']
        conversation = item['conversation']
        
        # Log item statistics
        logger.info(f"  Item has {len(conversation)} conversation turns")
        total_turns += len(conversation)
        
        # Process each turn in the conversation
        conversation_history = []
        enhanced_conversation = []
        
        for turn_idx, turn in enumerate(conversation):
            question = turn['question']
            logger.info(f"  Processing turn {turn_idx + 1}/{len(conversation)}: '{question[:50]}...'")
            
            try:
                # Generate prediction for current turn
                prediction = generate_prediction(
                    financial_report=financial_report,
                    conversation_history=conversation_history,
                    current_question=question
                )
                
                # Create enhanced turn with predictions
                enhanced_turn = {
                    **turn,  # Keep original fields
                    **prediction  # Add predicted fields
                }
                
                enhanced_conversation.append(enhanced_turn)
                successful_predictions += 1
                
                logger.info(f"  ✓ Turn {turn_idx + 1} completed successfully")
                logger.debug(f"    Program: {prediction['predicted_program']}")
                logger.debug(f"    Answer: {prediction['predicted_answer']}")
                
            except Exception as e:
                logger.error(f"  ✗ Turn {turn_idx + 1} failed: {e}")
                failed_predictions += 1
                
                # Add turn with empty predictions
                enhanced_turn = {
                    **turn,
                    "predicted_program": "",
                    "predicted_answer": 0.0
                }
                enhanced_conversation.append(enhanced_turn)
            
            # Add current turn to history for next iterations
            conversation_history.append(turn)
        
        # Create result item
        result_item = {
            **item,  # Keep original structure
            'conversation': enhanced_conversation  # Replace with enhanced conversation
        }
        
        results.append(result_item)
        logger.info(f"✓ Item {item_idx + 1} completed")
    
    # Save results
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info(f"Successfully saved results to {output_file}")
    except Exception as e:
        logger.error(f"Failed to save results: {e}")
        raise
    
    # Log final statistics
    logger.info("=" * 50)
    logger.info("PROCESSING COMPLETE")
    logger.info("=" * 50)
    logger.info(f"Total items processed: {len(results)}")
    logger.info(f"Total conversation turns: {total_turns}")
    logger.info(f"Successful predictions: {successful_predictions}")
    logger.info(f"Failed predictions: {failed_predictions}")
    logger.info(f"Success rate: {successful_predictions/total_turns*100:.1f}%")
    logger.info(f"Results saved to: {output_file}")
    
    print(f"\nProcessing complete! Check logs for detailed information.")
    print(f"Processed {len(results)} items with {total_turns} total turns")
    print(f"Success rate: {successful_predictions/total_turns*100:.1f}%")

def main(max_examples: int = None):
    """Main function to run the prediction generator.
    
    Args:
        max_examples (int, optional): Maximum number of examples to process. 
                                    If None, processes all examples.
    """
    input_file = "data/processed_train.json"
    output_file = "data/predictions_output.json"
    
    logger.info("="*60)
    logger.info("FINANCIAL QA PREDICTION GENERATOR STARTED")
    logger.info("="*60)
    
    if max_examples:
        logger.info(f"Running in limited mode: processing first {max_examples} examples")
    else:
        logger.info("Running in full mode: processing all examples")
    
    # Check if input file exists
    if not os.path.exists(input_file):
        logger.error(f"Input file {input_file} not found.")
        print(f"Error: Input file {input_file} not found.")
        print("Please make sure the file exists and the path is correct.")
        return
    
    logger.info(f"Input file found: {input_file}")
    
    # Check if required environment variables are set
    required_vars = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT", 
        "AZURE_OPENAI_DEPLOYMENT_NAME"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        print(f"Error: Missing required environment variables: {missing_vars}")
        print("Please set these in your .env file.")
        return
    
    logger.info("All required environment variables are set")
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.info(f"Created output directory: {output_dir}")
    
    # Update output filename if running limited examples
    if max_examples:
        base_name = os.path.splitext(output_file)[0]
        extension = os.path.splitext(output_file)[1]
        output_file = f"{base_name}_first_{max_examples}{extension}"
        logger.info(f"Updated output file for limited run: {output_file}")
    
    print("Starting financial QA prediction generation...")
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    if max_examples:
        print(f"Processing only first {max_examples} examples")
    print(f"Logs will be saved to: logs/")
    
    try:
        process_financial_qa_dataset(input_file, output_file, max_examples)
        logger.info("SCRIPT COMPLETED SUCCESSFULLY")
    except Exception as e:
        logger.error(f"SCRIPT FAILED: {e}", exc_info=True)
        print(f"Error: Script failed. Check logs for details: {e}")
        raise

if __name__ == "__main__":
    import argparse
    
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(
        description="Generate predictions for financial QA dataset using Azure OpenAI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Process all examples
  python main.py --max-examples 5   # Process first 5 examples
  python main.py -n 10             # Process first 10 examples
        """
    )
    
    parser.add_argument(
        '--max-examples', '-n',
        type=int,
        default=None,
        help='Maximum number of examples to process (default: process all examples)'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.max_examples is not None and args.max_examples <= 0:
        print("Error: --max-examples must be a positive integer")
        parser.print_help()
        exit(1)
    
    main(max_examples=args.max_examples)
    
    