#!/bin/sh
#SBATCH -J analyze_timepoints
#SBATCH -p brains
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH -t 0-00:30:00
#SBATCH -o /data/etosato/RHOSTS/Logs/timepoint_analysis/%x_%A_%a.out
#SBATCH -e /data/etosato/RHOSTS/Logs/timepoint_analysis/%x_%A_%a.err

cd /data/etosato/RHOSTS
python analyze_timepoints.py
