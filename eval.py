#!/usr/bin/env python3
"""
Simple LLM judge evaluation script.
"""

import json
import os
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime

from src.api.azure_client import azure_client

@dataclass
class EvaluationResult:
    """Result of a single prediction evaluation."""
    question_id: str
    question: str
    expected_answer: float
    predicted_answer: float
    expected_program: str
    predicted_program: str
    answer_correct: bool
    program_correct: bool
    reasoning: str
    error: str = None

class LLMJudge:
    """LLM-based evaluation of financial calculation predictions."""
    
    def __init__(self):
        self.client = azure_client
    
    def create_evaluation_prompt(self, question: str, expected_answer: float, predicted_answer: float, 
                               expected_program: str, predicted_program: str) -> str:
        """Create evaluation prompt for the LLM judge."""
        return f"""Evaluate this financial calculation prediction:

Question: {question}
Expected Answer: {expected_answer}
Predicted Answer: {predicted_answer}
Expected Program: {expected_program}
Predicted Program: {predicted_program}

Determine:
1. Is the predicted answer correct? (Consider decimal vs percentage formats - e.g., 0.14 = 14%)
2. Is the predicted program correct? (Consider functionally equivalent calculations)

Important: Answers may be equivalent even if in different formats:
- 0.14 and 14.0 both represent 14%
- Programs may be equivalent with different percentage conversions

Respond with:
- answer_correct: true/false
- program_correct: true/false  
- reasoning: Brief explanation of why answers/programs are correct or incorrect, especially for format differences"""

    def evaluate_single_prediction(self, item: Dict[str, Any], conversation_idx: int) -> EvaluationResult:
        """Evaluate a single prediction using the LLM judge."""
        try:
            conv_item = item['conversation'][conversation_idx]
            question = conv_item['question']
            expected_answer = float(conv_item['expected_answer'])
            predicted_answer = float(conv_item['predicted_answer'])
            expected_program = conv_item.get('expected_program', '')
            predicted_program = conv_item.get('predicted_program', '')
            
            # Create evaluation prompt
            prompt = self.create_evaluation_prompt(question, expected_answer, predicted_answer, 
                                                 expected_program, predicted_program)
            
            # Get LLM evaluation
            messages = [
                {"role": "system", "content": "You are a financial analyst. Respond only with valid JSON."},
                {"role": "user", "content": prompt}
            ]
            
            eval_data = self.client.create_chat_completion(
                messages, 
                temperature=0.1, 
                json=True,
            )
            
            # Handle string response if needed
            if isinstance(eval_data, str):
                eval_data = json.loads(eval_data)
            
            return EvaluationResult(
                question_id=f"{item['id']}-{conversation_idx}",
                question=question,
                expected_answer=expected_answer,
                predicted_answer=predicted_answer,
                expected_program=expected_program,
                predicted_program=predicted_program,
                answer_correct=eval_data.get('answer_correct', False),
                program_correct=eval_data.get('program_correct', False),
                reasoning=eval_data.get('reasoning', '')
            )
                
        except Exception as e:
            print(f"Error evaluating prediction: {e}")
            return EvaluationResult(
                question_id=f"{item.get('id', 'unknown')}-{conversation_idx}",
                question=conv_item.get('question', 'unknown'),
                expected_answer=conv_item.get('expected_answer', 0),
                predicted_answer=conv_item.get('predicted_answer', 0),
                expected_program=conv_item.get('expected_program', ''),
                predicted_program=conv_item.get('predicted_program', ''),
                answer_correct=False,
                program_correct=False,
                reasoning="Evaluation failed due to error",
                error=str(e)
            )

def save_results(results: List[EvaluationResult], output_dir: str):
    """Save evaluation results to file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Calculate simple metrics
    total = len(results)
    answer_correct = sum(1 for r in results if r.answer_correct)
    program_correct = sum(1 for r in results if r.program_correct)
    both_correct = sum(1 for r in results if r.answer_correct and r.program_correct)
    
    # Save detailed results
    results_data = {
        "timestamp": timestamp,
        "summary": {
            "total": total,
            "answer_correct": answer_correct,
            "program_correct": program_correct,
            "both_correct": both_correct,
            "answer_accuracy": round(answer_correct / total * 100, 2) if total > 0 else 0,
            "program_accuracy": round(program_correct / total * 100, 2) if total > 0 else 0,
            "overall_accuracy": round(both_correct / total * 100, 2) if total > 0 else 0
        },
        "results": [
            {
                "question_id": r.question_id,
                "question": r.question,
                "expected_answer": r.expected_answer,
                "predicted_answer": r.predicted_answer,
                "expected_program": r.expected_program,
                "predicted_program": r.predicted_program,
                "answer_correct": r.answer_correct,
                "program_correct": r.program_correct,
                "reasoning": r.reasoning,
                "error": r.error
            }
            for r in results
        ]
    }
    
    results_file = os.path.join(output_dir, f"evaluation_results_{timestamp}.json")
    with open(results_file, 'w') as f:
        json.dump(results_data, f, indent=2)
    
    return results_file, results_data["summary"]

def main():
    """Main execution function."""
    print("Starting LLM Judge evaluation")
    
    # File paths
    input_file = "data/output/predictions_first_100.json"
    output_dir = "data/output"
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Load predictions
    try:
        with open(input_file, 'r') as f:
            predictions_data = json.load(f)
        print(f"Loaded {len(predictions_data)} prediction items")
    except FileNotFoundError:
        print(f"Predictions file not found: {input_file}")
        return
    except json.JSONDecodeError as e:
        print(f"Error parsing predictions JSON: {e}")
        return
    
    # Initialize judge
    judge = LLMJudge()
    
    # Evaluate all predictions
    all_results = []
    
    for item_idx, item in enumerate(predictions_data):
        print(f"Processing item {item_idx + 1}/{len(predictions_data)}: {item.get('id', 'unknown')}")
        
        # Process each conversation in the item
        conversations = item.get('conversation', [])
        for conv_idx, _ in enumerate(conversations):
            print(f"  Evaluating conversation {conv_idx + 1}/{len(conversations)}")
            
            result = judge.evaluate_single_prediction(item, conv_idx)
            all_results.append(result)
            
            # Log result
            answer_status = "✓" if result.answer_correct else "✗"
            program_status = "✓" if result.program_correct else "✗"
            print(f"  Answer: {answer_status} | Program: {program_status}")
            print(f"  Expected: {result.expected_answer} | Predicted: {result.predicted_answer}")
            if result.reasoning:
                print(f"  Reasoning: {result.reasoning}")
    
    # Save results
    results_file, summary = save_results(all_results, output_dir)
    
    # Print summary
    print("\n" + "="*50)
    print("EVALUATION SUMMARY")
    print("="*50)
    print(f"Total Questions: {summary['total']}")
    print(f"Answer Accuracy: {summary['answer_correct']}/{summary['total']} ({summary['answer_accuracy']:.1f}%)")
    print(f"Program Accuracy: {summary['program_correct']}/{summary['total']} ({summary['program_accuracy']:.1f}%)")
    print(f"Both Correct: {summary['both_correct']}/{summary['total']} ({summary['overall_accuracy']:.1f}%)")
    print(f"\nResults saved to: {results_file}")
    print("="*50)

if __name__ == "__main__":
    main()