#!/bin/bash
#SBATCH --job-name=preprocessing
#SBATCH -p brains
#SBATCH -t 04:00:00
#SBATCH -c 4
#SBATCH --mem=64G
#SBATCH -o preprocessing-%j.log

# Optional: load modules or activate your env
# module load python/3.X
# source /path/to/venv/bin/activate

python preprocessing_hcp.py
