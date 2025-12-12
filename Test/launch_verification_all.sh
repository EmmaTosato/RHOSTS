#!/bin/bash
#SBATCH -J verify_all
#SBATCH -p brains
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH -t 02:00:00
#SBATCH -o /data/etosato/RHOSTS/Logs/verification_scaffold/verify_all_%j.out
#SBATCH -e /data/etosato/RHOSTS/Logs/verification_scaffold/verify_all_%j.err

set -e
source /home/etosato/miniconda3/etc/profile.d/conda.sh
conda activate rhosts
export PYTHONPATH=$PYTHONPATH:/data/etosato/RHOSTS/High_order_TS_with_scaffold

SUBJECTS=("134829" "393247" "745555" "905147" "943862")

for SUB in "${SUBJECTS[@]}"; do
    echo "======================================================================"
    echo "Scanning Subject: ${SUB}"
    echo "======================================================================"
    python3 -u /data/etosato/RHOSTS/Test/check_scaffold_integrity.py /data/etosato/RHOSTS/Output/lorenzo_data/${SUB}/generators
    echo ""
done
