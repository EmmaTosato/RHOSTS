#!/bin/sh
#SBATCH -J edge_weight_brains
#SBATCH -p brains
#SBATCH --cpus-per-task=5
#SBATCH --mem=32G
#SBATCH -t 1-00:00:00
#SBATCH -o /data/etosato/RHOSTS/Logs/%A_%a_edge.out
#SBATCH -e /data/etosato/RHOSTS/Logs/%A_%a_edge.err

# Subjects
subjects=("745555" "905147" "943862")

sub=${subjects[$SLURM_ARRAY_TASK_ID]}

# Input code and files
codepath="/data/etosato/RHOSTS/High_order_TS/simplicial_multivariate.py"
filename="/data/etosato/RHOSTS/Input/lorenzo_data/cortical_subcortical/${sub}_ts_zscore_ctx_sub.txt"

# Output  files
weighted_network="/data/etosato/RHOSTS/Output/lorenzo_data/${sub}/${sub}_edge_projection"
result_file="/data/etosato/RHOSTS/Output/lorenzo_data/${sub}/${sub}_indicators.txt"

# Creating directories if they don't exist
mkdir -p "$(dirname "$weighted_network")"
mkdir -p "$(dirname "$result_file")"

python ${codepath} ${filename} -t 0 3600 -p 5 -s ${weighted_network} > ${result_file}
