#!/usr/bin/env python3
"""
Financial QA Prediction Generator - Main Entry Point

This script generates predictions for financial QA datasets using Azure OpenAI.
"""

import argparse
import os
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from config.settings import config
from src.utils.logging_config import setup_logging
from src.prediction.processor import dataset_processor
from src.utils.validation import validate_environment, validate_input_file


def main(max_examples: int = None) -> None:
    """Main function to run the prediction generator.
    
    Args:
        max_examples: Maximum number of examples to process. 
                      If None, processes all examples.
    """
    # Setup logging
    logger = setup_logging()
    
    logger.info("=" * 60)
    logger.info("FINANCIAL QA PREDICTION GENERATOR STARTED")
    logger.info("=" * 60)
    
    if max_examples:
        logger.info(f"Running in limited mode: processing first {max_examples} examples")
    else:
        logger.info("Running in full mode: processing all examples")
    
    try:
        # Ensure directories exist
        config.ensure_directories()
        
        # Validate environment and input
        validate_environment()
        validate_input_file(config.default_input_file)
        
        # Determine output file
        output_file = config.default_output_file
        if max_examples:
            base_name = os.path.splitext(output_file)[0]
            extension = os.path.splitext(output_file)[1]
            output_file = f"{base_name}_first_{max_examples}{extension}"
            logger.info(f"Updated output file for limited run: {output_file}")
        
        # Print startup information
        print("Starting financial QA prediction generation...")
        print(f"Input file: {config.default_input_file}")
        print(f"Output file: {output_file}")
        if max_examples:
            print(f"Processing only first {max_examples} examples")
        print(f"Logs will be saved to: {config.logs_dir}/")
        
        # Process the dataset
        stats = dataset_processor.process_dataset(
            input_file=config.default_input_file,
            output_file=output_file,
            max_items=max_examples
        )
        
        logger.info("SCRIPT COMPLETED SUCCESSFULLY")
        
    except Exception as e:
        logger.error(f"SCRIPT FAILED: {e}", exc_info=True)
        print(f"Error: Script failed. Check logs for details: {e}")
        sys.exit(1)


def create_cli_parser() -> argparse.ArgumentParser:
    """Create command line argument parser.
    
    Returns:
        Configured argument parser
    """
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
    
    parser.add_argument(
        '--input-file', '-i',
        type=str,
        default=None,
        help=f'Input file path (default: {config.default_input_file})'
    )
    
    parser.add_argument(
        '--output-file', '-o',
        type=str,
        default=None,
        help=f'Output file path (default: {config.default_output_file})'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )
    
    return parser


if __name__ == "__main__":
    parser = create_cli_parser()
    args = parser.parse_args()
    
    # Validate arguments
    if args.max_examples is not None and args.max_examples <= 0:
        print("Error: --max-examples must be a positive integer")
        parser.print_help()
        sys.exit(1)
    
    # Override config defaults if specified
    if args.input_file:
        config.default_input_file = args.input_file
    if args.output_file:
        config.default_output_file = args.output_file
    
    main(max_examples=args.max_examples)