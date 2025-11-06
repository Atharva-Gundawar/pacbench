import os
import csv
import pandas as pd
import argparse
import glob
from openai import OpenAI
from dotenv import load_dotenv


def verify_property_match(client, model, ground_truth, model_response):
    """Use LLM to verify if model response matches ground truth for properties."""
    prompt = f"""You are evaluating if a model's response matches the ground truth for a property classification task.

Ground Truth: {ground_truth}
Model Response: {model_response}

Does the model response match or align with the ground truth? Consider semantic similarity and variations in wording.

Respond with ONLY one of these options:
- "CORRECT" if the response matches or closely aligns with the ground truth
- "INCORRECT" if the response does not match or contradicts the ground truth"""

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50,
            temperature=0.0,
        )
        result = resp.choices[0].message.content.strip().upper()
        # Ensure we only get one of the valid responses
        if "CORRECT" in result and "INCORRECT" not in result:
            return "CORRECT"
        elif "INCORRECT" in result:
            return "INCORRECT"
        else:
            return "UNCERTAIN"
    except Exception as e:
        return f"ERROR: {e}"


def verify_affordance_match(client, model, ground_truth, model_response):
    """Use LLM to verify if model response matches ground truth for affordances."""
    prompt = f"""You are evaluating if a model's affordance predictions match the ground truth affordances.

Ground Truth Affordances: {ground_truth}
Model Response: {model_response}

Does the model response capture the same affordances as the ground truth? The model may use different wording but should convey the same affordances.

Respond with ONLY one of these options:
- "CORRECT" if the response captures all or most key affordances correctly
- "INCORRECT" if the response is wrong or misses the affordances"""

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50,
            temperature=0.0,
        )
        result = resp.choices[0].message.content.strip().upper()
        if "CORRECT" in result and "INCORRECT" not in result:
            return "CORRECT"
        elif "INCORRECT" in result:
            return "INCORRECT"
        else:
            return "UNCERTAIN"
    except Exception as e:
        return f"ERROR: {e}"


def verify_constraint_match(client, model, ground_truth, model_response):
    """Use LLM to verify if model response matches ground truth for constraints."""
    prompt = f"""You are evaluating if a model's constraint reasoning matches the expected answer.

Ground Truth Answer: {ground_truth}
Model Response: {model_response}

Does the model response correctly identify whether there is a constraint or not? Consider the semantic meaning.

Respond with ONLY one of these options:
- "CORRECT" if the response correctly identifies the constraint (or lack thereof)
- "INCORRECT" if the response incorrectly identifies or misses the constraint"""

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50,
            temperature=0.0,
        )
        result = resp.choices[0].message.content.strip().upper()
        if "CORRECT" in result and "INCORRECT" not in result:
            return "CORRECT"
        elif "INCORRECT" in result:
            return "INCORRECT"
        else:
            return "UNCERTAIN"
    except Exception as e:
        return f"ERROR: {e}"


def verify_properties(client, model, input_dir, output_file):
    """Verify all property evaluation results."""
    print("\n" + "="*60)
    print("Verifying Property Evaluations")
    print("="*60)
    
    all_results = []
    csv_files = glob.glob(os.path.join(input_dir, "*.csv"))
    
    for csv_file in csv_files:
        print(f"\nProcessing: {os.path.basename(csv_file)}")
        df = pd.read_csv(csv_file)
        
        for idx, row in df.iterrows():
            # Handle different CSV formats
            if 'ground_truth_choice' in df.columns:
                # OpenImages format
                ground_truth = row['ground_truth_choice']
                model_response = row['model_response']
                identifier = row.get('image_filename', f'row_{idx}')
                property_type = row.get('property', 'UNKNOWN')
            elif 'ground_truth_category' in df.columns:
                # RoboCasa/Humanoid format
                ground_truth = row['ground_truth_category']
                identifier = row.get('object_name', row.get('cam0_image', f'row_{idx}'))
                property_type = row.get('property_name', 'UNKNOWN')
                
                # Check for multiple camera responses
                if 'response_cam0' in df.columns and 'response_cam1' in df.columns:
                    # Verify both cameras
                    verification_cam0 = verify_property_match(client, model, ground_truth, row['response_cam0'])
                    verification_cam1 = verify_property_match(client, model, ground_truth, row['response_cam1'])
                    
                    all_results.append({
                        'source_file': os.path.basename(csv_file),
                        'property_type': property_type,
                        'identifier': identifier,
                        'ground_truth': ground_truth,
                        'model_response': row['response_cam0'],
                        'camera': 'cam0',
                        'verification': verification_cam0
                    })
                    all_results.append({
                        'source_file': os.path.basename(csv_file),
                        'property_type': property_type,
                        'identifier': identifier,
                        'ground_truth': ground_truth,
                        'model_response': row['response_cam1'],
                        'camera': 'cam1',
                        'verification': verification_cam1
                    })
                    print(f"  {identifier} - cam0: {verification_cam0}, cam1: {verification_cam1}")
                    continue
                else:
                    model_response = row['model_response']
            else:
                continue
            
            verification = verify_property_match(client, model, ground_truth, model_response)
            all_results.append({
                'source_file': os.path.basename(csv_file),
                'property_type': property_type,
                'identifier': identifier,
                'ground_truth': ground_truth,
                'model_response': model_response,
                'camera': 'N/A',
                'verification': verification
            })
            print(f"  {identifier}: {verification}")
    
    # Save results
    df_results = pd.DataFrame(all_results)
    df_results.to_csv(output_file, index=False)
    
    # Print summary
    print(f"\n{'='*60}")
    print("Property Verification Summary:")
    print(f"  Total: {len(all_results)}")
    print(f"  Correct: {len(df_results[df_results['verification'] == 'CORRECT'])}")
    print(f"  Incorrect: {len(df_results[df_results['verification'] == 'INCORRECT'])}")
    print(f"  Uncertain: {len(df_results[df_results['verification'] == 'UNCERTAIN'])}")
    print(f"Results saved to: {output_file}")


def verify_affordances(client, model, input_dir, output_file):
    """Verify all affordance evaluation results."""
    print("\n" + "="*60)
    print("Verifying Affordance Evaluations")
    print("="*60)
    
    all_results = []
    csv_files = glob.glob(os.path.join(input_dir, "*.csv"))
    
    for csv_file in csv_files:
        print(f"\nProcessing: {os.path.basename(csv_file)}")
        df = pd.read_csv(csv_file)
        
        for idx, row in df.iterrows():
            ground_truth = row.get('ground_truth_affordances', 'N/A')
            identifier = row.get('object_name', row.get('cam0_image', f'row_{idx}'))
            
            # Check for multiple camera responses
            if 'response_cam0' in df.columns and 'response_cam1' in df.columns:
                verification_cam0 = verify_affordance_match(client, model, ground_truth, row['response_cam0'])
                verification_cam1 = verify_affordance_match(client, model, ground_truth, row['response_cam1'])
                
                all_results.append({
                    'source_file': os.path.basename(csv_file),
                    'identifier': identifier,
                    'ground_truth': ground_truth,
                    'model_response': row['response_cam0'],
                    'camera': 'cam0',
                    'verification': verification_cam0
                })
                all_results.append({
                    'source_file': os.path.basename(csv_file),
                    'identifier': identifier,
                    'ground_truth': ground_truth,
                    'model_response': row['response_cam1'],
                    'camera': 'cam1',
                    'verification': verification_cam1
                })
                print(f"  {identifier} - cam0: {verification_cam0}, cam1: {verification_cam1}")
            else:
                model_response = row.get('model_response', 'N/A')
                verification = verify_affordance_match(client, model, ground_truth, model_response)
                all_results.append({
                    'source_file': os.path.basename(csv_file),
                    'identifier': identifier,
                    'ground_truth': ground_truth,
                    'model_response': model_response,
                    'camera': 'N/A',
                    'verification': verification
                })
                print(f"  {identifier}: {verification}")
    
    # Save results
    df_results = pd.DataFrame(all_results)
    df_results.to_csv(output_file, index=False)
    
    # Print summary
    print(f"\n{'='*60}")
    print("Affordance Verification Summary:")
    print(f"  Total: {len(all_results)}")
    print(f"  Correct: {len(df_results[df_results['verification'] == 'CORRECT'])}")
    print(f"  Incorrect: {len(df_results[df_results['verification'] == 'INCORRECT'])}")
    print(f"  Uncertain: {len(df_results[df_results['verification'] == 'UNCERTAIN'])}")
    print(f"Results saved to: {output_file}")


def verify_constraints(client, model, input_dir, output_file):
    """Verify all constraint evaluation results."""
    print("\n" + "="*60)
    print("Verifying Constraint Evaluations")
    print("="*60)
    
    all_results = []
    csv_files = glob.glob(os.path.join(input_dir, "*.csv"))
    
    for csv_file in csv_files:
        print(f"\nProcessing: {os.path.basename(csv_file)}")
        df = pd.read_csv(csv_file)
        
        for idx, row in df.iterrows():
            ground_truth = row.get('ground_truth_answer', row.get('verification_prompt', 'N/A'))
            identifier = row.get('question', row.get('constraint_key', f'row_{idx}'))
            constraint_type = row.get('constraint_key', 'humanoid_task')
            
            # Check for multiple camera responses
            if 'response_cam0' in df.columns and 'response_cam1' in df.columns:
                verification_cam0 = verify_constraint_match(client, model, ground_truth, row['response_cam0'])
                verification_cam1 = verify_constraint_match(client, model, ground_truth, row['response_cam1'])
                verification_both = verify_constraint_match(client, model, ground_truth, row.get('response_both_cams', 'N/A'))
                
                all_results.append({
                    'source_file': os.path.basename(csv_file),
                    'constraint_type': constraint_type,
                    'identifier': identifier,
                    'ground_truth': ground_truth,
                    'model_response': row['response_cam0'],
                    'camera': 'cam0',
                    'verification': verification_cam0
                })
                all_results.append({
                    'source_file': os.path.basename(csv_file),
                    'constraint_type': constraint_type,
                    'identifier': identifier,
                    'ground_truth': ground_truth,
                    'model_response': row['response_cam1'],
                    'camera': 'cam1',
                    'verification': verification_cam1
                })
                if 'response_both_cams' in df.columns:
                    all_results.append({
                        'source_file': os.path.basename(csv_file),
                        'constraint_type': constraint_type,
                        'identifier': identifier,
                        'ground_truth': ground_truth,
                        'model_response': row['response_both_cams'],
                        'camera': 'both',
                        'verification': verification_both
                    })
                print(f"  {identifier[:50]}... - cam0: {verification_cam0}, cam1: {verification_cam1}, both: {verification_both}")
            else:
                model_response = row.get('model_response', 'N/A')
                verification = verify_constraint_match(client, model, ground_truth, model_response)
                all_results.append({
                    'source_file': os.path.basename(csv_file),
                    'constraint_type': constraint_type,
                    'identifier': identifier,
                    'ground_truth': ground_truth,
                    'model_response': model_response,
                    'camera': 'N/A',
                    'verification': verification
                })
                print(f"  {identifier[:50]}...: {verification}")
    
    # Save results
    df_results = pd.DataFrame(all_results)
    df_results.to_csv(output_file, index=False)
    
    # Print summary
    print(f"\n{'='*60}")
    print("Constraint Verification Summary:")
    print(f"  Total: {len(all_results)}")
    print(f"  Correct: {len(df_results[df_results['verification'] == 'CORRECT'])}")
    print(f"  Incorrect: {len(df_results[df_results['verification'] == 'INCORRECT'])}")
    print(f"  Uncertain: {len(df_results[df_results['verification'] == 'UNCERTAIN'])}")
    print(f"Results saved to: {output_file}")


def main():
    """Main function to run LLM verification."""
    load_dotenv()
    
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    if not OPENROUTER_API_KEY:
        raise EnvironmentError("OPENROUTER_API_KEY not set in environment variables.")

    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY)

    # Argument parser
    parser = argparse.ArgumentParser(description="Verify VLM evaluation results using LLM")
    parser.add_argument("--model", type=str, default="meta-llama/llama-4-maverick",
                        help="Model name to use for verification")
    parser.add_argument("--property_dir", type=str, default="../property_results",
                        help="Directory containing property evaluation CSVs")
    parser.add_argument("--affordance_dir", type=str, default="../affordance_results",
                        help="Directory containing affordance evaluation CSVs")
    parser.add_argument("--constraint_dir", type=str, default="../constraint_results",
                        help="Directory containing constraint evaluation CSVs")
    parser.add_argument("--output_dir", type=str, default="../evaluations",
                        help="Directory to save verification results")
    parser.add_argument("--task", type=str, choices=["properties", "affordances", "constraints", "all"],
                        default="all", help="Which task to verify")

    args = parser.parse_args()

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Run verifications based on task argument
    if args.task in ["properties", "all"]:
        output_file = os.path.join(args.output_dir, "property_verification_results.csv")
        verify_properties(client, args.model, args.property_dir, output_file)
    
    if args.task in ["affordances", "all"]:
        output_file = os.path.join(args.output_dir, "affordance_verification_results.csv")
        verify_affordances(client, args.model, args.affordance_dir, output_file)
    
    if args.task in ["constraints", "all"]:
        output_file = os.path.join(args.output_dir, "constraint_verification_results.csv")
        verify_constraints(client, args.model, args.constraint_dir, output_file)

    print("\n" + "="*60)
    print("All verifications complete!")
    print("="*60)


if __name__ == "__main__":
    main()

