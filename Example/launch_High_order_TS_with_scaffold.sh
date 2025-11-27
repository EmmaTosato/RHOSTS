#!/bin/sh
#SBATCH -J scaffold_brains
#SBATCH -p brains
#SBATCH --cpus-per-task=1
#SBATCH --mem=20G
#SBATCH -t 1-00:00:00
#SBATCH --array=0-0               # vero range lo passi con sbatch --array=...
#SBATCH -o /data/etosato/RHOSTS/Logs/%x_%A_%a.out
#SBATCH -e /data/etosato/RHOSTS/Logs/%x_%A_%a.err

set -euo pipefail

if [ $# -lt 1 ]; then
    echo "Usage: $0 SUBJECT_ID [OFFSET]" >&2
    exit 1
fi

subject="$1"
offset="${2:-0}"  # Default offset to 0 if not provided

# Memory Limits
export JAVA_TOOL_OPTIONS="-Xms2G -Xmx16G"

cd /data/etosato/RHOSTS/High_order_TS_with_scaffold/

# Input codes and files
codepath="simplicial_multivariate.py"
filename="../Input/lorenzo_data/cortical_subcortical/${subject}_ts_zscore_ctx_sub.txt"
javaplexpath="javaplex/javaplex.jar"
outtag="scaffold_"

# Current time of the arry
t=$((SLURM_ARRAY_TASK_ID + offset))
tnext=$((t+1))

# Output folder
outdir="../Output/lorenzo_data/${subject}/generators"
failfile="../Output/lorenzo_data/${subject}/fails.txt"
mkdir -p "${outdir}"
mkdir -p scaffold_gen

echo "---- Starting scaffold subject=${subject}, t=${t} ----"
date

if python "${codepath}" "${filename}" -t "${t}" "${tnext}" -p 1 -j "${javaplexpath}" "${outtag}"; then
    # Sposta SOLO il file generato da questo t
    if [ -f "scaffold_gen/generators__${t}.pck" ]; then
        mv "scaffold_gen/generators__${t}.pck" "${outdir}/"
    fi
else
    # Append con lock per evitare scritture concorrenti
    {
        flock -w 10 9 || true
        echo "${t}" >&9
    } 9>> "${failfile}"
fi

echo "---- Finished scaffold subject=${subject}, t=${t} ----"
date
