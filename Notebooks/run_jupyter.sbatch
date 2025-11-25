#!/bin/bash
#SBATCH --job-name=jupyter
#SBATCH -p brains
#SBATCH -t 04:00:00
#SBATCH -c 8
#SBATCH --mem=64G
#SBATCH -o /data/etosato/RHOSTS/Logs/jupyter-%j.log

# === Config ===
ENV_NAME="rhosts"
NB_ROOT="/data/etosato/RHOSTS"          # directory to expose as the Jupyter root
WORK_DIR="/data/etosato/RHOSTS/Notebooks"  # working directory for logs and startup

# === Environment setup ===
# Initialize conda in a non-interactive shell
if [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
    source "$HOME/miniconda3/etc/profile.d/conda.sh"
elif [ -f "/home/etosato/miniconda3/etc/profile.d/conda.sh" ]; then
    source "/home/etosato/miniconda3/etc/profile.d/conda.sh"
else
    echo "WARNING: conda.sh not found; falling back to PATH lookup"
    export PATH="$HOME/miniconda3/bin:$PATH"
fi

# Activate the environment
conda activate rhosts || {
    echo "ERROR: unable to activate env 'rhosts'"; exit 1;
}

# === Pick a free port ===
PORT=$(python - <<'PY'
import socket
s=socket.socket(); s.bind(('',0))
print(s.getsockname()[1]); s.close()
PY
)

mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

echo "MAGIC_NODE: $(hostname -s)"
echo "MAGIC_PORT: $PORT"
echo "MAGIC_DIR : $NB_ROOT"
echo "MAGIC_INFO: Starting Jupyter..."

# Launch Jupyter. The warning "Fail to get yarn configuration" is harmless.
# NB: root_dir = NB_ROOT as requested
jupyter lab --no-browser \
  --ip=0.0.0.0 \
  --port="$PORT" \
  --ServerApp.root_dir="$NB_ROOT"
