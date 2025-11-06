# PACBench: Physical Attribute Comprehension Benchmark

A comprehensive benchmark for evaluating Vision-Language Models (VLMs) on physical attribute understanding across three key capabilities: **Properties**, **Affordances**, and **Constraints**.

## 📁 Project Structure

```
pacbench/
├── run_properties.py           # Evaluate property understanding (color, weight, etc.)
├── run_affordances.py          # Evaluate affordance predictions
├── run_constraints.py          # Evaluate constraint reasoning
├── utils.py                    # Utility functions for API calls
├── config.py                   # Configuration and constants
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

### 1. Run Property Evaluations

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

**Evaluated Properties:**
- COLOR, WEIGHT, HARDNESS, ORIENTATION
- CONSUMABILITY, COMPLEXITY, CAPACITY
- CONTENTS, SEALING, STICKINESS, etc.

### 2. Run Affordance Evaluations

Evaluate VLM predictions of object affordances:

```bash
# Run all affordance evaluations
python run_affordances.py

# Run specific dataset
python run_affordances.py --dataset humanoid
python run_affordances.py --dataset robocasa

# With custom settings
python run_affordances.py --model "claude-3-opus" --num_samples 50
```

### 3. Run Constraint Evaluations

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

