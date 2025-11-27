# Higher-Order Brain Network Analysis Workflow

This document explains exactly what happens when you run the analysis pipeline, specifically for the case of generating an image for **all frames** of a subject.

## 1. The Command
To analyze all frames for a subject (e.g., in `dv` mode), you run:

```bash
MODE=dv SCENARIO=all_frames sbatch src/higher_order/main.sh
```

## 2. Execution Flow

### Step 1: `main.sh` (The Orchestrator)
The bash script starts on a compute node.
1.  **Configuration**: It reads `MODE=dv` and `SCENARIO=all_frames`. It sets `METRIC=coherence` automatically because the mode is `dv`.
2.  **Input Selection**: It looks at `SLURM_ARRAY_TASK_ID` (e.g., 0) and reads the corresponding row from `Input/higher_order_inputs.tsv`.
    *   It identifies the data file: `.../134829_edge_projection.hd5`
    *   It identifies the indicator file: `.../134829_indicators.txt`
3.  **Environment**: It exports variables for headless rendering (`PYVISTA_OFF_SCREEN=true`, etc.) to prevent crashes.
4.  **Launch**: It calls Python with all the necessary arguments:
    ```bash
    python -m src.higher_order.main --mode dv --inputs ...hd5 --scenario all_frames --metric coherence ...
    ```

### Step 2: `main.py` (The Calculator)
The Python script takes over.
1.  **Setup**: It configures `matplotlib` to use the `Agg` backend (no window) to avoid errors.
2.  **Dispatch**: Based on `mode=dv`, it calls `compute_brainmap_dv` in `src/higher_order/maps/brain_map.py`.

### Step 3: `brain_map.py` (The Logic)
This module orchestrates the calculation.
1.  **`select_frames`**: Since `scenario=all_frames`, it selects **every** time point available in the HDF5 file.
2.  **`aggregate_frames`**:
    *   It loops through every selected frame.
    *   For each frame, it calls `load_single_frame_dv` (in `nodal_strength/nodal_strength_dv.py`).
    *   **`load_single_frame_dv`**: Reads the triangles for that specific time point and computes the nodal strength vector (size 100).
    *   It collects all these vectors and computes the **average** (mean) across time.
3.  **Result**: Returns a single array of shape (100,) representing the average nodal strength for that subject.

### Step 4: Back to `main.py` (Output)
1.  **Save Data**: It saves the result array to `Output/higher_order/dv/134829_all_frames.npy`.
2.  **Generate Image**:
    *   It calls `normal_view` from `src/higher_order/utils_neuromaps_brain.py`.
    *   It uses the "green_yellow_red" colormap.
    *   It generates a brain surface plot with the nodal strength values.
    *   It saves the figure to `Output/Images/dv/134829_all_frames.png`.

## 3. Group Analysis (Optional Final Step)
After running the above for all subjects, you can run the group analysis using the same `main.py` script with `mode=group`.

```bash
# Example: Average all .npy files in the output directory
python -m src.higher_order.main \
  --mode group \
  --inputs Output/higher_order/dv/*_all_frames.npy \
  --output-npy Output/higher_order/dv/GROUP_AVERAGE.npy \
  --output-img Output/Images/dv/GROUP_AVERAGE.png
```

1.  **`--mode group`**: Tells the script to expect `.npy` files as input.
2.  **`--inputs`**: A list of all the subject-level `.npy` files you want to average (use wildcards like `*`).
3.  **Logic**:
    *   It loads all the specified `.npy` files.
    *   It computes the **Grand Average** (mean of means).
    *   It saves the averaged data to `--output-npy`.
    *   It generates and saves the final group-level brain map image to `--output-img`.
## 4. Fully Automated Execution (Recommended)
To run the entire pipeline (subjects + group average) automatically, use the provided wrapper script:

```bash
# Usage: bash src/higher_order/launch_wrapper.sh [MODE] [SCENARIO] [NUM_SUBJECTS]
bash src/higher_order/launch_wrapper.sh dv all_frames 5
```

**What this does:**
1.  Submits the array job for the first 5 subjects (IDs 0-4).
2.  Automatically submits a **dependent job** for the group analysis.
3.  The group job waits in the queue until the array job finishes successfully.
4.  Once finished, it produces the group average image automatically.

**Note:** If you set `NUM_SUBJECTS` to 1, it skips the group analysis step.
