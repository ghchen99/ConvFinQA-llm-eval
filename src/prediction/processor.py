"""Dataset processing for financial QA predictions."""

import json
import os
from typing import List, Dict, Any, Optional
from src.prediction.generator import prediction_generator
from src.utils.logging_config import get_logger
from config.settings import config

logger = get_logger(__name__)


class DatasetProcessor:
    """Handles processing of financial QA datasets."""
    
    def __init__(self):
        """Initialize the dataset processor."""
        self.generator = prediction_generator
    
    def process_dataset(
        self,
        input_file: str,
        output_file: str,
        max_items: Optional[int] = None
    ) -> Dict[str, Any]:
        """Process the entire dataset and generate predictions.
        
        Args:
            input_file: Path to input JSON file
            output_file: Path to output JSON file
            max_items: Maximum number of items to process (None for all)
            
        Returns:
            Dictionary with processing statistics
        """
        logger.info("Starting dataset processing")
        logger.info(f"Input file: {input_file}")
        logger.info(f"Output file: {output_file}")
        
        if max_items:
            logger.info(f"Processing only first {max_items} items")
        else:
            logger.info("Processing all items in dataset")
        
        # Load and validate input data
        data = self._load_input_data(input_file, max_items)
        
        # Process each item
        results, stats = self._process_items(data)
        
        # Save results
        self._save_results(results, output_file)
        
        # Log final statistics
        self._log_final_stats(stats, output_file)
        
        return stats
    
    def _load_input_data(self, input_file: str, max_items: Optional[int]) -> List[Dict]:
        """Load and validate input data.
        
        Args:
            input_file: Path to input JSON file
            max_items: Maximum number of items to process
            
        Returns:
            List of data items
            
        Raises:
            FileNotFoundError: If input file doesn't exist
            json.JSONDecodeError: If input file is not valid JSON
        """
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Successfully loaded {len(data)} items from input file")
            
            # Limit to first n items if specified
            if max_items and max_items > 0:
                original_count = len(data)
                data = data[:max_items]
                logger.info(f"Limited dataset from {original_count} to {len(data)} items")
            
            return data
            
        except FileNotFoundError:
            logger.error(f"Input file {input_file} not found")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse input file as JSON: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to load input file: {e}")
            raise
    
    def _process_items(self, data: List[Dict]) -> tuple[List[Dict], Dict[str, Any]]:
        """Process all items in the dataset.
        
        Args:
            data: List of data items to process
            
        Returns:
            Tuple of (results, statistics)
        """
        results = []
        total_turns = 0
        successful_predictions = 0
        failed_predictions = 0
        
        for item_idx, item in enumerate(data):
            item_id = item.get('id', f'item_{item_idx}')
            logger.info(f"Processing item {item_idx + 1}/{len(data)}: {item_id}")
            
            # Process item
            result_item, item_stats = self._process_single_item(item, item_idx)
            results.append(result_item)
            
            # Update statistics
            total_turns += item_stats['turns']
            successful_predictions += item_stats['successful']
            failed_predictions += item_stats['failed']
            
            logger.info(f"✓ Item {item_idx + 1} completed")
        
        stats = {
            'total_items': len(results),
            'total_turns': total_turns,
            'successful_predictions': successful_predictions,
            'failed_predictions': failed_predictions,
            'success_rate': successful_predictions / total_turns * 100 if total_turns > 0 else 0
        }
        
        return results, stats
    
    def _process_single_item(self, item: Dict, item_idx: int) -> tuple[Dict, Dict[str, Any]]:
        """Process a single item with its conversation turns.
        
        Args:
            item: Data item to process
            item_idx: Item index for logging
            
        Returns:
            Tuple of (processed_item, item_statistics)
        """
        financial_report = item['financial_report']
        conversation = item['conversation']
        
        logger.info(f"  Item has {len(conversation)} conversation turns")
        
        # Process each turn in the conversation
        conversation_history = []
        enhanced_conversation = []
        successful = 0
        failed = 0
        
        for turn_idx, turn in enumerate(conversation):
            question = turn['question']
            logger.info(f"  Processing turn {turn_idx + 1}/{len(conversation)}: '{question[:50]}...'")
            
            try:
                # Generate prediction for current turn
                prediction = self.generator.generate_prediction(
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
                successful += 1
                
                logger.info(f"  ✓ Turn {turn_idx + 1} completed successfully")
                logger.debug(f"    Program: {prediction['predicted_program']}")
                logger.debug(f"    Answer: {prediction['predicted_answer']}")
                
            except Exception as e:
                logger.error(f"  ✗ Turn {turn_idx + 1} failed: {e}")
                failed += 1
                
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
        
        item_stats = {
            'turns': len(conversation),
            'successful': successful,
            'failed': failed
        }
        
        return result_item, item_stats
    
    def _save_results(self, results: List[Dict], output_file: str) -> None:
        """Save processing results to file.
        
        Args:
            results: List of processed items
            output_file: Path to output file
            
        Raises:
            Exception: If saving fails
        """
        try:
            # Ensure output directory exists
            output_dir = os.path.dirname(output_file)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"Successfully saved results to {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
            raise
    
    def _log_final_stats(self, stats: Dict[str, Any], output_file: str) -> None:
        """Log final processing statistics.
        
        Args:
            stats: Processing statistics
            output_file: Path to output file
        """
        logger.info("=" * 50)
        logger.info("PROCESSING COMPLETE")
        logger.info("=" * 50)
        logger.info(f"Total items processed: {stats['total_items']}")
        logger.info(f"Total conversation turns: {stats['total_turns']}")
        logger.info(f"Successful predictions: {stats['successful_predictions']}")
        logger.info(f"Failed predictions: {stats['failed_predictions']}")
        logger.info(f"Success rate: {stats['success_rate']:.1f}%")
        logger.info(f"Results saved to: {output_file}")
        
        print(f"\nProcessing complete! Check logs for detailed information.")
        print(f"Processed {stats['total_items']} items with {stats['total_turns']} total turns")
        print(f"Success rate: {stats['success_rate']:.1f}%")


# Global processor instance
dataset_processor = DatasetProcessor()