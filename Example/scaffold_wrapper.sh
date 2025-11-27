#!/bin/bash
#SBATCH -J scaffold_wrapper
#SBATCH -p brains
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH -t 00:10:00
#SBATCH -o /data/etosato/RHOSTS/Logs/%x_%j.out
#SBATCH -e /data/etosato/RHOSTS/Logs/%x_%j.err

set -euo pipefail

# Subject lists
subjects=(134829 393247 745555 905147 943862)

max_t=3599         # last timepoint
chunk_size=500     # Reduced to 500 to avoid array limit (MaxArraySize=1001)
concurrency=8

# Script scaffold
script="launch_High_order_TS_with_scaffold.sh"

prev_jid=""

for subj in "${subjects[@]}"; do
    start=0
    while [ "${start}" -le "${max_t}" ]; do
        end=$(( start + chunk_size - 1 ))
        if [ "${end}" -gt "${max_t}" ]; then
            end="${max_t}"
        fi

        # Smart Resume: Check if all output files for this chunk exist
        all_done=true
        for (( t=start; t<=end; t++ )); do
            # Output path matches launch_High_order_TS_with_scaffold.sh logic
            outfile="/data/etosato/RHOSTS/Output/lorenzo_data/${subj}/generators/generators__${t}.pck"
            if [ ! -f "${outfile}" ]; then
                all_done=false
                break
            fi
        done

        if [ "${all_done}" = "true" ]; then
            echo "Skipping subject=${subj} array ${start}-${end} (already done)"
            # Do not update prev_jid, so next job depends on the last *submitted* job (or runs immediately if none)
        else
            if [ -z "${prev_jid}" ]; then
                dep_opt=""
            else
                dep_opt="--dependency=afterok:${prev_jid}"
            fi

            echo "Submitting subject=${subj} array ${start}-${end}%${concurrency}"
            jid=$(sbatch ${dep_opt} --array=${start}-${end}%${concurrency} "${script}" "${subj}" | awk '{print $4}')
            prev_jid="${jid}"
        fi

        start=$(( end + 1 ))
    done
done
