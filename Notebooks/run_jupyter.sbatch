#!/bin/bash
#SBATCH --job-name=jupyter
#SBATCH -p brains
#SBATCH -t 04:00:00
#SBATCH -c 4
#SBATCH --mem=16G
#SBATCH -o jupyter-%j.log

# === Config ===
ENV_NAME="rhosts"
NB_ROOT="/data/etosato/RHOSTS"          # cartella che vuoi vedere in Jupyter
WORK_DIR="/data/etosato/RHOSTS/Notebooks"  # dove salviamo il log e partiamo

# === Ambiente ===
# Inizializza conda in shell non interattiva
if [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
    source "$HOME/miniconda3/etc/profile.d/conda.sh"
elif [ -f "/home/etosato/miniconda3/etc/profile.d/conda.sh" ]; then
    source "/home/etosato/miniconda3/etc/profile.d/conda.sh"
else
    echo "WARNING: conda.sh non trovato; fallback PATH"
    export PATH="$HOME/miniconda3/bin:$PATH"
fi

# Attiva l'ambiente
conda activate rhosts || {
    echo "ERRORE: impossibile attivare l'env 'rhosts'"; exit 1;
}

# === Porta libera ===
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

# Avvia Jupyter. Il warning "Fail to get yarn configuration" è innocuo.
# NB: root_dir = NB_ROOT come richiesto
jupyter lab --no-browser \
  --ip=0.0.0.0 \
  --port="$PORT" \
  --ServerApp.root_dir="$NB_ROOT"
