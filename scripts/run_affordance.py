import os
import csv
import pandas as pd
import random
import argparse
from openai import OpenAI
from dotenv import load_dotenv
from utils import query_openrouter


def build_affordance_prompt(object_name: str) -> str:
    """Build prompt for affordance reasoning."""
    return (
        f"What are the affordances of the object '{object_name}'?\n\n"
        f"Respond only with all applicable affordances, separated by commas.\n"
        f"Provide no explanation."
    )


def evaluate_humanoid_affordances(client, model, num_samples, output_csv):
    """Evaluate affordance understanding for Humanoid dataset (dual cam)."""
    print("\nEvaluating affordances for Humanoid dataset...")
    
    humanoid_affordance_gt = "../pacbench/ground_truth/robo_affordances.psv"
    humanoid_images_path = "../pacbench/humanoid/captured_images"
    
    df = pd.read_csv(humanoid_affordance_gt, sep="|")
    df.columns = [c.strip().lower() for c in df.columns]

    with open(output_csv, "w", newline="") as outfile:
        writer = csv.writer(outfile)
        writer.writerow([
            "ground_truth_affordances", "cam0_image", "cam1_image",
            "response_cam0", "response_cam1"
        ])

        df_sample = df.head(num_samples) if num_samples else df
        for _, row in df_sample.iterrows():
            try:
                cam0_file = str(row.get("cam0_file", "")).strip()
                cam1_file = str(row.get("cam1_file", "")).strip()

                if not cam0_file or not cam1_file:
                    print(f"Skipping row with missing cam files")
                    continue

                # Collect affordances from affordance1, affordance2, affordance3 columns
                gt_affordances = [
                    str(a).strip() for a in [
                        row.get("affordance1", ""),
                        row.get("affordance2", ""),
                        row.get("affordance3", "")
                    ]
                    if str(a).strip() != "" and str(a) != "nan"
                ]
                gt_affordances_str = ", ".join(gt_affordances) if gt_affordances else "N/A"

                cam0_path = os.path.join(humanoid_images_path, cam0_file)
                cam1_path = os.path.join(humanoid_images_path, cam1_file)

                prompt = "What are the affordances of the object in the image? Respond only with all applicable affordances, separated by commas. Provide no explanation."

                result_cam0 = (
                    query_openrouter(client, model, prompt, cam0_path)
                    if os.path.exists(cam0_path)
                    else "Missing cam0"
                )
                result_cam1 = (
                    query_openrouter(client, model, prompt, cam1_path)
                    if os.path.exists(cam1_path)
                    else "Missing cam1"
                )

                writer.writerow([
                    gt_affordances_str,
                    os.path.basename(cam0_path),
                    os.path.basename(cam1_path),
                    result_cam0,
                    result_cam1
                ])

                print(f"GT: {gt_affordances_str} | cam0 -> {result_cam0} | cam1 -> {result_cam1}")

            except Exception as e:
                print(f"Error evaluating humanoid affordance row: {e}")

    print(f"Humanoid affordance evaluation complete. Results saved to: {output_csv}")


def evaluate_robocasa_affordances(client, model, num_samples, output_csv):
    """Evaluate affordance understanding for RoboCasa dataset."""
    print("\nEvaluating affordances for RoboCasa dataset...")
    
    robocasa_affordance_gt = "../pacbench/ground_truth/syn_affordance.psv"
    robocasa_path = "../pacbench/robocasa_objects/object_views"
    
    df = pd.read_csv(robocasa_affordance_gt, sep="|")
    df.columns = [c.strip().lower() for c in df.columns]

    with open(output_csv, "w", newline="") as outfile:
        writer = csv.writer(outfile)
        writer.writerow([
            "object_name", "ground_truth_affordances",
            "sampled_image", "model_response",
        ])

        df_sample = df.head(num_samples) if num_samples else df
        for _, row in df_sample.iterrows():
            try:
                obj_name = str(row.get("object_name", "")).strip()
                if not obj_name:
                    continue
                
                # Collect all non-empty affordances
                gt_affordances = [
                    str(a).strip().lower() for a in [
                        row.get("affordance1", ""),
                        row.get("affordance2", ""),
                        row.get("affordance3", "")
                    ]
                    if isinstance(a, str) and a.strip() != "" and a != "nan"
                ]
                if not gt_affordances:
                    continue

                # Find image directory
                obj_dir = os.path.join(robocasa_path, obj_name+"/unnamed")
             
                if not os.path.isdir(obj_dir):
                    print(f"No folder found for {obj_name}")
                    continue
                
                # Randomly sample one image
                images = [f for f in os.listdir(obj_dir) if f.lower().endswith(('.png', '.jpg'))]
                if not images:
                    print(f"No images found for {obj_name}")
                    continue
                sampled_image = random.choice(images)
                img_path = os.path.join(obj_dir, sampled_image)

                # Query the model
                prompt = build_affordance_prompt(obj_name)
                result = query_openrouter(client, model, prompt, img_path).lower()

                writer.writerow([
                    obj_name, ", ".join(gt_affordances),
                    os.path.basename(img_path), result,
                ])

                print(f"{obj_name} → {result} | GT: {gt_affordances}")

            except Exception as e:
                print(f"Error evaluating RoboCasa affordance row: {e}")

    print(f"RoboCasa affordance evaluation complete. Results saved to: {output_csv}")


def main():
    """Main function to run affordance evaluations."""
    load_dotenv()
    
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    if not OPENROUTER_API_KEY:
        raise EnvironmentError("OPENROUTER_API_KEY not set in environment variables.")

    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY)

    # Argument parser
    parser = argparse.ArgumentParser(description="Evaluate VLM affordance understanding across multiple datasets")
    parser.add_argument("--model", type=str, default="meta-llama/llama-4-maverick",
                        help="Model name to use for evaluation")
    parser.add_argument("--num_samples", type=int, default=None,
                        help="Number of samples to evaluate per dataset (default: all)")
    parser.add_argument("--output_dir", type=str, default="../affordance_results",
                        help="Directory to save results")
    parser.add_argument("--dataset", type=str, choices=["humanoid", "robocasa", "all"],
                        default="all", help="Which dataset to evaluate")

    args = parser.parse_args()

    # Create results directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Define output paths
    output_csv_humanoid = os.path.join(args.output_dir, "openrouter_humanoid_affordance_results.csv")
    output_csv_robocasa = os.path.join(args.output_dir, "openrouter_robocasa_affordance_results.csv")

    # Run evaluations based on dataset argument
    if args.dataset in ["humanoid", "all"]:
        evaluate_humanoid_affordances(client, args.model, args.num_samples, output_csv_humanoid)
    
    if args.dataset in ["robocasa", "all"]:
        evaluate_robocasa_affordances(client, args.model, args.num_samples, output_csv_robocasa)

    print("\nAll evaluations complete!")


if __name__ == "__main__":
    main()
