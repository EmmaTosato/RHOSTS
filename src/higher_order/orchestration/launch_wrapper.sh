#!/bin/bash
#
# Wrapper script to launch higher-order analysis with automatic group averaging.
#
# Usage: bash launch_wrapper.sh [MODE] [SCENARIO] [NUM_SUBJECTS]
# Example: bash launch_wrapper.sh dv all_frames 5
#

set -e

# 1. Parse Arguments
MODE="${1:-dv}"
SCENARIO="${2:-single_frame}"
NUM_SUBS="${3:-1}"

echo "----------------------------------------------------------------"
echo "Launching Analysis Pipeline"
echo "MODE:        ${MODE}"
echo "SCENARIO:    ${SCENARIO}"
echo "SUBJECTS:    ${NUM_SUBS}"
echo "----------------------------------------------------------------"

# 2. Submit the Array Job (Subject Level)
# We use --parsable to capture just the Job ID
# We pass the arguments as environment variables to override defaults in main.sh
JOB_ID=$(MODE="${MODE}" SCENARIO="${SCENARIO}" sbatch --parsable --array=0-$((NUM_SUBS-1)) src/higher_order/orchestration/main.sh)

echo "Submitted Subject Array Job: ${JOB_ID}"

# 3. Submit Group Analysis (Conditional)
if [ "$NUM_SUBS" -gt 1 ]; then
    echo "Multiple subjects detected. Submitting Group Analysis dependency..."
    
    # Define the command for the group analysis
    # It uses the same main.py but in 'group' mode
    # We use wildcards to catch all outputs from the previous step
    GROUP_CMD="python -m src.higher_order.orchestration.main \
        --mode group \
        --inputs /data/etosato/RHOSTS/Output/higher_order/${MODE}/*_${SCENARIO}.npy \
        --output-npy /data/etosato/RHOSTS/Output/higher_order/${MODE}/GROUP_AVERAGE.npy \
        --output-img /data/etosato/RHOSTS/Output/Images/${MODE}/GROUP_AVERAGE.png"
    
    # Submit the dependent job
    # --dependency=afterok:JOB_ID ensures it starts only after the array finishes successfully
    # --wrap allows us to pass the command directly without a separate script file
    GROUP_JOB_ID=$(sbatch --dependency=afterok:${JOB_ID} \
                          -J "group_${MODE}" \
                          -o "/data/etosato/RHOSTS/Logs/group_${MODE}_%j.out" \
                          -e "/data/etosato/RHOSTS/Logs/group_${MODE}_%j.err" \
                          --wrap="${GROUP_CMD}")
                          
    echo "Submitted Group Analysis Job: ${GROUP_JOB_ID} (Waiting for ${JOB_ID})"
else
    echo "Single subject. Skipping Group Analysis."
fi

echo "----------------------------------------------------------------"
echo "Done! Monitor your jobs with 'squeue -u \$USER'"
