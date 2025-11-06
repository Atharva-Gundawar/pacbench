#!/bin/bash
# PACBench Full Evaluation Pipeline
# Runs evaluations, verification, and generates summary tables

echo "================================================================================"
echo "PACBENCH FULL EVALUATION PIPELINE"


# Parse command line arguments
EVAL_MODEL="${1:-meta-llama/llama-4-maverick}"
VERIFIER_MODEL="${2:-meta-llama/llama-4-maverick}"
NUM_SAMPLES="${3:-}"
OUTPUT_DIR="${4:-evaluations}"

echo "Evaluation Model: $EVAL_MODEL"
echo "Verifier Model: $VERIFIER_MODEL"
echo "Number of Samples: ${NUM_SAMPLES:-all}"
echo "Output Directory: $OUTPUT_DIR"
echo "================================================================================"

# Change to scripts directory
cd scripts || exit 1

# Step 1: Run Property Evaluations
echo ""
echo "================================================================================"
echo "STEP 1: Running Property Evaluations"
echo "================================================================================"
if [ -z "$NUM_SAMPLES" ]; then
    python run_properties.py --model "$EVAL_MODEL" --dataset all
else
    python run_properties.py --model "$EVAL_MODEL" --dataset all --num_samples "$NUM_SAMPLES"
fi

if [ $? -ne 0 ]; then
    echo "ERROR: Property evaluation failed!"
    exit 1
fi

# Step 2: Run Affordance Evaluations
echo ""
echo "================================================================================"
echo "STEP 2: Running Affordance Evaluations"
echo "================================================================================"
if [ -z "$NUM_SAMPLES" ]; then
    python run_affordance.py --model "$EVAL_MODEL" --dataset all
else
    python run_affordance.py --model "$EVAL_MODEL" --dataset all --num_samples "$NUM_SAMPLES"
fi

if [ $? -ne 0 ]; then
    echo "ERROR: Affordance evaluation failed!"
    exit 1
fi

# Step 3: Run Constraint Evaluations
echo ""
echo "================================================================================"
echo "STEP 3: Running Constraint Evaluations"
echo "================================================================================"
if [ -z "$NUM_SAMPLES" ]; then
    python run_constraint.py --model "$EVAL_MODEL" --dataset all
else
    python run_constraint.py --model "$EVAL_MODEL" --dataset all --num_samples "$NUM_SAMPLES"
fi

if [ $? -ne 0 ]; then
    echo "ERROR: Constraint evaluation failed!"
    exit 1
fi

# Step 4: Run verification
echo ""
echo "================================================================================"
echo "STEP 4: Verifying Results with LLM"
echo "================================================================================"
python verify_results.py \
    --model "$VERIFIER_MODEL" \
    --output_dir "../$OUTPUT_DIR" \
    --task all

if [ $? -ne 0 ]; then
    echo "ERROR: Verification failed!"
    exit 1
fi

# Step 5: Generate summary tables
echo ""
echo "================================================================================"
echo "STEP 5: Generating Summary Tables"
echo "================================================================================"
python generate_performance.py \
    --eval_dir "../$OUTPUT_DIR" \
    --output_dir "../$OUTPUT_DIR"

if [ $? -ne 0 ]; then
    echo "ERROR: Summary generation failed!"
    exit 1
fi

# Return to root directory
cd ..

# Success message
echo ""
echo "================================================================================"
echo "✓ FULL EVALUATION PIPELINE COMPLETED SUCCESSFULLY!"
echo "================================================================================"
echo ""
echo "Results available in:"
echo "  - property_results/"
echo "  - affordance_results/"
echo "  - constraint_results/"
echo "  - $OUTPUT_DIR/"
echo ""
echo "Generated files in $OUTPUT_DIR/:"
echo "  Verification Results:"
echo "    - property_verification_results.csv"
echo "    - affordance_verification_results.csv"
echo "    - constraint_verification_results.csv"
echo ""
echo "  Summary Tables:"
echo "    - property_summary.csv"
echo "    - property_by_camera_summary.csv"
echo "    - affordance_summary.csv"
echo "    - constraint_summary.csv"
echo "    - constraint_by_camera_summary.csv"
echo "    - overall_benchmark_summary.csv"
echo "================================================================================"
echo ""
echo "Usage: ./run_full_evaluation.sh [EVAL_MODEL] [VERIFIER_MODEL] [NUM_SAMPLES] [OUTPUT_DIR]"
echo "Example: ./run_full_evaluation.sh meta-llama/llama-4-maverick meta-llama/llama-4-maverick 10 evaluations"
echo "================================================================================"

