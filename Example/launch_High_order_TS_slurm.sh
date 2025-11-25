#!/bin/bash
#SBATCH -J higher_order_brains
#SBATCH -p brains
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH -t 1-00:00:00
#SBATCH --array=0-2
#SBATCH -o /data/etosato/RHOSTS/Logs/%x_%A_%a.out
#SBATCH -e /data/etosato/RHOSTS/Logs/%x_%A_%a.err

set -euo pipefail

# Root directory of the repository on the cluster filesystem.
# Override with RHOSTS_ROOT to adapt to a different install path.
repo_dir="${RHOSTS_ROOT:-/data/etosato/RHOSTS}"
cd "${repo_dir}"

# Subjects and corresponding input locations for src/higher_order/main.py.
# Update these arrays to match your dataset (e.g., scaffold folders or DV hd5 files).
subjects=("745555" "905147" "943862")
inputs=(
  "${repo_dir}/Output/lorenzo_data/745555/scaffold_gen"
  "${repo_dir}/Output/lorenzo_data/905147/scaffold_gen"
  "${repo_dir}/Output/lorenzo_data/943862/scaffold_gen"
)

if [[ ${SLURM_ARRAY_TASK_ID} -ge ${#subjects[@]} ]]; then
  echo "Invalid SLURM_ARRAY_TASK_ID=${SLURM_ARRAY_TASK_ID} (only ${#subjects[@]} subjects defined)" >&2
  exit 1
fi

subject="${subjects[${SLURM_ARRAY_TASK_ID}]}"
input_path="${inputs[${SLURM_ARRAY_TASK_ID}]}"
output_dir="${repo_dir}/Output/lorenzo_data/${subject}"
output_npy="${output_dir}/${subject}_nodal_strength.npy"

mkdir -p "${repo_dir}/Logs" "${output_dir}"

# Optional tuning via environment variables (with defaults matching main.py):
#   MODE       -> dv | scaffold
#   SCENARIO   -> single_frame | all_frames | top_percent
#   FRAME      -> integer frame (used for single_frame)
#   PERCENT    -> float (used for top_percent)
#   NUM_ROIS   -> int number of regions
#   METRIC     -> hyper | complexity
#   DIRECTION  -> high | low
#   SORTED_TXT -> path to the sorted txt file (if selecting frames via percent)
MODE="${MODE:-scaffold}"
SCENARIO="${SCENARIO:-all_frames}"
PERCENT="${PERCENT:-0.15}"
NUM_ROIS="${NUM_ROIS:-100}"
METRIC="${METRIC:-complexity}"
DIRECTION="${DIRECTION:-low}"

cmd=(python -m src.higher_order.main \
  --mode "${MODE}" \
  --inputs "${input_path}" \
  --scenario "${SCENARIO}" \
  --percent "${PERCENT}" \
  --num-rois "${NUM_ROIS}" \
  --metric "${METRIC}" \
  --direction "${DIRECTION}" \
  --output-npy "${output_npy}")

if [[ -n "${FRAME:-}" ]]; then
  cmd+=(--frame "${FRAME}")
fi

if [[ -n "${SORTED_TXT:-}" ]]; then
  cmd+=(--sorted-output-txt "${SORTED_TXT}")
fi

echo "Running: ${cmd[*]}"
"${cmd[@]}"
