# RHOSTS Higher-Order Analysis - Execution Guide

## Code Structure

```
src/
├── config.json              # Analysis configuration
├── run_analysis.sh          # SLURM launch script
├── subject_134829.txt       # Subject list (1 subject)
└── higher_order/
    ├── orchestration/
    │   └── main.py          # Main entry point
    ├── nodal_strength/
    │   ├── loaders_dv.py    # DV data loading (HDF5)
    │   ├── loaders_scaffold.py  # Scaffold data loading
    │   └── utils.py         # Frame selection
    └── visualization/
        ├── utils_neuromaps_brain.py  # Brain map (local)
        └── utils_nilearn_brain.py    # Headless fallback
```

## Configuration (config.json)

```json
{
    "mode": "dv",                    // "dv" or "scaffold"
    "scenario": "all_frames",        // "all_frames", "top_percent", "single_frame"
    "percent": 0.15,                 // Percentage (for top_percent)
    "metric": "coherence",           // "coherence" (DV) or "complexity" (scaffold)
    "subjects_list_file": "/.../subjects.txt",
    "data_path_pattern_dv": "/.../lorenzo_data/{subject}/{subject}_edge_projection.hd5",
    "data_path_pattern_scaffold": "/.../lorenzo_data/{subject}/generators",
    "indicators_path_pattern": "/.../lorenzo_data/{subject}/{subject}_indicators.txt",
    "num_rois": 116,                 // 116 (100 cortical + 16 subcortical) or 119 (100 cortical + 19 subcortical)
    "output_dir": "/.../node_strengths"
}
```

### ROI Configuration

The analysis supports two parcellation configurations:
- **116 ROI**: 100 cortical (Schaefer atlas) + 16 subcortical regions
- **119 ROI**: 100 cortical (Schaefer atlas) + 19 subcortical regions

**Important**: Set `num_rois` in `config.json` to match your input data dimensions.

### Parameters

| Parameter | Values | Description |
|-----------|--------|-------------|
| `mode` | `dv`, `scaffold` | Analysis type |
| `scenario` | `all_frames`, `top_percent`, `single_frame` | Frame selection |
| `percent` | 0.0-1.0 | Top/bottom percentage |
| `metric` | `coherence`, `complexity` | DV uses coherence (↑), scaffold uses complexity (↓) |
| `num_rois` | `116`, `119` | Number of ROIs: 116 (100+16) or 119 (100+19) |

### Subject List

Create a `.txt` file with one subject ID per line:
```
134829
393247
745555
```

## Execution

```bash
# 1. Edit config.json with desired parameters
nano src/config.json

# 2. Submit job
sbatch src/run_analysis.sh

# 3. Monitor
squeue -u $USER

# 4. Check logs
cat Logs/nodal_strength/rhosts_run_<JOBID>.out
```

## Output

`.npy` files are generated in:
```
Output/lorenzo_data/node_strengths/
├── dv/
│   ├── dv_all_frames_5subj.npy
│   └── dv_top15pct_coherence_5subj.npy
└── scaffold/
    ├── scaffold_all_frames_5subj.npy
    └── scaffold_top15pct_complexity_5subj.npy
```

Filename is auto-generated: `{mode}_{scenario}_{n}subj.npy`

## Common Use Cases

### DV - All frames, all subjects
```json
{"mode": "dv", "scenario": "all_frames", "subjects_list_file": ".../subjects.txt"}
```

### DV - Top 15% coherence, single subject
```json
{"mode": "dv", "scenario": "top_percent", "percent": 0.15, "metric": "coherence", "subjects_list_file": ".../subject_134829.txt"}
```

### Scaffold - Top 15% complexity, all subjects
```json
{"mode": "scaffold", "scenario": "top_percent", "percent": 0.15, "metric": "complexity", "subjects_list_file": ".../subjects.txt"}
```

---

## Local Visualization (for local agent)

The `.npy` files contain nodal strength vectors (116 or 119 values, depending on ROI configuration). Brain map images must be generated on a local machine with display capabilities.

### Instructions for Local Agent

Use `normal_view()` from `src/higher_order/visualization/utils_neuromaps_brain.py` to generate brain maps.

#### Usage Example

```python
from src.higher_order.visualization.utils_neuromaps_brain import normal_view
import matplotlib.colors as mcolors
import numpy as np

# Load data
data = np.load('dv_all_frames_5subj.npy')  # Shape: (116,) or (119,) depending on configuration

# Preferred colormap
cmap = mcolors.LinearSegmentedColormap.from_list(
    "green_yellow_red", ["#2ca25f", "#ffffbf", "#d73027"]
)

# Generate brain map
fig = normal_view(
    current_nodestrength=data,
    edges=True,
    cmap=cmap,
    q_thresh=0.0,
    center_cbar=True,
    alpha_graymap=0.99,
    xlabel=r"$\langle s_i \rangle$"
)

fig.savefig('brain_map.png', dpi=300, bbox_inches='tight')
```

#### Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `current_nodestrength` | - | ndarray (116,) or (119,) with nodal strength values |
| `edges` | False | Show parcellation outlines |
| `cmap` | 'RdBu_r' | Colormap (str or LinearSegmentedColormap) |
| `q_thresh` | 0.0 | Percentile threshold (0 = show all) |
| `center_cbar` | False | Center colorbar below the brain |
| `alpha_graymap` | 1.0 | Outline transparency |
| `xlabel` | `$<s_i>$` | Colorbar label |
