#!/bin/bash
################################################################################
# Higher-Order Brain Network Analysis - Group Level
#
# Usage: sbatch group.sh
#        MODE=scaffold SCENARIO=all_frames sbatch group.sh
#
# Typically launched with dependency:
# sbatch --dependency=afterok:<ARRAY_JOB_ID> group.sh
################################################################################

#SBATCH -J group_brains
#SBATCH -p brains
#SBATCH --cpus-per-task=5
#SBATCH --mem=32G
#SBATCH -t 01:00:00
#SBATCH -o /data/etosato/RHOSTS/Logs/%x_%j.out
#SBATCH -e /data/etosato/RHOSTS/Logs/%x_%j.err

set -euo pipefail

# Activate conda environment
set +u
source $(conda info --base)/etc/profile.d/conda.sh || true
conda activate rhosts || true
set -u

# Configuration
repo_dir="${RHOSTS_ROOT:-/data/etosato/RHOSTS}"
mode="${MODE:-dv}"                          # dv | scaffold
scenario="${SCENARIO:-single_frame}"        # single_frame | all_frames | percent

# Headless rendering configuration
export PYVISTA_OFF_SCREEN=true
export VTK_OFF_SCREEN=true
export MPLBACKEND=Agg

# Map scenario to filename pattern
# main.sh saves as: ${subject}_${scenario}.npy
# Note: "percent" scenario in main.sh maps to "top_percent" in python, 
# but the filename uses the bash variable "percent" if passed as SCENARIO=percent?
# Let's check main.sh logic:
# py_scenario="${scenario}" -> if percent, py_scenario="top_percent"
# out_file="${out_dir}/${subject}_${scenario}.npy" -> Uses the bash variable!
# So if SCENARIO=percent, file is *_percent.npy.
# If SCENARIO=top_percent, file is *_top_percent.npy.
# We should stick to what main.sh does.

input_pattern="${repo_dir}/Output/higher_order/${mode}/*_${scenario}.npy"
out_npy="${repo_dir}/Output/higher_order/${mode}/GROUP_AVERAGE_${scenario}.npy"
out_img="${repo_dir}/Output/Images/${mode}/GROUP_AVERAGE_${scenario}.png"

echo "Running Group Analysis"
echo "Mode: ${mode}"
echo "Scenario: ${scenario}"
echo "Input Pattern: ${input_pattern}"

# Execute
python -m src.higher_order.orchestration.main \
  --mode group \
  --inputs ${input_pattern} \
  --output-npy "${out_npy}" \
  --output-img "${out_img}"
