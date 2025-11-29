#!/bin/bash
#SBATCH -J verify_suspicious
#SBATCH -p brains
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH -t 00:05:00
#SBATCH -o /data/etosato/RHOSTS/Logs/scaffold_generation/verify_suspicious_%j.out
#SBATCH -e /data/etosato/RHOSTS/Logs/scaffold_generation/verify_suspicious_%j.err

set -e
source /home/etosato/miniconda3/etc/profile.d/conda.sh
conda activate rhosts
export PYTHONPATH=$PYTHONPATH:/data/etosato/RHOSTS/High_order_TS_with_scaffold

python3 -u /data/etosato/RHOSTS/Test/check_scaffold_integrity.py /data/etosato/RHOSTS/Output/lorenzo_data/134829/generators --pattern "generators__1203.pck"
python3 -u /data/etosato/RHOSTS/Test/check_scaffold_integrity.py /data/etosato/RHOSTS/Output/lorenzo_data/134829/generators --pattern "generators__1219.pck"
python3 -u /data/etosato/RHOSTS/Test/check_scaffold_integrity.py /data/etosato/RHOSTS/Output/lorenzo_data/134829/generators --pattern "generators__1220.pck"
python3 -u /data/etosato/RHOSTS/Test/check_scaffold_integrity.py /data/etosato/RHOSTS/Output/lorenzo_data/134829/generators --pattern "generators__1222.pck"
