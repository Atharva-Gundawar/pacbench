
# PACBench Full Evaluation Pipeline
# Runs verification and generates summary tables

echo "================================================================================"
echo "PACBENCH EVALUATION"
echo "================================================================================"

# Parse command line arguments
VERIFIER_MODEL="${1:-meta-llama/llama-4-maverick}"
OUTPUT_DIR="${2:-evaluations}"

echo "Verifier Model: $VERIFIER_MODEL"
echo "Output Directory: $OUTPUT_DIR"
echo "================================================================================"

# Step 1: Run verification
echo ""
echo "================================================================================"
echo "STEP 1: Verifying Results with LLM"
echo "================================================================================"
python verify_results.py \
    --model "$VERIFIER_MODEL" \
    --property_dir property_results \
    --affordance_dir affordance_results \
    --constraint_dir constraint_results \
    --output_dir "$OUTPUT_DIR" \
    --task all

if [ $? -ne 0 ]; then
    echo "ERROR: Verification failed!"
    exit 1
fi

# Step 2: Generate summary tables
echo ""
echo "================================================================================"
echo "STEP 2: Generating Summary Tables"
echo "================================================================================"
python generate_summary_tables.py \
    --eval_dir "$OUTPUT_DIR" \
    --output_dir "$OUTPUT_DIR"

if [ $? -ne 0 ]; then
    echo "ERROR: Summary generation failed!"
    exit 1
fi

# Success message
echo ""
echo "================================================================================"
echo "✓ FULL EVALUATION PIPELINE COMPLETED SUCCESSFULLY!"
echo "================================================================================"
echo ""
echo "Results available in: $OUTPUT_DIR/"
echo ""
echo "Generated files:"
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

