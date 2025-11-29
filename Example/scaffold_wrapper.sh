#!/bin/bash
#SBATCH -J scaffold_wrapper
#SBATCH -p brains
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH -t 00:10:00
#SBATCH -o /data/etosato/RHOSTS/Logs/scaffold_generation/%x_%j.out
#SBATCH -e /data/etosato/RHOSTS/Logs/scaffold_generation/%x_%j.err

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
        
        # Calculate array size for this chunk (0 to N-1)
        count=$(( end - start + 1 ))
        array_limit=$(( count - 1 ))

        # Smart Resume: Check if all output files for this chunk exist
        all_done=true
        for (( i=0; i<=array_limit; i++ )); do
            t=$(( start + i ))
            # Output path matches launch_High_order_TS_with_scaffold.sh logic
            outfile="/data/etosato/RHOSTS/Output/lorenzo_data/${subj}/generators/generators__${t}.pck"
            if [ ! -f "${outfile}" ]; then
                all_done=false
                break
            fi
        done

        if [ "${all_done}" = "true" ]; then
            echo "Skipping subject=${subj} range ${start}-${end} (already done)"
            # Do not update prev_jid
        else
            if [ -z "${prev_jid}" ]; then
                dep_opt=""
            else
                # Use afterany so the next job starts even if the previous one has failed tasks
                dep_opt="--dependency=afterany:${prev_jid}"
            fi

            echo "Submitting subject=${subj} range ${start}-${end} (Array 0-${array_limit}, Offset ${start})"
            # Pass 'start' as the offset
            jid=$(sbatch ${dep_opt} --array=0-${array_limit}%${concurrency} "${script}" "${subj}" "${start}" | awk '{print $4}')
            prev_jid="${jid}"
        fi

        start=$(( end + 1 ))
    done
done
