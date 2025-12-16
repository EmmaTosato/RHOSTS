#!/bin/bash
#SBATCH -J rhosts_run
#SBATCH -p brains
#SBATCH --cpus-per-task=5
#SBATCH --mem=32G
#SBATCH -t 02:00:00
#SBATCH -o /data/etosato/RHOSTS/Logs/nodal_strength/rhosts_run_%j.out
#SBATCH -e /data/etosato/RHOSTS/Logs/nodal_strength/rhosts_run_%j.err

set -euo pipefail

# Configuration
CONFIG_FILE="${1:-src/config/config.json}"

echo "Starting RHOSTS Analysis..."
echo "Config File: ${CONFIG_FILE}"

# Activate Environment
if [ -f "$(conda info --base)/etc/profile.d/conda.sh" ]; then
    set +u
    source $(conda info --base)/etc/profile.d/conda.sh
    conda activate rhosts
    set -u
else
    echo "WARNING: Could not find conda.sh, assuming environment is active or handled externally."
fi

# Environment Variables for Headless Execution
export PYVISTA_OFF_SCREEN=true
export MPLBACKEND=Agg
export PYTHONPATH="${PYTHONPATH:-}:/data/etosato/RHOSTS/High_order_TS_with_scaffold"

# Launch Analysis
python -m src.higher_order.orchestration.main --config "${CONFIG_FILE}"

echo "Analysis Complete."
