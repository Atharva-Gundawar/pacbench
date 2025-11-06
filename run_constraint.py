import os
import csv
import pandas as pd
import argparse
from openai import OpenAI
from dotenv import load_dotenv
from utils import query_openrouter, query_openrouter_multi_image


def evaluate_humanoid_constraints(client, model, num_samples, output_csv):
    """Evaluate constraint reasoning for Humanoid dataset (dual cam)."""
    print("\nEvaluating constraints for Humanoid dataset...")
    
    humanoid_constraints_gt = "pacbench/ground_truth/robo_constraints.psv"
    humanoid_images_path = "pacbench/humanoid/captured_images"
    
    df = pd.read_csv(humanoid_constraints_gt, sep="|")
    df.columns = [c.strip().lower() for c in df.columns]

    with open(output_csv, "w", newline="") as outfile:
        writer = csv.writer(outfile)
        writer.writerow([
            "question", "ground_truth_answer",
            "cam0_image", "cam1_image",
            "response_cam0", "response_cam1", "response_both_cams"
        ])

        df_sample = df.head(num_samples) if num_samples else df
        for _, row in df_sample.iterrows():
            try:
                question = str(row.get("question", "")).strip()
                answer = str(row.get("answer", "")).strip()
                cam0_file = str(row.get("cam0_file", "")).strip()
                cam1_file = str(row.get("cam1_file", "")).strip()

                cam0_path = os.path.join(humanoid_images_path, cam0_file)
                cam1_path = os.path.join(humanoid_images_path, cam1_file)

                if not os.path.exists(cam0_path) and not os.path.exists(cam1_path):
                    print(f"Skipping: missing both cams for {question}")
                    continue

                # --- use the unified candidate prompt ---
                candidate_prompt = (
                    f"Given the image(s), tell me if there is any constraint that would stop us "
                    f"from doing the following (Answer in 1 very short line): {question}"
                )

                # Query both camera views individually
                result_cam0 = (
                    query_openrouter(client, model, candidate_prompt, cam0_path)
                    if os.path.exists(cam0_path)
                    else "Missing cam0"
                )
                result_cam1 = (
                    query_openrouter(client, model, candidate_prompt, cam1_path)
                    if os.path.exists(cam1_path)
                    else "Missing cam1"
                )

                # Query with both cameras together
                available_cams = []
                if os.path.exists(cam0_path):
                    available_cams.append(cam0_path)
                if os.path.exists(cam1_path):
                    available_cams.append(cam1_path)
                
                result_both = (
                    query_openrouter_multi_image(client, model, candidate_prompt, available_cams)
                    if available_cams
                    else "No cameras available"
                )

                writer.writerow([
                    question, answer,
                    os.path.basename(cam0_path), os.path.basename(cam1_path),
                    result_cam0, result_cam1, result_both
                ])
                print(f"Q: {question}\ncam0 → {result_cam0}\ncam1 → {result_cam1}\nboth → {result_both}\n")

            except Exception as e:
                print(f"Error processing humanoid constraint row: {e}")

    print(f"Humanoid constraint evaluation complete. Results saved to: {output_csv}")


def evaluate_sim_constraints(client, model, num_samples, output_csv):
    """Evaluate simulated constraint reasoning (MuJoCo / RoboCasa-style) with multi-view support."""
    print("\nEvaluating simulated constraint dataset...")
    
    sim_constraints_gt = "pacbench/ground_truth/syn_constraints.psv"
    sim_images_path = "pacbench/constraint_images"
    
    df = pd.read_csv(sim_constraints_gt, sep="|")
    df.columns = [c.strip().lower() for c in df.columns]

    with open(output_csv, "w", newline="") as outfile:
        writer = csv.writer(outfile)
        writer.writerow([
            "constraint_key", "view", "prompt", "verification_prompt",
            "image_file", "model_response"
        ])

        df_sample = df.head(num_samples) if num_samples else df
        for _, row in df_sample.iterrows():
            try:
                key = str(row.get("key", "")).strip()
                question = str(row.get("prompt", "")).strip()
                verification_prompt = str(row.get("verification_prompt", "")).strip()

                # Constraint folder path (e.g. constraint_images/stack_bottom)
                constraint_dir = os.path.join(sim_images_path, key)
                if not os.path.isdir(constraint_dir):
                    print(f"No folder found for constraint key: {key}")
                    continue

                # Each constraint folder has subfolders: agentview, frontview, sideview
                for view in ["agentview", "frontview", "sideview"]:
                    view_path = os.path.join(constraint_dir, view)
                    if not os.path.isdir(view_path):
                        continue

                    images = [f for f in os.listdir(view_path) if f.lower().endswith(('.png', '.jpg'))]
                    if not images:
                        print(f"No images found for {key}/{view}")
                        continue

                    for img_name in images:
                        img_path = os.path.join(view_path, img_name)

                        # Unified candidate prompt from your template
                        candidate_prompt = (
                            f"Given the image(s), tell me if there is any constraint that would stop us "
                            f"from doing the following (Answer in 1 very short line): {question}"
                        )

                        result = query_openrouter(client, model, candidate_prompt, img_path)

                        writer.writerow([
                            key, view, question, verification_prompt,
                            os.path.basename(img_path), result
                        ])

                        print(f"{key}/{view} | {img_name} → {result}")

            except Exception as e:
                print(f"Error processing simulated constraint row: {e}")

    print(f"Simulated constraint evaluation complete. Results saved to: {output_csv}")


def main():
    """Main function to run constraint evaluations."""
    load_dotenv()
    
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    if not OPENROUTER_API_KEY:
        raise EnvironmentError("OPENROUTER_API_KEY not set in environment variables.")

    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY)

    # Argument parser
    parser = argparse.ArgumentParser(description="Evaluate VLM constraint reasoning across multiple datasets")
    parser.add_argument("--model", type=str, default="meta-llama/llama-4-maverick",
                        help="Model name to use for evaluation")
    parser.add_argument("--num_samples", type=int, default=None,
                        help="Number of samples to evaluate per dataset (default: all)")
    parser.add_argument("--output_dir", type=str, default="constraint_results",
                        help="Directory to save results")
    parser.add_argument("--dataset", type=str, choices=["humanoid", "simulated", "all"],
                        default="all", help="Which dataset to evaluate")

    args = parser.parse_args()

    # Create results directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Define output paths
    output_csv_humanoid = os.path.join(args.output_dir, "openrouter_humanoid_constraint_results.csv")
    output_csv_sim = os.path.join(args.output_dir, "openrouter_sim_constraint_results.csv")

    # Run evaluations based on dataset argument
    if args.dataset in ["humanoid", "all"]:
        evaluate_humanoid_constraints(client, args.model, args.num_samples, output_csv_humanoid)
    
    if args.dataset in ["simulated", "all"]:
        evaluate_sim_constraints(client, args.model, args.num_samples, output_csv_sim)

    print("\nAll evaluations complete!")


if __name__ == "__main__":
    main()
