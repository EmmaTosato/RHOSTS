#!/bin/bash
# Test Suite for Nodal Strength Generation
# Verifies that .npy files are correctly generated for all modes and scenarios.

set -u

# 1. Configuration
REPO_DIR="/data/etosato/RHOSTS"
LOG_DIR="${REPO_DIR}/Logs/tests_report"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="${LOG_DIR}/generation_test_${TIMESTAMP}.log"
SUBJECT="134829"  # Test Subject

# Ensure paths exist
mkdir -p "${LOG_DIR}"
cd "${REPO_DIR}" || exit 1

# Activate Conda (if not already active)
if [[ -z "${CONDA_DEFAULT_ENV:-}" ]]; then
    set +u
    source /home/etosato/miniconda3/etc/profile.d/conda.sh
    conda activate rhosts
    set -u
fi

# Define Inputs for the Test Subject (Hardcoded for verification consistency)
INPUT_DV="${REPO_DIR}/Output/lorenzo_data/${SUBJECT}/${SUBJECT}_edge_projection.hd5"
INPUT_TXT="${REPO_DIR}/Output/lorenzo_data/${SUBJECT}/${SUBJECT}_indicators.txt"
# For scaffold, we assume the directory exists or we point to the same HD5 if appropriate for the test mock logic, 
# BUT strict scaffold requires directories. Let's find a valid scaffold input from `Input/lorenzo_data/tsv_files/higher_order_inputs.tsv` logic if possible.
# Wait, higher_order_inputs.tsv uses the same paths for validation usually, let's just use the known inputs.
# Looking at previous logs/files:
INPUT_SCAFFOLD="${REPO_DIR}/Output/lorenzo_data/${SUBJECT}/${SUBJECT}_scaffold" # Hypothetical, might need adjustment if mock

echo "========================================================" | tee -a "${LOG_FILE}"
echo "STARTING GENERATION TESTS - ${TIMESTAMP}" | tee -a "${LOG_FILE}"
echo "Subject: ${SUBJECT}" | tee -a "${LOG_FILE}"
echo "Log: ${LOG_FILE}" | tee -a "${LOG_FILE}"
echo "========================================================" | tee -a "${LOG_FILE}"

# Function to run a single test case
run_test() {
    local MODE=$1
    local SCENARIO=$2
    local INPUT=$3
    local METRIC=$4
    
    echo "--------------------------------------------------------" | tee -a "${LOG_FILE}"
    echo "TESTING: Mode=${MODE}, Scenario=${SCENARIO}, Metric=${METRIC}" | tee -a "${LOG_FILE}"
    
    # Define expected output
    OUT_DIR="${REPO_DIR}/Output/lorenzo_data/node_strengths/${MODE}"
    OUT_FILE="${OUT_DIR}/${SUBJECT}_${SCENARIO}.npy"
    
    # 1. Cleanup (ensure we are testing generation, not existence)
    if [[ -f "${OUT_FILE}" ]]; then
        rm "${OUT_FILE}"
    fi
    mkdir -p "${OUT_DIR}"

    # 2. Construction Command
    CMD=(python -m src.higher_order.orchestration.main \
        --mode "${MODE}" \
        --inputs "${INPUT}" \
        --scenario "${SCENARIO}" \
        --frame 0 \
        --percent 0.15 \
        --output-npy "${OUT_FILE}" \
        --sorted-output-txt "${INPUT_TXT}" \
        --metric "${METRIC}")

    echo "Command: ${CMD[*]}" >> "${LOG_FILE}"
    
    echo "Command: ${CMD[*]}" >> "${LOG_FILE}"
    
    # 3. Execution via SLURM
    # Use sbatch --wait to submit to cluster and wait for completion.
    SLURM_OUT="${LOG_DIR}/slurm_${MODE}_${SCENARIO}_${TIMESTAMP}.out"
    
    # Construct sbatch command
    SBATCH_CMD="sbatch --parsable --wait --job-name=val_${MODE} --output=${SLURM_OUT} --error=${SLURM_OUT} --mem=32G --partition=brains --time=02:00:00 --wrap=\"${CMD[*]}\""
    
    echo "Submitting: ${SBATCH_CMD}" | tee -a "${LOG_FILE}"
    
    # Execute sbatch
    # Note: we use eval to handle the quoted wrap string correctly
    if eval "${SBATCH_CMD}" >> "${LOG_FILE}" 2>&1; then
        echo "Job finished." >> "${LOG_FILE}"
    else
        echo "RESULT: FAIL (Submission Error)" | tee -a "${LOG_FILE}"
        return 1
    fi

    # 4. Verification
    if [[ -f "${OUT_FILE}" ]] && [[ -s "${OUT_FILE}" ]]; then
        echo "RESULT: PASS" | tee -a "${LOG_FILE}"
        echo "Verified Output: ${OUT_FILE}" >> "${LOG_FILE}"
    else
        echo "RESULT: FAIL (File not created or empty)" | tee -a "${LOG_FILE}"
        echo "Check SLURM output: ${SLURM_OUT}" | tee -a "${LOG_FILE}"
        echo "Expected: ${OUT_FILE}" | tee -a "${LOG_FILE}"
    fi
}

# --- TEST MATRIX ---

# 1. DV Modes (High Coherence = Top Percent)
run_test "dv" "single_frame" "${INPUT_DV}" "coherence"
run_test "dv" "all_frames" "${INPUT_DV}" "coherence"
run_test "dv" "top_percent" "${INPUT_DV}" "coherence"

# 2. Scaffold Modes (Low Complexity = Low Percent)
SCAFFOLD_INPUT_DIR="${REPO_DIR}/Output/lorenzo_data/${SUBJECT}/generators"

if [[ -d "${SCAFFOLD_INPUT_DIR}" ]]; then
    run_test "scaffold" "single_frame" "${SCAFFOLD_INPUT_DIR}" "complexity"
    run_test "scaffold" "all_frames" "${SCAFFOLD_INPUT_DIR}" "complexity"
    run_test "scaffold" "top_percent" "${SCAFFOLD_INPUT_DIR}" "complexity"
else
    echo "WARNING: Scaffold input directory ${SCAFFOLD_INPUT_DIR} not found. Skipping Scaffold tests." | tee -a "${LOG_FILE}"
fi

echo "========================================================" | tee -a "${LOG_FILE}"
echo "TESTS COMPLETED" | tee -a "${LOG_FILE}"
echo "Summary written to ${LOG_FILE}"
