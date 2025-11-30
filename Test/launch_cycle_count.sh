#!/bin/bash
#SBATCH -J count_cycles
#SBATCH -p brains
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH -t 00:30:00
#SBATCH -o /data/etosato/RHOSTS/Logs/verification_scaffold/count_cycles_%j.out
#SBATCH -e /data/etosato/RHOSTS/Logs/verification_scaffold/count_cycles_%j.err

set -e
source /home/etosato/miniconda3/etc/profile.d/conda.sh
conda activate rhosts
export PYTHONPATH=$PYTHONPATH:/data/etosato/RHOSTS/High_order_TS_with_scaffold

echo "---- Scanning Subject 134829 ----"
python3 -u /data/etosato/RHOSTS/Test/check_scaffold_integrity.py /data/etosato/RHOSTS/Output/lorenzo_data/134829/generators

echo ""
echo "---- Scanning Subject 393247 ----"
python3 -u /data/etosato/RHOSTS/Test/check_scaffold_integrity.py /data/etosato/RHOSTS/Output/lorenzo_data/393247/generators
