#!/bin/bash

# Test/verify_smart_resume.sh
# Verifies the Smart Resume logic in Example/launch_High_order_TS_with_scaffold.sh

set -euo pipefail

# Configuration
SUBJECT="TEST_SMART_RESUME"
OFFSET=0
T=0
SCRIPT_DIR="/data/etosato/RHOSTS/Example"
SCRIPT="${SCRIPT_DIR}/launch_High_order_TS_with_scaffold.sh"
OUTPUT_DIR="/data/etosato/RHOSTS/Output/lorenzo_data/${SUBJECT}/generators"
OUTFILE="${OUTPUT_DIR}/generators__${T}.pck"

# Ensure output directory exists
mkdir -p "${OUTPUT_DIR}"

# Helper function to create a valid pickle file
create_valid_pickle() {
    python -c "import pickle; pickle.dump({'test': 'data'}, open('${OUTFILE}', 'wb'))"
}

# Helper function to create a corrupted file
create_corrupted_file() {
    echo "CORRUPTED DATA" > "${OUTFILE}"
}

echo "=========================================="
echo "Starting Smart Resume Verification"
echo "Subject: ${SUBJECT}"
echo "Target File: ${OUTFILE}"
echo "=========================================="

# ---------------------------------------------------------
# Test Case 1: File exists and is valid
# ---------------------------------------------------------
echo ""
echo "[TEST 1] Testing with VALID existing file..."
create_valid_pickle

# Run the script. We expect exit code 0 and "Skipping" message.
# We need to export SLURM_ARRAY_TASK_ID for the script to work locally.
export SLURM_ARRAY_TASK_ID=0

# Capture output
output=$(bash "${SCRIPT}" "${SUBJECT}" "${OFFSET}" 2>&1) || true

if echo "${output}" | grep -q "Skipping subject=${SUBJECT}, t=${T}"; then
    echo "✅ PASSED: Script skipped valid file."
else
    echo "❌ FAILED: Script did not skip valid file."
    echo "Output was:"
    echo "${output}"
fi

# ---------------------------------------------------------
# Test Case 2: File exists but is corrupted
# ---------------------------------------------------------
echo ""
echo "[TEST 2] Testing with CORRUPTED existing file..."
create_corrupted_file

# Run the script. We expect "Warning: ... Regenerating..."
# The script will likely fail later because input files are missing, but that's expected.
output=$(bash "${SCRIPT}" "${SUBJECT}" "${OFFSET}" 2>&1) || true

if echo "${output}" | grep -q "Warning: File ${OUTFILE} exists but is corrupted"; then
    echo "✅ PASSED: Script detected corrupted file and attempted regeneration."
else
    echo "❌ FAILED: Script did not detect corrupted file."
    echo "Output was:"
    echo "${output}"
fi

# ---------------------------------------------------------
# Cleanup
# ---------------------------------------------------------
echo ""
echo "Cleaning up..."
rm -f "${OUTFILE}"
rmdir "${OUTPUT_DIR}" 2>/dev/null || true
# Try to remove parent dirs if empty
rmdir "/data/etosato/RHOSTS/Output/lorenzo_data/${SUBJECT}" 2>/dev/null || true

echo "Verification Complete."
