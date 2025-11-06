# PACBench: Properties Affordances Constraints Benchmark

A comprehensive benchmark for evaluating Vision-Language Models (VLMs) on physical attribute understanding across three key capabilities: **Properties**, **Affordances**, and **Constraints**.

Hugging Face: https://huggingface.co/datasets/lens-lab/pacbench

## 📁 Project Structure

```
pacbench/
├── scripts/                    # All Python scripts
│   ├── run_properties.py       # Evaluate property understanding (color, weight, etc.)
│   ├── run_affordance.py       # Evaluate affordance predictions
│   ├── run_constraint.py       # Evaluate constraint reasoning
│   ├── verify_results.py       # LLM-based verification of results
│   ├── generate_performance.py # Generate accuracy summary tables
│   ├── utils.py                # Utility functions for API calls
│   └── config.py               # Configuration and constants
├── run_full_evaluation.sh      # Complete evaluation pipeline script
├── requirements.txt            # Python dependencies
├── pacbench/                   # Dataset directory
│   ├── ground_truth/           # Ground truth annotations
│   ├── open_images/            # Open Images dataset
│   ├── robocasa_objects/       # Simulated object views
│   ├── humanoid/               # Real-world humanoid robot captures
│   └── constraint_images/      # Constraint reasoning images
├── property_results/           # Property evaluation outputs
├── affordance_results/         # Affordance evaluation outputs
├── constraint_results/         # Constraint evaluation outputs
└── evaluations/                # Verification and summary results
```

## 🚀 Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd pacbench
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your API key:
Create a `.env` file in the root directory:
```
OPENROUTER_API_KEY=your_api_key_here
```

## 📊 Usage

### Quick Start: Run Full Evaluation Pipeline

The easiest way to run the complete evaluation pipeline is using the shell script:

```bash
# Run full pipeline with all evaluations (properties, affordances, constraints)
./run_full_evaluation.sh

# With custom models and sample size
./run_full_evaluation.sh meta-llama/llama-4-maverick meta-llama/llama-4-maverick 10 evaluations
```

Arguments:
1. `EVAL_MODEL` - Model for evaluation (default: meta-llama/llama-4-maverick)
2. `VERIFIER_MODEL` - Model for verification (default: meta-llama/llama-4-maverick)
3. `NUM_SAMPLES` - Number of samples per dataset (default: all)
4. `OUTPUT_DIR` - Output directory (default: evaluations)

### Alternative: Run Individual Evaluations

You can also run individual evaluation scripts from the `scripts/` directory:

**Note:** All Python scripts are now in the `scripts/` directory. Change to that directory before running:
```bash
cd scripts/
```

#### Step 1: Run Evaluations

Generate evaluation results by testing your VLM on the benchmark tasks:

#### 1.1 Run Property Evaluations

Evaluate VLM understanding of physical properties across three datasets:

```bash
# Run all property evaluations
python run_properties.py

# Run specific dataset
python run_properties.py --dataset openimages
python run_properties.py --dataset robocasa
python run_properties.py --dataset humanoid

# Customize model and samples
python run_properties.py --model "gpt-4-vision-preview" --num_samples 10

# Custom output directory
python run_properties.py --output_dir my_results
```


#### 1.2 Run Affordance Evaluations

Evaluate VLM predictions of object affordances:

```bash
# Run all affordance evaluations
python run_affordance.py

# Run specific dataset
python run_affordance.py --dataset humanoid
python run_affordance.py --dataset robocasa

# With custom settings
python run_affordance.py --model "claude-3-opus" --num_samples 50
```

#### 1.3 Run Constraint Evaluations

Evaluate VLM reasoning about physical constraints:

```bash
# Run all constraint evaluations
python run_constraints.py

# Run specific dataset
python run_constraints.py --dataset humanoid
python run_constraints.py --dataset simulated

# With custom settings
python run_constraints.py --model "gpt-4" --num_samples 20
```


---

### Step 2: Verify and Generate Summaries

After running evaluations, verify results and generate comprehensive summaries.


**Step 2.1: Verify Results with LLM**

Use an LLM to verify if model outputs match ground truth:

```bash
# Verify all results
python verify_results.py

# Verify specific task
python verify_results.py --task properties
python verify_results.py --task affordances
python verify_results.py --task constraints

# Use different verifier model
python verify_results.py --model "gpt-4" --task all
```

**Output:**
- Semantic matching (CORRECT/INCORRECT/UNCERTAIN)
- Per-instance verification results
- Summary statistics

**Step 2.2: Generate Summary Tables**

Create comprehensive accuracy tables from verification results:

```bash
python generate_summary_tables.py
```

**Generated Tables:**
- Property accuracy by type (COLOR, WEIGHT, etc.)
- Property accuracy by camera view
- Affordance overall accuracy
- Constraint accuracy by type
- Constraint accuracy by camera view
- **Overall benchmark summary** (Properties, Affordances, Constraints)

## 📋 Output Files

### Evaluation Results
- `property_results/openrouter_property_eval_results.csv`
- `property_results/openrouter_robocasa_eval_results.csv`
- `property_results/openrouter_humanoid_eval_results.csv`
- `affordance_results/openrouter_humanoid_affordance_results.csv`
- `affordance_results/openrouter_robocasa_affordance_results.csv`
- `constraint_results/openrouter_humanoid_constraint_results.csv`
- `constraint_results/openrouter_sim_constraint_results.csv`

### Verification Results
- `evaluations/property_verification_results.csv`
- `evaluations/affordance_verification_results.csv`
- `evaluations/constraint_verification_results.csv`

### Summary Tables
- `evaluations/property_summary.csv`
- `evaluations/property_by_camera_summary.csv`
- `evaluations/affordance_summary.csv`
- `evaluations/constraint_summary.csv`
- `evaluations/constraint_by_camera_summary.csv`
- `evaluations/overall_benchmark_summary.csv` ⭐

### Dataset Choices
- **Properties**: `openimages`, `robocasa`, `humanoid`, `all`
- **Affordances**: `humanoid`, `robocasa`, `all`
- **Constraints**: `humanoid`, `simulated`, `all`
- **Verification**: `properties`, `affordances`, `constraints`, `all`


## 🤝 Citation

If you use PACBench in your research, please cite:

```bibtex
@inproceedings{pacbench2025,
  title={PAC Bench: Do Foundation Models Understand Prerequisites for Executing Manipulation Policies?},
  author={Gundawar, Atharva and Sagar, Som and Senanayake, Ransalu},
  booktitle={Proceedings of the 39th Conference on Neural Information Processing Systems (NeurIPS)},
  year={2025}
}
```
## 📜 License

This repository is released under the [MIT License](LICENSE).

Please note that external datasets (e.g., OpenImages, RoboCasa) retain their **own licenses** and terms of use. Users are responsible for complying with those when using the data.

## 🙏 Acknowledgments

- **OpenImages** dataset is used for property evaluation data ([license](https://creativecommons.org/licenses/by/4.0/)).
- **RoboCasa** is used for simulated object views ([project page](https://robocasa.ai)).

---

**Note**: This benchmark requires API access to vision-language models through OpenRouter or compatible services. Ensure you have appropriate API credits before running large-scale evaluations.
