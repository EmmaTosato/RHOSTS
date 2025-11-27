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

# Root directory of the repository on the cluster filesystem.
# Override with RHOSTS_ROOT to adapt to a different install path.
repo_dir="${RHOSTS_ROOT:-/data/etosato/RHOSTS}"

# TSV file listing the jobs to run with two columns: SUBJECT_ID and INPUTS.
# The INPUTS column may contain one or more paths separated by spaces. When
# targeting scaffold mode, each path should be a directory; for dv mode, each
# path should be an HDF5 file. Adjust --array above to cover the number of rows
# in this table (0-indexed).
input_table="${INPUT_TABLE:-${repo_dir}/Input/higher_order_inputs.tsv}"

if [[ ! -f "${input_table}" ]]; then
  cat <<MSG >&2
Missing ${input_table}.
Create a TSV with two columns: SUBJECT_ID<TAB>INPUTS (space-separated paths).
Example:
  sub-001\t/data/.../sub-001.h5
  sub-002\t/data/.../sub-002_scaffold/frame_* /data/.../sub-002_scaffold/other_cycles
MSG
  exit 1
fi

mapfile -t rows < <(grep -v '^\s*$' "${input_table}")

if [[ ${#rows[@]} -eq 0 ]]; then
  echo "No jobs found in ${input_table}" >&2
  exit 1
fi

if [[ ${SLURM_ARRAY_TASK_ID} -ge ${#rows[@]} ]]; then
  echo "Invalid SLURM_ARRAY_TASK_ID=${SLURM_ARRAY_TASK_ID} (only ${#rows[@]} rows in ${input_table})" >&2
  exit 1
fi

IFS=$'\t' read -r subject input_paths <<<"${rows[${SLURM_ARRAY_TASK_ID}]}"
read -r -a inputs <<<"${input_paths}"

# Configure higher-order brain map parameters. Override via environment
# variables to customize a job without editing the script.
mode="${MODE:-dv}"                          # dv | scaffold
scenario="${SCENARIO:-single_frame}"        # single_frame | all_frames | top_percent
frame="${FRAME:-0}"                         # frame index for single_frame scenario
percent="${PERCENT:-0.15}"                  # used by top_percent scenario
metric="${METRIC:-hyper}"                   # hyper | complexity
direction="${DIRECTION:-high}"              # high | low

out_dir="${repo_dir}/Output/higher_order/${mode}"
mkdir -p "${repo_dir}/Logs" "${out_dir}"

out_file="${out_dir}/${subject}_${scenario}.npy"

args=(
  --mode "${mode}"
  --inputs "${inputs[@]}"
  --scenario "${scenario}"
  --percent "${percent}"
  --metric "${metric}"
  --direction "${direction}"
  --output-npy "${out_file}"
)

# Only pass --frame when explicitly set to avoid conflicting with scenarios
# that iterate over all frames.
if [[ -n "${FRAME:-}" ]]; then
  args+=(--frame "${frame}")
fi

python -m src.higher_order.main "${args[@]}"