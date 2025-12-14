#!/bin/sh
#SBATCH -J clean_err_logs
#SBATCH -p brains
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH -t 0-00:05:00
#SBATCH -o /data/etosato/RHOSTS/Logs/utils/%x_%j.out
#SBATCH -e /data/etosato/RHOSTS/Logs/utils/%x_%j.err

# Activate conda environment
eval "$(conda shell.bash hook)"
conda activate rhosts

# Run the cleanup script
python /data/etosato/RHOSTS/utils/clean_empty_err_logs.py
