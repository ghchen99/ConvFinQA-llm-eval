import json
import pandas as pd
import os

def load_and_save_samples(input_file='./train.json', output_file='./processed_train.json'):
    """
    Load samples from train.json, process them into a structured format,
    and save the processed data to a new JSON file.
    
    Args:
        input_file (str): Path to the input JSON file
        output_file (str): Path to save the processed JSON file
    
    Returns:
        list: The processed samples (also saved to file)
    """
    # Load the JSON file
    print(f"Loading data from {input_file}...")
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    print(f"Processing {len(data)} samples...")
    processed_samples = []
    
    for sample in data:
        # Extract financial report components
        # For JSON serialization, convert table to list of dicts instead of DataFrame
        financial_report = {
            'pre_text': sample.get('pre_text', ''),
            'post_text': sample.get('post_text', ''),
            'table': sample.get('table', [])  # Keep as list for JSON serialization
        }
        
        # Extract conversation components
        conversation = []
        questions = sample['annotation']['dialogue_break']
        programs = sample['annotation']['turn_program']
        answers = sample['annotation']['exe_ans_list']
        
        # Create a structured conversation history
        for i in range(len(questions)):
            conversation.append({
                'question': questions[i],
                'expected_program': programs[i] if i < len(programs) else None,
                'expected_answer': answers[i] if i < len(answers) else None
            })
        
        processed_samples.append({
            'financial_report': financial_report,
            'conversation': conversation,
            'id': sample.get('id', '')
        })
    
    # Save processed samples to a new JSON file
    print(f"Saving processed data to {output_file}...")
    with open(output_file, 'w') as f:
        json.dump(processed_samples, f, indent=2)
    
    print(f"Successfully processed and saved {len(processed_samples)} samples.")
    return processed_samples

# Execute the function if run as a script
if __name__ == "__main__":
    load_and_save_samples()