# PNC Server Rules

Rules specific to the **my lo local environment**.

---

## Project Location

All projects on this server are located under:
```
/Users/emmatosato/Documents/PhD/Projects/
```

---

## Environment Setup

### Conda Activation
Always activate the conda environment before executing any scripts or commands.

**The specific environment name is defined in `specific-project.md`.**

```bash
conda activate <environment_name>
```

---

## Getting context
Read always documentaions files. 
- Search for the doc folder
- If not found, search for the specific-project.md file. 
- Explore all the files in the project folder to get a better understanding of the project.

---

## Folder Organization

### Logs

#### Directory Structure
Every project must have a **`logs/`** directory at the root level:
```
/Users/emmatosato/Documents/PhD/Projects/<project_name>/logs/
```

#### Organization Guidelines
- Create a **subfolder for each task** or category of operations
- Use clear, descriptive names that reflect the task being executed
- Logs can be for the job (we use slurm in this server), or a script
- **Reuse existing folders** when continuing the same task across different chat sessions
- Always verify with the user before creating new log folders to avoid duplicates

**Example:**
```
/Users/emmatosato/Documents/PhD/Projects/RHOSTS/
├── logs/
│   ├── scaffold_brains/
│   │   ├── job_123.out
│   │   └── job_123.err
│   └── test_reports/
│       └── generation_tests/
```

#### Test Logs
For tests that generate logs:
- Create a **`test_reports/`** subfolder within `logs/`.
- Organize into further subfolders by test type.
- Example: `/data/etosato/<project>/logs/test_reports/<test_type>/`

### Test 
For test scripts within the `test/` directory:
- Create a **subfolder for each task** being tested.
- Use clear, descriptive names that reflect the task being tested.
- **Reuse existing folders** when continuing the same task across different chat sessions.

**Example:**
```
/Users/emmatosato/Documents/PhD/Projects/<project>/
├── test/
│   ├── scaffold_generation/
│   │   ├── test_scaffold_integrity.py
│   │   └── run_scaffold_tests.sh
│   └── visualization/
│       ├── test_brain_maps.py
│       └── test_nilearn.py
```

---

## SLURM Execution

### Required
On this server, **all script executions must be submitted as SLURM jobs**. Scripts cannot be run directly on the compute node.

### Template
Use this template for SLURM job scripts:

```bash
#!/bin/sh
#SBATCH -J name_of_job
#SBATCH -p brains
#SBATCH --cpus-per-task=1
#SBATCH --mem=20G
#SBATCH -t 1-00:00:00
#SBATCH -o /data/etosato/<project>/Logs/name_of_task/%x_%A_%a.out
#SBATCH -e /data/etosato/<project>/Logs/name_of_task/%x_%A_%a.err
```

### Parameters
- `-J`: Job name
- `-p`: Partition (use `brains`)
- `--cpus-per-task`: Number of CPUs (adjust as needed)
- `--mem`: Memory allocation (adjust as needed)
- `-t`: Time limit (format: `days-hours:minutes:seconds`)
- `-o`: Standard output log path
- `-e`: Standard error log path

### Important
- Adjust resource allocations based on task requirements
- Ensure log directories exist before submitting jobs
- Use `%x_%A_%a` pattern for job name, job ID, and array task ID

---

## Project-Specific Information

**Check `specific-project.md`** for the ulterior info you need. For example:
- Conda environment name
- Project-specific directory structure
- Additional configurations
