#!/bin/sh
#SBATCH -J scaffold_brains
#SBATCH -p brains
#SBATCH --cpus-per-task=1
#SBATCH --mem=20G
#SBATCH -t 1-00:00:00
#SBATCH --array=51-1199%8
#SBATCH -o /data/etosato/RHOSTS/Logs/%x_%A_%a.out
#SBATCH -e /data/etosato/RHOSTS/Logs/%x_%A_%a.err

set -euo pipefail

# Limiti memoria JVM
export JAVA_TOOL_OPTIONS="-Xms2G -Xmx16G"

# Dir di lavoro richiesto dalla pipeline
cd ../High_order_TS_with_scaffold/

codepath="simplicial_multivariate.py"
filename="./../Input/subject1_left.txt"
javaplexpath="javaplex/javaplex.jar"
outtag="scaffold_"   # prefisso output (come negli esempi originali)

# Tempo corrente dell'array
t=${SLURM_ARRAY_TASK_ID}
tnext=$((t+1))

# Assicura cartelle output esistano
mkdir -p ../Output/generators1200
mkdir -p ../Example

echo "---- Starting scaffold for t=${t} ----"
date

# Esecuzione: una JVM per job -> -p 1
if python "${codepath}" "${filename}" -t "${t}" "${tnext}" -p 1 -j "${javaplexpath}" "${outtag}"; then
  # Sposta SOLO il file generato da questo t per evitare race conditions
  if [ -f scaffold_gen/generators__${t}.pck ]; then
    mv "scaffold_gen/generators__${t}.pck" ../Output/
  fi
else
  # Append con lock per evitare scritture concorrenti
  {
    flock -w 10 9 || true
    echo "${t}" >&9
  } 9>> ../Example/fails.txt
fi

echo "---- Finished scaffold for t=${t} ----"
date

# Torna alla cartella Example (non spostiamo la cartella intera per evitare conflitti tra task)
cd /data/etosato/RHOSTS/Example
