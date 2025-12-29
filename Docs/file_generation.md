# Output File Generation Guide

This guide describes how to generate output files (`.txt`, `.hd5`, `.pck`) for each subject using the RHOSTS pipeline on the PNC server.

---

## Pipeline Overview

The RHOSTS pipeline generates three main types of output files for each subject:

| File | Description | Script |
|------|-------------|--------|
| `{subject}_indicators.txt` | Higher-order indicators for each timepoint | `High_order_TS/simplicial_multivariate.py` |
| `{subject}_edge_projection.hd5` | Weighted projection of violating triangles onto edges | `High_order_TS/simplicial_multivariate.py` |
| `generators/generators__{t}.pck` | Homological generators (scaffold) for each timepoint | `High_order_TS_with_scaffold/simplicial_multivariate.py` |

---

## Prerequisites

### Conda Environment
```bash
conda activate rhosts
```

### Required Input Structure
Input data must be `.txt` files containing z-scored multivariate time series:
- **Format**: columns = brain regions (ROI), rows = timepoints
- **Location**: `/data/etosato/RHOSTS/Input/lorenzo_data/cortical_subcortical/{subject}_ts_zscore_ctx_sub.txt`

### Output Directories
Ensure the output folder for the subject exists:
```bash
mkdir -p /data/etosato/RHOSTS/Output/lorenzo_data/{subject}
mkdir -p /data/etosato/RHOSTS/Output/lorenzo_data/{subject}/generators
```

---

## 1. Generating TXT and HD5 Files (Edge Projection)

### What It Produces
- **`{subject}_indicators.txt`**: Text file with 7 columns for each timepoint:
  1. Time
  2. Hyper complexity indicator
  3. Hyper complexity FC (Fully Coherent)
  4. Hyper complexity CT (Coherent Transition)
  5. Hyper complexity FD (Fully Decoherent)
  6. Hyper coherence indicator
  7. Average edge violation

- **`{subject}_edge_projection.hd5`**: HDF5 file with a dataset for each timepoint, containing the projection of violating triangles onto edges (4 columns: node_i, node_j, weight_sum, count)

### Script to Use
`/data/etosato/RHOSTS/High_order_TS/simplicial_multivariate.py`

### How to Execute

#### SLURM Job (Recommended)
Use the example script: [launch_High_order_TS_with_edgesaving.sh](file:///data/etosato/RHOSTS/Example/launch_High_order_TS_with_edgesaving.sh)

```bash
#!/bin/sh
#SBATCH -J edge_weight_brains
#SBATCH -p brains
#SBATCH --cpus-per-task=5
#SBATCH --mem=32G
#SBATCH -t 1-00:00:00
#SBATCH -o /data/etosato/RHOSTS/Logs/edge_projection/%A_%a.out
#SBATCH -e /data/etosato/RHOSTS/Logs/edge_projection/%A_%a.err

# Subject definition
subjects=("134829" "393247" "745555" "905147" "943862")
sub=${subjects[$SLURM_ARRAY_TASK_ID]}

# Paths
codepath="/data/etosato/RHOSTS/High_order_TS/simplicial_multivariate.py"
filename="/data/etosato/RHOSTS/Input/lorenzo_data/cortical_subcortical/${sub}_ts_zscore_ctx_sub.txt"
weighted_network="/data/etosato/RHOSTS/Output/lorenzo_data/${sub}/${sub}_edge_projection"
result_file="/data/etosato/RHOSTS/Output/lorenzo_data/${sub}/${sub}_indicators.txt"

# Create directories
mkdir -p "$(dirname "$weighted_network")"
mkdir -p "$(dirname "$result_file")"

# Execution: -t 0 3600 = timepoints from 0 to 3600, -p 5 = 5 cores, -s = save edge weights
python ${codepath} ${filename} -t 0 3600 -p 5 -s ${weighted_network} > ${result_file}
```

#### Job Submission
```bash
# For all subjects (array job)
sbatch --array=0-4 /data/etosato/RHOSTS/Example/launch_High_order_TS_with_edgesaving.sh

# For a single subject (modify the array index)
sbatch --array=0 /data/etosato/RHOSTS/Example/launch_High_order_TS_with_edgesaving.sh
```

### CLI Parameters

| Parameter | Description |
|-----------|-------------|
| `<filename>` | Path to input file with time series |
| `-t t0 T` | Time range [t0, T] to analyze |
| `-p #core` | Number of cores for parallel computation |
| `-s <filename>` | Save edge weights to `<filename>.hd5` |
| `-n` | Compute indicators for null model (shuffle) |

---

## 2. Generating PCK Files (Scaffold/Generators)

### What It Produces
- **`generators/generators__{t}.pck`**: Pickle file for each timepoint containing H₁ homological generators (persistent cycles). Each file contains a dictionary with:
  - Homology groups (typically H1)
  - List of generators (cycles)
  - Persistence intervals (birth, death)

### Script to Use
`/data/etosato/RHOSTS/High_order_TS_with_scaffold/simplicial_multivariate.py`

### How to Execute

#### SLURM Job for Single Timepoint
Use the script: [launch_High_order_TS_with_scaffold.sh](file:///data/etosato/RHOSTS/Example/launch_High_order_TS_with_scaffold.sh)

This script processes **a single timepoint** per execution, using SLURM job arrays.

```bash
#!/bin/sh
#SBATCH -J scaffold_brains
#SBATCH -p brains
#SBATCH --cpus-per-task=1
#SBATCH --mem=20G
#SBATCH -t 1-00:00:00
#SBATCH --array=0-0  # Range passed with sbatch --array=...
#SBATCH -o /data/etosato/RHOSTS/Logs/scaffold_generation/%x_%A_%a.out
#SBATCH -e /data/etosato/RHOSTS/Logs/scaffold_generation/%x_%A_%a.err

set -eo pipefail

if [ $# -lt 1 ]; then
    echo "Usage: $0 SUBJECT_ID [OFFSET]" >&2
    exit 1
fi

subject="$1"
offset="${2:-0}"  # Default offset to 0

# Conda
source /home/etosato/miniconda3/etc/profile.d/conda.sh
conda activate rhosts

# Java/Javaplex settings
export JAVA_TOOL_OPTIONS="-Xms2G -Xmx16G"

cd /data/etosato/RHOSTS/High_order_TS_with_scaffold/

# Paths
codepath="simplicial_multivariate.py"
filename="../Input/lorenzo_data/cortical_subcortical/${subject}_ts_zscore_ctx_sub.txt"
javaplexpath="javaplex/javaplex.jar"
outtag="scaffold_"

# Calculate current timepoint
t=$((SLURM_ARRAY_TASK_ID + offset))
tnext=$((t+1))

# Output
outdir="../Output/lorenzo_data/${subject}/generators"
failfile="../Output/lorenzo_data/${subject}/fails.txt"
mkdir -p "${outdir}"
mkdir -p scaffold_gen

# Smart Resume: skip if file already exists and is valid
outfile="${outdir}/generators__${t}.pck"
if [ -f "${outfile}" ]; then
    if python -c "import pickle; pickle.load(open('${outfile}', 'rb'))" 2>/dev/null; then
        echo "Skipping subject=${subject}, t=${t} (File exists and is valid)"
        exit 0
    else
        echo "Warning: File ${outfile} exists but is corrupted. Regenerating..."
        rm -f "${outfile}"
    fi
fi

echo "---- Starting scaffold subject=${subject}, t=${t} ----"
date

# Execution
if python "${codepath}" "${filename}" -t "${t}" "${tnext}" -p 1 -j "${javaplexpath}" "${outtag}"; then
    if [ -f "scaffold_gen/generators__${t}.pck" ]; then
        mv "scaffold_gen/generators__${t}.pck" "${outdir}/"
    fi
else
    # Log failures
    {
        flock -w 10 9 || true
        echo "${t} Job:${SLURM_JOB_ID} Array:${SLURM_ARRAY_TASK_ID}" >&9
    } 9>> "${failfile}"
fi

echo "---- Finished scaffold subject=${subject}, t=${t} ----"
date
```

#### Job Submission for Timepoint Range
```bash
# Single subject, timepoints 0-99
sbatch --array=0-99 launch_High_order_TS_with_scaffold.sh 134829

# Single subject, timepoints 500-599 (with offset)
sbatch --array=0-99 launch_High_order_TS_with_scaffold.sh 134829 500
```

#### Wrapper for All Subjects and Timepoints
Use the script: [scaffold_wrapper.sh](file:///data/etosato/RHOSTS/Example/scaffold_wrapper.sh)

This wrapper automatically handles:
- All subjects in sequence
- Splitting into 500-timepoint chunks
- Smart resume (skips existing files)
- Job dependencies

```bash
# Submit the wrapper that will handle everything automatically
sbatch scaffold_wrapper.sh
```

### CLI Parameters (Scaffold)

| Parameter | Description |
|-----------|-------------|
| `<filename>` | Path to input file with time series |
| `-t t0 T` | Time range [t0, T] to analyze |
| `-p #core` | Number of cores (use 1 for scaffold) |
| `-j <path_javaplex> <outdir>` | Enable scaffold computation with javaplex |
| `-s <filename>` | Save edge weights (optional) |
| `-n` | Compute indicators for null model |

> [!WARNING]
> Scaffold computation requires significant RAM (~16-20GB per timepoint). It is recommended to process one timepoint at a time with `--cpus-per-task=1`.

---

## Output Structure per Subject

After complete execution, the structure for each subject will be:

```
/data/etosato/RHOSTS/Output/lorenzo_data/{subject}/
├── {subject}_indicators.txt       # Higher-order indicators
├── {subject}_edge_projection.hd5  # Triangle projection onto edges
├── fails.txt                      # Log of failed timepoints (scaffold)
└── generators/                    # Scaffold generators
    ├── generators__0.pck
    ├── generators__1.pck
    ├── generators__2.pck
    └── ... (one file per timepoint)
```

---

## Complete Example: New Subject

### Step 1: Prepare Input Data
```bash
# Copy z-scored time series to the correct location
cp /path/to/my_data.txt /data/etosato/RHOSTS/Input/lorenzo_data/cortical_subcortical/NEWSUB_ts_zscore_ctx_sub.txt
```

### Step 2: Create Output Directory
```bash
mkdir -p /data/etosato/RHOSTS/Output/lorenzo_data/NEWSUB/generators
```

### Step 3: Verify Log Directories
```bash
mkdir -p /data/etosato/RHOSTS/Logs/edge_projection
mkdir -p /data/etosato/RHOSTS/Logs/scaffold_generation
```

### Step 4: Generate TXT and HD5
```bash
# Create custom SLURM script or modify launch_High_order_TS_with_edgesaving.sh
sbatch my_edge_job.sh NEWSUB
```

### Step 5: Generate PCK (Scaffold)
```bash
# Use the wrapper or submit directly
sbatch --array=0-3599 launch_High_order_TS_with_scaffold.sh NEWSUB
```

### Step 6: Verify Completeness
```bash
# Count generated generator files
ls /data/etosato/RHOSTS/Output/lorenzo_data/NEWSUB/generators/ | wc -l

# Check for failures
cat /data/etosato/RHOSTS/Output/lorenzo_data/NEWSUB/fails.txt
```

---

## Troubleshooting

### Insufficient Memory (Scaffold)
- Increase `--mem` in the SLURM job
- Reduce `JAVA_TOOL_OPTIONS` Xmx if necessary

### Corrupted PCK Files
- The script detects and regenerates them automatically
- Delete manually: `rm generators__XXX.pck`

### Missing Timepoints
- Check `fails.txt` to identify which ones failed
- Resubmit only the missing ones with a specific array

### Javaplex Errors
- Verify that `JAVA_TOOL_OPTIONS` is set correctly
- Ensure `javaplex.jar` is accessible

---

## References

- [Main README](file:///data/etosato/RHOSTS/Docs/README.md)
- [Code Explanation](file:///data/etosato/RHOSTS/Docs/code_explanation.md)
- [Analysis Execution Guide](file:///data/etosato/RHOSTS/Docs/guida_esecuzione.md)