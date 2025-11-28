#!/bin/bash
#SBATCH -J brain_images
#SBATCH -p brains
#SBATCH --cpus-per-task=5
#SBATCH --mem=32G
#SBATCH -t 1-00:00:00
# Commented out array directive to default to single-job sequential mode
# To run in parallel, use: sbatch --array=0-N src/higher_order/main.sh
##SBATCH --array=0-4
#SBATCH -o /data/etosato/RHOSTS/Logs/%x_%j.out
#SBATCH -e /data/etosato/RHOSTS/Logs/%x_%j.err

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
cd "${repo_dir}" || exit 1

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
metric="${METRIC:-${default_metric}}"

# Image generation control
# Set to "true" to enable image generation (requires xvfb on cluster)
# Set to "false" to only generate .npy files (default, images can be generated locally)
generate_images="${GENERATE_IMAGES:-false}"       # coherence | complexity

################################################################################
# VALIDATION & EXECUTION
################################################################################

if [[ ! -f "${input_table}" ]]; then
  echo "ERROR: Input table not found: ${input_table}" >&2
  exit 1
fi

mapfile -t rows < <(grep -v '^\s*$' "${input_table}")
total_rows=${#rows[@]}

if [[ ${total_rows} -eq 0 ]]; then
  echo "ERROR: No jobs found in ${input_table}" >&2
  exit 1
fi

# Determine which subjects to process
# SUBJECT_RANGE can be a single number "0" or a range "0-4"
# Default to processing ALL subjects if not specified
subject_range="${SUBJECT_RANGE:-0-$((total_rows-1))}"

if [[ "${subject_range}" == *"-"* ]]; then
  start_idx=${subject_range%-*}
  end_idx=${subject_range#*-}
else
  start_idx=${subject_range}
  end_idx=${subject_range}
fi

# Validate indices
if [[ ${start_idx} -lt 0 ]] || [[ ${end_idx} -ge ${total_rows} ]]; then
  echo "ERROR: Invalid subject range ${subject_range}. Valid range is 0-$((total_rows-1))." >&2
  exit 1
fi

# Calculate number of subjects to process
num_subjects_to_process=$((end_idx - start_idx + 1))
echo "Processing ${num_subjects_to_process} subjects (Indices ${start_idx} to ${end_idx})"

# Function to process a single subject
process_subject() {
  local task_id=$1
  local generate_image=$2 # "true" or "false"
  
  # Parse current job from input table
  IFS=$'\t' read -r subject input_paths <<<"${rows[${task_id}]}"
  read -r -a all_inputs <<<"${input_paths}"

  echo "Processing Subject: ${subject} (Row ${task_id})"

  # Separate TXT file from HDF5/scaffold inputs
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
  out_dir="${repo_dir}/Output/lorenzo_data/node_strengths/${mode}"
  img_dir="${repo_dir}/Output/lorenzo_data/images/${mode}"
  mkdir -p "${repo_dir}/Logs" "${out_dir}" "${img_dir}"

  out_file="${out_dir}/${subject}_${scenario}.npy"
  img_file="${img_dir}/${subject}_${scenario}.png"

  # Build arguments
  args=(
    --mode "${mode}"
    --inputs "${data_inputs[@]}"
    --scenario "${py_scenario}"
    --percent "${percent}"
    --metric "${metric}"
    --output-npy "${out_file}"
  )

  # Only generate image if requested (Single Subject case) AND images are enabled
  if [[ "${generate_image}" == "true" ]] && [[ "${generate_images}" == "true" ]]; then
    args+=(--output-img "${img_file}")
  fi

  if [[ "${scenario}" == "single_frame" ]] || [[ -n "${FRAME:-}" ]]; then
    args+=(--frame "${frame}")
  fi

  if [[ -n "${txt_file}" ]]; then
    args+=(--sorted-output-txt "${txt_file}")
  fi

  python -m src.higher_order.main "${args[@]}"
}

# MAIN LOGIC
if [[ -n "${SLURM_ARRAY_TASK_ID:-}" ]]; then
  # ---------------------------------------------------------
  # PARALLEL MODE (Array Job)
  # ---------------------------------------------------------
  # In parallel mode, we don't know if we are part of a group > 1 easily without external coordination.
  # Default behavior: Generate images for everyone.
  # If you want to disable images in parallel, set GENERATE_IMAGES=false
  echo "Running in PARALLEL ARRAY MODE (Task ID: ${SLURM_ARRAY_TASK_ID})"
  process_subject "${SLURM_ARRAY_TASK_ID}" "true"

else
  # ---------------------------------------------------------
  # SEQUENTIAL MODE (Single Job)
  # ---------------------------------------------------------
  echo "Running in SEQUENTIAL MODE"
  
  # Decide whether to generate individual images
  # Rule: If > 1 subject, DO NOT generate individual images.
  if [[ ${num_subjects_to_process} -gt 1 ]]; then
    gen_img="false"
    echo "Multiple subjects selected: Skipping individual image generation."
  else
    gen_img="true"
    echo "Single subject selected: Generating individual image."
  fi
  
  # Loop through selected range
  for ((i=start_idx; i<=end_idx; i++)); do
    process_subject "$i" "$gen_img"
  done
  
  # Automatic Group Analysis (only if > 1 subject)
  if [[ ${num_subjects_to_process} -gt 1 ]]; then
    echo "----------------------------------------------------------------"
    echo "Running Automatic Group Analysis"
    
    group_npy="${repo_dir}/Output/lorenzo_data/node_strengths/${mode}/group_average_${scenario}.npy"
    group_img="${repo_dir}/Output/lorenzo_data/images/${mode}/group_average_${scenario}.png"
    
    # We need to find the files we just created.
    # Since we might have processed a subset, we should ideally only average those.
    # But the group mode takes a list of files.
    # Let's construct the list of expected output files based on the processed subjects.
    
    group_inputs=()
    for ((i=start_idx; i<=end_idx; i++)); do
      IFS=$'\t' read -r subj _ <<<"${rows[$i]}"
      group_inputs+=("${repo_dir}/Output/lorenzo_data/node_strengths/${mode}/${subj}_${scenario}.npy")
    done
    
    
    group_args=(
      --mode group
      --inputs "${group_inputs[@]}"
      --output-npy "${group_npy}"
    )
    
    # Only generate group image if enabled
    if [[ "${generate_images}" == "true" ]]; then
      group_args+=(--output-img "${group_img}")
    fi
    
    python -m src.higher_order.main "${group_args[@]}"
  fi
fi