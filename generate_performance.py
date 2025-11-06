import os
import pandas as pd
import argparse
from tabulate import tabulate


def generate_property_summary(verification_csv):
    """Generate property accuracy summary table."""
    df = pd.read_csv(verification_csv)
    
    if 'property_type' not in df.columns:
        print("Warning: property_type column not found. Re-run verify_results.py with updated version.")
        return None
    
    # Calculate accuracy by property type
    summary = []
    property_types = df['property_type'].unique()
    
    for prop_type in sorted(property_types):
        prop_data = df[df['property_type'] == prop_type]
        total = len(prop_data)
        correct = len(prop_data[prop_data['verification'] == 'CORRECT'])
        accuracy = (correct / total * 100) if total > 0 else 0
        
        summary.append({
            'Property': prop_type,
            'Total': total,
            'Correct': correct,
            'Accuracy (%)': f"{accuracy:.2f}"
        })
    
    # Add overall accuracy
    total_all = len(df)
    correct_all = len(df[df['verification'] == 'CORRECT'])
    accuracy_all = (correct_all / total_all * 100) if total_all > 0 else 0
    
    summary.append({
        'Property': 'OVERALL',
        'Total': total_all,
        'Correct': correct_all,
        'Accuracy (%)': f"{accuracy_all:.2f}"
    })
    
    return pd.DataFrame(summary)


def generate_property_by_camera_summary(verification_csv):
    """Generate property accuracy by camera view."""
    df = pd.read_csv(verification_csv)
    
    if 'camera' not in df.columns:
        return None
    
    summary = []
    cameras = df['camera'].dropna().unique()
    
    for camera in sorted(cameras, key=str):
        cam_data = df[df['camera'] == camera]
        total = len(cam_data)
        correct = len(cam_data[cam_data['verification'] == 'CORRECT'])
        accuracy = (correct / total * 100) if total > 0 else 0
        
        summary.append({
            'Camera': camera,
            'Total': total,
            'Correct': correct,
            'Accuracy (%)': f"{accuracy:.2f}"
        })
    
    return pd.DataFrame(summary)


def generate_constraint_summary(verification_csv):
    """Generate constraint accuracy summary table."""
    df = pd.read_csv(verification_csv)
    
    if 'constraint_type' not in df.columns:
        print("Warning: constraint_type column not found. Re-run verify_results.py with updated version.")
        return None
    
    # Calculate accuracy by constraint type
    summary = []
    constraint_types = df['constraint_type'].unique()
    
    for const_type in sorted(constraint_types):
        const_data = df[df['constraint_type'] == const_type]
        total = len(const_data)
        correct = len(const_data[const_data['verification'] == 'CORRECT'])
        accuracy = (correct / total * 100) if total > 0 else 0
        
        summary.append({
            'Constraint Type': const_type,
            'Total': total,
            'Correct': correct,
            'Accuracy (%)': f"{accuracy:.2f}"
        })
    
    # Add overall accuracy
    total_all = len(df)
    correct_all = len(df[df['verification'] == 'CORRECT'])
    accuracy_all = (correct_all / total_all * 100) if total_all > 0 else 0
    
    summary.append({
        'Constraint Type': 'OVERALL',
        'Total': total_all,
        'Correct': correct_all,
        'Accuracy (%)': f"{accuracy_all:.2f}"
    })
    
    return pd.DataFrame(summary)


def generate_constraint_by_camera_summary(verification_csv):
    """Generate constraint accuracy by camera view."""
    df = pd.read_csv(verification_csv)
    
    if 'camera' not in df.columns:
        return None
    
    summary = []
    cameras = df['camera'].dropna().unique()
    
    for camera in sorted(cameras, key=str):
        cam_data = df[df['camera'] == camera]
        total = len(cam_data)
        correct = len(cam_data[cam_data['verification'] == 'CORRECT'])
        accuracy = (correct / total * 100) if total > 0 else 0
        
        summary.append({
            'Camera': camera,
            'Total': total,
            'Correct': correct,
            'Accuracy (%)': f"{accuracy:.2f}"
        })
    
    return pd.DataFrame(summary)


def generate_affordance_summary(verification_csv):
    """Generate affordance accuracy summary table."""
    df = pd.read_csv(verification_csv)
    
    # Overall accuracy
    total = len(df)
    correct = len(df[df['verification'] == 'CORRECT'])
    accuracy = (correct / total * 100) if total > 0 else 0
    
    summary = [{
        'Metric': 'Overall Affordance Accuracy',
        'Total': total,
        'Correct': correct,
        'Accuracy (%)': f"{accuracy:.2f}"
    }]
    
    # By camera if available
    if 'camera' in df.columns:
        cameras = df['camera'].dropna().unique()
        for camera in sorted(cameras, key=str):
            cam_data = df[df['camera'] == camera]
            total_cam = len(cam_data)
            correct_cam = len(cam_data[cam_data['verification'] == 'CORRECT'])
            accuracy_cam = (correct_cam / total_cam * 100) if total_cam > 0 else 0
            
            summary.append({
                'Metric': f'Camera {camera}',
                'Total': total_cam,
                'Correct': correct_cam,
                'Accuracy (%)': f"{accuracy_cam:.2f}"
            })
    
    return pd.DataFrame(summary)


def main():
    parser = argparse.ArgumentParser(description="Generate summary tables from verification results")
    parser.add_argument("--eval_dir", type=str, default="evaluations",
                        help="Directory containing verification CSVs")
    parser.add_argument("--output_dir", type=str, default="evaluations",
                        help="Directory to save summary tables")
    
    args = parser.parse_args()
    
    # File paths
    property_csv = os.path.join(args.eval_dir, "property_verification_results.csv")
    affordance_csv = os.path.join(args.eval_dir, "affordance_verification_results.csv")
    constraint_csv = os.path.join(args.eval_dir, "constraint_verification_results.csv")
    
    print("\n" + "="*80)
    print("GENERATING SUMMARY TABLES")
    print("="*80)
    
    # Property Summary
    if os.path.exists(property_csv):
        print("\n" + "="*80)
        print("PROPERTY EVALUATION SUMMARY")
        print("="*80)
        
        prop_summary = generate_property_summary(property_csv)
        if prop_summary is not None:
            print("\n### Property Accuracy by Type:")
            print(tabulate(prop_summary, headers='keys', tablefmt='grid', showindex=False))
            prop_summary.to_csv(os.path.join(args.output_dir, "property_summary.csv"), index=False)
        
        prop_cam_summary = generate_property_by_camera_summary(property_csv)
        if prop_cam_summary is not None:
            print("\n### Property Accuracy by Camera:")
            print(tabulate(prop_cam_summary, headers='keys', tablefmt='grid', showindex=False))
            prop_cam_summary.to_csv(os.path.join(args.output_dir, "property_by_camera_summary.csv"), index=False)
    
    # Affordance Summary
    if os.path.exists(affordance_csv):
        print("\n" + "="*80)
        print("AFFORDANCE EVALUATION SUMMARY")
        print("="*80)
        
        aff_summary = generate_affordance_summary(affordance_csv)
        if aff_summary is not None:
            print(tabulate(aff_summary, headers='keys', tablefmt='grid', showindex=False))
            aff_summary.to_csv(os.path.join(args.output_dir, "affordance_summary.csv"), index=False)
    
    # Constraint Summary
    if os.path.exists(constraint_csv):
        print("\n" + "="*80)
        print("CONSTRAINT EVALUATION SUMMARY")
        print("="*80)
        
        const_summary = generate_constraint_summary(constraint_csv)
        if const_summary is not None:
            print("\n### Constraint Accuracy by Type:")
            print(tabulate(const_summary, headers='keys', tablefmt='grid', showindex=False))
            const_summary.to_csv(os.path.join(args.output_dir, "constraint_summary.csv"), index=False)
        
        const_cam_summary = generate_constraint_by_camera_summary(constraint_csv)
        if const_cam_summary is not None:
            print("\n### Constraint Accuracy by Camera:")
            print(tabulate(const_cam_summary, headers='keys', tablefmt='grid', showindex=False))
            const_cam_summary.to_csv(os.path.join(args.output_dir, "constraint_by_camera_summary.csv"), index=False)
    
    print("\n" + "="*80)
    print("SUMMARY TABLES SAVED")
    print("="*80)
    print(f"Location: {args.output_dir}/")
    print("Files:")
    print("  - property_summary.csv")
    print("  - property_by_camera_summary.csv")
    print("  - affordance_summary.csv")
    print("  - constraint_summary.csv")
    print("  - constraint_by_camera_summary.csv")
    print("="*80)
    
    # Generate overall summary across all tasks
    print("\n" + "="*80)
    print("OVERALL BENCHMARK SUMMARY")
    print("="*80)
    
    overall_summary = []
    
    # Property accuracy
    if os.path.exists(property_csv):
        df_prop = pd.read_csv(property_csv)
        total_prop = len(df_prop)
        correct_prop = len(df_prop[df_prop['verification'] == 'CORRECT'])
        accuracy_prop = (correct_prop / total_prop * 100) if total_prop > 0 else 0
        overall_summary.append({
            'Task': 'Properties',
            'Total': total_prop,
            'Correct': correct_prop,
            'Accuracy (%)': f"{accuracy_prop:.2f}"
        })
    
    # Affordance accuracy
    if os.path.exists(affordance_csv):
        df_aff = pd.read_csv(affordance_csv)
        total_aff = len(df_aff)
        correct_aff = len(df_aff[df_aff['verification'] == 'CORRECT'])
        accuracy_aff = (correct_aff / total_aff * 100) if total_aff > 0 else 0
        overall_summary.append({
            'Task': 'Affordances',
            'Total': total_aff,
            'Correct': correct_aff,
            'Accuracy (%)': f"{accuracy_aff:.2f}"
        })
    
    # Constraint accuracy
    if os.path.exists(constraint_csv):
        df_const = pd.read_csv(constraint_csv)
        total_const = len(df_const)
        correct_const = len(df_const[df_const['verification'] == 'CORRECT'])
        accuracy_const = (correct_const / total_const * 100) if total_const > 0 else 0
        overall_summary.append({
            'Task': 'Constraints',
            'Total': total_const,
            'Correct': correct_const,
            'Accuracy (%)': f"{accuracy_const:.2f}"
        })
    
    if overall_summary:
        df_overall = pd.DataFrame(overall_summary)
        print(tabulate(df_overall, headers='keys', tablefmt='grid', showindex=False))
        df_overall.to_csv(os.path.join(args.output_dir, "overall_benchmark_summary.csv"), index=False)
        print(f"\nOverall summary saved to: {os.path.join(args.output_dir, 'overall_benchmark_summary.csv')}")
    
    print("="*80)


if __name__ == "__main__":
    main()

