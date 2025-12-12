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
    
    echo "--------------------------------------------------------" | tee -a "${LOG_FILE}"
    echo "TESTING: Mode=${MODE}, Scenario=${SCENARIO}" | tee -a "${LOG_FILE}"
    
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
        --sorted-output-txt "${INPUT_TXT}")
        
    # Default metric depends on mode usually, let's be explicit to avoid warnings
    if [[ "${MODE}" == "dv" ]]; then
        CMD+=(--metric coherence)
    else
        CMD+=(--metric complexity)
    fi

    echo "Command: ${CMD[*]}" >> "${LOG_FILE}"
    
    # 3. Execution
    if "${CMD[@]}" >> "${LOG_FILE}" 2>&1; then
        # 4. Verification
        if [[ -f "${OUT_FILE}" ]] && [[ -s "${OUT_FILE}" ]]; then
            echo "RESULT: PASS" | tee -a "${LOG_FILE}"
            echo "Verified Output: ${OUT_FILE}" >> "${LOG_FILE}"
        else
            echo "RESULT: FAIL (File not created or empty)" | tee -a "${LOG_FILE}"
            echo "Expected: ${OUT_FILE}" | tee -a "${LOG_FILE}"
        fi
    else
        echo "RESULT: FAIL (Execution Error)" | tee -a "${LOG_FILE}"
    fi
}

# --- TEST MATRIX ---

# 1. DV Modes
run_test "dv" "single_frame" "${INPUT_DV}"
run_test "dv" "all_frames" "${INPUT_DV}"
run_test "dv" "top_percent" "${INPUT_DV}" # Maps to --scenario percent in shell wrapper, but here we call python directly which expects 'top_percent' if using arg parser? 
# Wait, main.py arg parser says: choices=["single_frame", "all_frames", "top_percent"]
# So passing "top_percent" is correct for python.

# 2. Scaffold Modes
# Note: Scaffold execution might fail if the input directory structure isn't exactly as expected for this subject.
# We will try it. If it fails, the log will show it.
# Assuming inputs variable can take a directory for scaffold mode.
# Let's use the SC_DIR if exists, else skip or try mocked path.
# Based on file listing, we saw `Example/launch_High_order_TS_with_scaffold.sh` outputs to `Output/lorenzo_data/${subject}/generators`.
SCAFFOLD_INPUT_DIR="${REPO_DIR}/Output/lorenzo_data/${SUBJECT}/generators"

if [[ -d "${SCAFFOLD_INPUT_DIR}" ]]; then
    run_test "scaffold" "single_frame" "${SCAFFOLD_INPUT_DIR}"
    run_test "scaffold" "all_frames" "${SCAFFOLD_INPUT_DIR}"
    run_test "scaffold" "top_percent" "${SCAFFOLD_INPUT_DIR}"
else
    echo "WARNING: Scaffold input directory ${SCAFFOLD_INPUT_DIR} not found. Skipping Scaffold tests." | tee -a "${LOG_FILE}"
fi

echo "========================================================" | tee -a "${LOG_FILE}"
echo "TESTS COMPLETED" | tee -a "${LOG_FILE}"
echo "Summary written to ${LOG_FILE}"
