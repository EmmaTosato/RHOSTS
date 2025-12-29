#!/bin/bash
#SBATCH --job-name=preprocessing
#SBATCH -p brains
#SBATCH -t 04:00:00
#SBATCH -c 4
#SBATCH --mem=64G
#SBATCH -o /data/etosato/RHOSTS/Logs/preprocessing/preprocessing-%j.log


python preprocessing_hcp.py
