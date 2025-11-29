#!/bin/bash
#SBATCH -J verify_scaffold
#SBATCH -p brains
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH -t 00:30:00
#SBATCH -o /data/etosato/RHOSTS/Logs/scaffold_generation/verify_%j.out
#SBATCH -e /data/etosato/RHOSTS/Logs/scaffold_generation/verify_%j.err

set -e

# Activate environment
source /home/etosato/miniconda3/etc/profile.d/conda.sh
conda activate rhosts

# Add project root to PYTHONPATH so pickle can find classes if needed
export PYTHONPATH=$PYTHONPATH:/data/etosato/RHOSTS/High_order_TS_with_scaffold

# Run verification
python3 -u /data/etosato/RHOSTS/Test/check_scaffold_integrity.py /data/etosato/RHOSTS/Output/lorenzo_data/134829/generators
