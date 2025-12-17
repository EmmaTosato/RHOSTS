# PNC Server Rules

Rules specific to the **PNC server environment**.

---

## Project Location

All projects on this server are located under:
```
/data/etosato/
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

## Context Gathering Rules

**MANDATORY: Before starting any task, you MUST execute these steps in order:**

1. **FIRST**: Locate and read all documentation files:
   - Search for `docs/`, `doc/`, or `Docs/` folders
   - Look for README files, markdown files, or any documentation
   - Read ALL documentation files found

2. **SECOND**: Read the `specific-project.md` file to understand project-specific configurations

3. **THIRD**: Explore and understand the project structure:
   - Identify main code directories
   - Understand the project organization
   - Read key configuration files (package.json, requirements.txt, setup.py, etc.)

4. **ONLY THEN**: Proceed with the requested task

**These steps are NOT optional - execute them every time before starting work.**

---

## Documentation Tracking

**MANDATORY: Document all work performed:**

1. **Create or update documentation** for every task completed
2. **Track progress and decisions** made during development
3. **Document code structure and functionality** in appropriate files
4. **User responsibility**: After task completion, the user will decide whether to:
   - Keep documentation as-is
   - Merge content with existing documentation
   - Remove or reorganize documentation
   - Use the agent to perform documentation management

**The agent must maintain clear records of all work for user review.**

---

## Communication Guidelines

**Documentation and Code - STRICT RULES:**
- **ABSOLUTELY NO emoticons** in any documentation files, code comments, or configuration files
- **ZERO TOLERANCE** for emoticons in source code, scripts, or technical documentation
- Keep all written content professional and clear
- Use plain text formatting for emphasis instead of emoticons
- **VIOLATION OF THIS RULE IS UNACCEPTABLE**

---

## Folder Organization

### Source Code Directory Structure

**Every project MUST have a `src/` directory at the root for source code:**
```
/data/etosato/<project_name>/src/
```

**Organization rules:**
- Organize code by **macro tasks** agreed upon with the user
- Create clear, descriptive folder names that reflect the main functionality
- Maintain separation between different major components

**Example structure:**
```
/data/etosato/RHOSTS/
├── src/
│   ├── data_processing/
│   │   ├── preprocessing.py
│   │   └── cleaning.py
│   ├── analysis/
│   │   ├── statistical_analysis.py
│   │   └── visualization.py
│   └── models/
│       ├── neural_network.py
│       └── evaluation.py
```

### Output Directory Structure

**Every project MUST have an `output/` directory at the root for generated outputs:**
```
/data/etosato/<project_name>/output/
```

**Organization rules:**
- Organize outputs by **task or analysis type** agreed upon with the user
- Use clear, descriptive subfolder names
- Maintain consistency with source code organization where applicable

**Example structure:**
```
/data/etosato/RHOSTS/
├── output/
│   ├── processed_data/
│   │   ├── cleaned_dataset.csv
│   │   └── normalized_features.pkl
│   ├── figures/
│   │   ├── correlation_plots/
│   │   └── model_performance/
│   └── results/
│       ├── model_predictions.json
│       └── statistical_summary.txt
```

### Logs

#### Directory Structure
Every project must have a **`logs/`** directory at the root level:
```
/data/etosato/<project_name>/Logs/
```

#### Organization Guidelines
- Create a **subfolder for each task** or category of operations
- Use clear, descriptive names that reflect the task being executed
- Logs can be for the job (we use slurm in this server), or a script
- **Reuse existing folders** when continuing the same task across different chat sessions
- Always verify with the user before creating new log folders to avoid duplicates

**Example:**
```
/data/etosato/RHOSTS/
├── logs/
│   ├── scaffold_brains/
│   │   ├── job_123.out
│   │   └── job_123.err
│   └── test_reports/
│       └── generation_tests/
```

#### Test Logs
For tests that generate logs:
- Create a **`test_reports/`** subfolder within `Logs/`.
- Organize into further subfolders by test type.
- Example: `/data/etosato/<project>/Logs/test_reports/<test_type>/`

### Test 
For test scripts within the `Test/` directory:
- Create a **subfolder for each task** being tested.
- Use clear, descriptive names that reflect the task being tested.
- **Reuse existing folders** when continuing the same task across different chat sessions.

**Example:**
```
/data/etosato/<project>/
├── Test/
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

**Check `specific-project.md`** for additional information you need. For example:
- Conda environment name
- Project-specific directory structure
- Additional configurations
