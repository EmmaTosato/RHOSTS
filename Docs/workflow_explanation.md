# Higher-Order Brain Network Analysis Workflow

This document explains the two main ways to run the analysis pipeline using `main.sh`.
The logic applies to both `dv` (HDF5) and `scaffold` (Generators) modes.

## Case 1: Single Subject Analysis
**Goal:** Analyze one specific subject to check their individual results.

### 1. The Command
To run only the first subject (Index 0) in `dv` mode:

```bash
SUBJECT_RANGE=0 sbatch src/higher_order/main.sh
```

### 2. What Happens (Step-by-Step)
1.  **Job Start**: SLURM starts a single job.
2.  **Selection**: The script sees `SUBJECT_RANGE=0`, so it picks only the first subject from the input table (e.g., `134829`).
3.  **Processing**:
    *   It calculates the nodal strength (e.g., for `all_frames`).
    *   It saves the data to `Output/lorenzo_data/node_strengths/dv/134829_all_frames.npy`.
4.  **Image Generation**:
    *   Since **only 1 subject** was selected, the script **GENERATES** the individual brain map image.
    *   It saves the image to `Output/lorenzo_data/images/dv/134829_all_frames.png`.
5.  **Group Analysis**: Skipped (N=1).

### 3. Final Output
*   `Output/lorenzo_data/node_strengths/dv/134829_all_frames.npy`
*   `Output/lorenzo_data/images/dv/134829_all_frames.png`

---

## Case 2: All Subjects Analysis (Group Study)
**Goal:** Analyze the entire cohort and get the group average.

### 1. The Command
To run all subjects (e.g., indices 0 to 4) in `dv` mode:

```bash
SUBJECT_RANGE=0-4 sbatch src/higher_order/main.sh
```

### 2. What Happens (Step-by-Step)
1.  **Job Start**: SLURM starts a single job.
2.  **Selection**: The script sees `SUBJECT_RANGE=0-4`, so it prepares to loop from subject 0 to 4.
3.  **Processing Loop**:
    *   **Subject 0**: Calculates data -> Saves `.npy`. **SKIPS** individual image.
    *   **Subject 1**: Calculates data -> Saves `.npy`. **SKIPS** individual image.
    *   ...
    *   **Subject 4**: Calculates data -> Saves `.npy`. **SKIPS** individual image.
4.  **Group Analysis**:
    *   The script detects that multiple subjects were processed (N > 1).
    *   It automatically launches the group analysis routine.
    *   It loads all the `.npy` files just created.
    *   It computes the **Grand Average** (mean of all subjects).
5.  **Image Generation**:
    *   It generates the **Group Average** brain map image.
    *   It saves the image to `Output/lorenzo_data/images/dv/group_average_all_frames.png`.

### 3. Final Output
*   **Individual Data**: 5 files in `Output/lorenzo_data/node_strengths/dv/*.npy`
*   **Group Data**: `Output/lorenzo_data/node_strengths/dv/group_average_all_frames.npy`
*   **Group Image**: `Output/lorenzo_data/images/dv/group_average_all_frames.png`
*   *(Note: No individual images are created to save space)*

