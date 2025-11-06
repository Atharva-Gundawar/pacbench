import os
import pandas as pd
import csv
import random
import argparse
from openai import OpenAI
from config import property_ground_files, PROPERTY_MCQ_OPTIONS
from utils import query_openrouter
from dotenv import load_dotenv


def build_prompt(property_name, options):
    """Builds the property-specific prompt."""
    return (
        f"Evaluate the {property_name.lower()} of the object(s) enclosed within "
        f"the red bounding box in the image.\n\n"
        f"Choose one of the following options:\n{', '.join(options)}\n\n"
        f"Respond only with the chosen option text."
    )


def evaluate_openimages(client, model_name, num_samples, output_csv):
    """Evaluate property understanding on Open Images dataset."""
    print("\nStarting evaluation for Open Images dataset...")
    
    properties_path = "pacbench/ground_truth"
    images_base_path = "pacbench/open_images"
    
    with open(output_csv, "w", newline="") as outfile:
        writer = csv.writer(outfile)
        writer.writerow(["property", "image_filename", "ground_truth_choice", "model_response"])

        for filename in property_ground_files:
            file_path = os.path.join(properties_path, filename)
            try:
                prop = filename.split("_")[-2].upper()
                print(f"\n🔍 Evaluating property: {prop}")

                df = pd.read_csv(file_path)
                print(f"Loaded {filename} with {len(df)} rows.\n")

                options = PROPERTY_MCQ_OPTIONS.get(prop)
                if not options:
                    print(f"No options defined for {prop}. Skipping.")
                    continue

                # Evaluate samples based on num_samples argument
                df_sample = df.head(num_samples) if num_samples else df
                for _, row in df_sample.iterrows():
                    image_filename = str(row["image"]).strip()
                    ground_truth = str(row["choice"]).strip()

                    img_path = os.path.join(images_base_path, f"{image_filename}.jpg")

                    if not os.path.exists(img_path):
                        print(f"image missing for: {image_filename}")
                        continue

                    prompt = build_prompt(prop, options)
                    result = query_openrouter(client, model_name, prompt, img_path)

                    writer.writerow([prop, os.path.basename(img_path), ground_truth, result])
                    print(f"{os.path.basename(img_path)} → {result} | GT: {ground_truth}")

            except Exception as e:
                print(f"Error processing {filename}: {e}")

    print(f"\nOpen Images evaluation complete! Results saved to: {output_csv}")


def evaluate_robocasa(client, model_name, num_samples, output_csv):
    """Evaluate property understanding on RoboCasa dataset."""
    print("\nStarting evaluation for RoboCasa dataset...")
    
    robocasa_path = "pacbench/robocasa_objects/object_views"
    robocasa_gt_file = "pacbench/ground_truth/syn_properties.psv"
    
    ground_truth_df = pd.read_csv(robocasa_gt_file, sep="|")
    ground_truth_df.columns = [c.strip().lower() for c in ground_truth_df.columns]

    with open(output_csv, "w", newline="") as outfile:
        writer = csv.writer(outfile)
        writer.writerow([
            "object_name", "property_name", "ground_truth_category",
            "ground_truth_descriptors", "sampled_image", "model_response"
        ])

        objects_to_process = sorted(os.listdir(robocasa_path))
        if num_samples:
            objects_to_process = objects_to_process[:num_samples]
        
        for obj_name in objects_to_process:
            obj_dir = os.path.join(robocasa_path, obj_name+"/unnamed")
            print(obj_dir)

            # Randomly sample one image for that object
            images = [f for f in os.listdir(obj_dir) if f.lower().endswith(('.png'))]
            if not images:
                print(f"No images found for {obj_name}")
                continue

            sampled_image = random.choice(images)
            img_path = os.path.join(obj_dir, sampled_image)

            # Find ground truth info for that object
            matches = ground_truth_df[ground_truth_df["object_name"].str.lower() == obj_name.lower()]
            if matches.empty:
                print(f"No ground truth found for {obj_name}")
                continue

            matches_sample = matches.head(num_samples) if num_samples else matches
            for _, row in matches_sample.iterrows():
                prop = str(row["property_name"]).strip().upper()
                gt_category = str(row["selected_category"]).strip()
                gt_desc = str(row["selected_descriptors"]).strip()
                options = PROPERTY_MCQ_OPTIONS.get(prop)

                if not options:
                    print(f"No options defined for {prop}. Skipping {obj_name}.")
                    continue

                prompt = build_prompt(prop, options)
                result = query_openrouter(client, model_name, prompt, img_path)

                writer.writerow([
                    obj_name, prop, gt_category, gt_desc,
                    os.path.basename(img_path), result
                ])

                print(f"{obj_name} | {prop} → {result} | GT: {gt_category}: {gt_desc}")

    print(f"\nRoboCasa evaluation complete! Results saved to: {output_csv}")


def evaluate_humanoid(client, model_name, num_samples, output_csv):
    """Evaluate property understanding on Humanoid dataset."""
    print("\nStarting evaluation for Humanoid dataset...")
    
    humanoid_gt_file = "pacbench/ground_truth/robo_properties.psv"
    humanoid_images_path = "pacbench/humanoid/captured_images"
    
    humanoid_df = pd.read_csv(humanoid_gt_file, sep="|")
    humanoid_df.columns = [c.strip().lower() for c in humanoid_df.columns]

    with open(output_csv, "w", newline="") as outfile:
        writer = csv.writer(outfile)
        writer.writerow([
            "property_name", "ground_truth_category", "ground_truth_descriptors",
            "cam0_image", "cam1_image", "response_cam0", "response_cam1"
        ])

        humanoid_sample = humanoid_df.head(num_samples) if num_samples else humanoid_df
        for _, row in humanoid_sample.iterrows():
            prop = str(row["property_name"]).strip().upper()
            gt_category = str(row["selected_category"]).strip()
            gt_desc = str(row["selected_descriptors"]).strip()

            cam0_file = str(row["cam0_file"]).strip()
            cam1_file = str(row["cam1_file"]).strip()

            cam0_path = os.path.join(humanoid_images_path, cam0_file)
            cam1_path = os.path.join(humanoid_images_path, cam1_file)

            options = PROPERTY_MCQ_OPTIONS.get(prop)
            if not options:
                print(f"No options defined for {prop}. Skipping row.")
                continue

            prompt = build_prompt(prop, options)

            result_cam0 = query_openrouter(client, model_name, prompt, cam0_path) if os.path.exists(cam0_path) else "Missing cam0"
            result_cam1 = query_openrouter(client, model_name, prompt, cam1_path) if os.path.exists(cam1_path) else "Missing cam1"

            writer.writerow([
                prop, gt_category, gt_desc,
                os.path.basename(cam0_path), os.path.basename(cam1_path),
                result_cam0, result_cam1
            ])

            print(f"{prop} | GT: {gt_category} | cam0 → {result_cam0} | cam1 → {result_cam1}")

    print(f"\nHumanoid evaluation complete! Results saved to: {output_csv}")


def main():
    """Main function to run property evaluations."""
    load_dotenv()
    
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    if not OPENROUTER_API_KEY:
        raise EnvironmentError("OPENROUTER_API_KEY not set in environment variables.")

    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY)

    # Argument parser
    parser = argparse.ArgumentParser(description="Evaluate VLM property understanding across multiple datasets")
    parser.add_argument("--model", type=str, default="meta-llama/llama-4-maverick",
                        help="Model name to use for evaluation")
    parser.add_argument("--num_samples", type=int, default=None,
                        help="Number of samples to evaluate per dataset (default: all)")
    parser.add_argument("--output_dir", type=str, default="property_results",
                        help="Directory to save results")
    parser.add_argument("--dataset", type=str, choices=["openimages", "robocasa", "humanoid", "all"],
                        default="all", help="Which dataset to evaluate")

    args = parser.parse_args()

    # Create results directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Define output paths
    output_csv_openimages = os.path.join(args.output_dir, "openrouter_property_eval_results.csv")
    output_csv_robocasa = os.path.join(args.output_dir, "openrouter_robocasa_eval_results.csv")
    output_csv_humanoid = os.path.join(args.output_dir, "openrouter_humanoid_eval_results.csv")

    # Run evaluations based on dataset argument
    if args.dataset in ["openimages", "all"]:
        evaluate_openimages(client, args.model, args.num_samples, output_csv_openimages)
    
    if args.dataset in ["robocasa", "all"]:
        evaluate_robocasa(client, args.model, args.num_samples, output_csv_robocasa)
    
    if args.dataset in ["humanoid", "all"]:
        evaluate_humanoid(client, args.model, args.num_samples, output_csv_humanoid)

    print("\nAll evaluations complete!")


if __name__ == "__main__":
    main()
