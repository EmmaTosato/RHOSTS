---
trigger: always_on
glob:
description: In this server, we execute the scripts using slurm. So, each time we run a script, we need to create a slurm job, and we cannot run in the node directly. Consider the basic slurm script template below:

```
#!/bin/sh
#SBATCH -J name_of_job
#SBATCH -p brains
#SBATCH --cpus-per-task=1
#SBATCH --mem=20G
#SBATCH -t 1-00:00:00
#SBATCH -o /data/etosato/RHOSTS/Logs/name_of_task/%x_%A_%a.out
#SBATCH -e /data/etosato/RHOSTS/Logs/name_of_task/%x_%A_%a.err
```

---

