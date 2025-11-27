#!/bin/bash
#SBATCH -J higher_order_brains
#SBATCH -p brains
#SBATCH --cpus-per-task=5
#SBATCH --mem=32G
#SBATCH -t 1-00:00:00
#SBATCH --array=0-4
#SBATCH -o /data/etosato/RHOSTS/Logs/%x_%A_%a.out
#SBATCH -e /data/etosato/RHOSTS/Logs/%x_%A_%a.err

set -euo pipefail

# Activate conda environment
set +u
source $(conda info --base)/etc/profile.d/conda.sh || true
conda activate rhosts || true
set -u

################################################################################
# CONFIGURATION
################################################################################

# Repository root directory
repo_dir="${RHOSTS_ROOT:-/data/etosato/RHOSTS}"

# Input TSV file: SUBJECT_ID<TAB>INPUTS (space-separated paths)
# Update --array in SLURM header to match row count
input_table="${INPUT_TABLE:-${repo_dir}/Input/higher_order_inputs.tsv}"

# Headless rendering configuration
export PYVISTA_OFF_SCREEN=true
export VTK_OFF_SCREEN=true
export MPLBACKEND=Agg

# Analysis parameters (override via environment variables)
# You can change these defaults directly here to avoid typing them every time
mode="${MODE:-dv}"                          # dv | scaffold
scenario="${SCENARIO:-single_frame}"        # single_frame | all_frames | percent
frame="${FRAME:-0}"                         # Frame index (for single_frame)
percent="${PERCENT:-0.15}"                  # Top percentage (for percent scenario)

# Infer metric from mode if not specified
if [[ "${mode}" == "dv" ]]; then
  default_metric="coherence"
else
  default_metric="complexity"
fi
metric="${METRIC:-${default_metric}}"       # coherence | complexity

################################################################################
# VALIDATION & EXECUTION
################################################################################

if [[ ! -f "${input_table}" ]]; then
  echo "ERROR: Input table not found: ${input_table}" >&2
  exit 1
fi

mapfile -t rows < <(grep -v '^\s*$' "${input_table}")
if [[ ${#rows[@]} -eq 0 ]]; then
  echo "ERROR: No jobs found in ${input_table}" >&2
  exit 1
fi

if [[ ${SLURM_ARRAY_TASK_ID} -ge ${#rows[@]} ]]; then
  echo "ERROR: Invalid array task ID (only ${#rows[@]} rows)" >&2
  exit 1
fi

# Parse current job from input table
IFS=$'\t' read -r subject input_paths <<<"${rows[${SLURM_ARRAY_TASK_ID}]}"
read -r -a all_inputs <<<"${input_paths}"

# Separate TXT file from HDF5/scaffold inputs
# The TXT file (indicators) is always the last one in the list
txt_file=""
data_inputs=()

for input in "${all_inputs[@]}"; do
  if [[ "$input" == *"indicators.txt" ]] || [[ "$input" == *.txt ]]; then
    txt_file="$input"
  else
    data_inputs+=("$input")
  fi
done

# Map "percent" scenario to python's "top_percent"
py_scenario="${scenario}"
if [[ "${scenario}" == "percent" ]]; then
  py_scenario="top_percent"
fi

# Setup output paths
out_dir="${repo_dir}/Output/higher_order/${mode}"
img_dir="${repo_dir}/Output/Images/${mode}"
mkdir -p "${repo_dir}/Logs" "${out_dir}" "${img_dir}"

out_file="${out_dir}/${subject}_${scenario}.npy"
img_file="${img_dir}/${subject}_${scenario}.png"

# Build arguments and execute
args=(
  --mode "${mode}"
  --inputs "${data_inputs[@]}"
  --scenario "${py_scenario}"
  --percent "${percent}"
  --metric "${metric}"
  --output-npy "${out_file}"
  --output-img "${img_file}"
)

if [[ "${scenario}" == "single_frame" ]] || [[ -n "${FRAME:-}" ]]; then
  args+=(--frame "${frame}")
fi

if [[ -n "${txt_file}" ]]; then
  args+=(--sorted-output-txt "${txt_file}")
fi

python -m src.higher_order.main "${args[@]}"