#!/usr/bin/env python3
"""
Simple LLM judge evaluation script - Refactored version.
"""

import argparse
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.evaluation.processor import EvaluationProcessor
from src.utils.logging_config import setup_logging


def create_cli_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Evaluate financial QA predictions using LLM judge",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--input-file', '-i',
        type=str,
        default="data/output/predictions_first_100.json",
        help='Input predictions file path'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        type=str,
        default="data/output",
        help='Output directory for results'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )
    
    return parser


def main():
    """Main execution function."""
    parser = create_cli_parser()
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(log_level=args.log_level)
    
    try:
        # Initialize processor and run evaluation
        processor = EvaluationProcessor()
        summary = processor.process_evaluation(args.input_file, args.output_dir)
        
        print(f"\nEvaluation completed successfully!")
        print(f"Overall accuracy: {summary.overall_accuracy:.1f}%")
        
    except Exception as e:
        print(f"Error: Evaluation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()