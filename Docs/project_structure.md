# Project Structure Documentation

This document describes the organization and purpose of directories and key files in the RHOSTS project.

## Directory Structure Overview

```
RHOSTS/
├── assets/                     # Project assets and resources
│   └── atlases/               # Brain atlases for ROI definition
│       ├── cortex_100.nii.gz  # Cortical atlas (100 ROIs)
│       └── subcortex_16.nii   # Subcortical atlas (16 ROIs)
├── Docs/                      # Documentation
├── High_order_TS/             # Core algorithms (basic version)
├── High_order_TS_with_scaffold/ # Algorithms with scaffold computation
├── Input/                     # Input data and examples
├── Logs/                      # Log files organized by type
├── Notebooks/                 # Jupyter notebooks for analysis
├── Output/                    # Generated output files
├── src/                       # Source code
├── Test/                      # Test scripts
├── utils/                     # Utility scripts
└── External/                  # External dependencies
```

## Detailed Directory Descriptions

### Core Directories

#### `assets/atlases/`
Contains brain atlases used for ROI (Region of Interest) definition:
- **Purpose**: Reference files for preprocessing fMRI data
- **Contents**: 
  - `cortex_100.nii.gz`: Schaefer cortical atlas with 100 regions
  - `subcortex_16.nii`: Subcortical atlas with 16 regions
- **Usage**: Required by preprocessing scripts to extract ROI time series

#### `src/`
Source code organized by functionality:
```
src/
├── config/                    # Configuration files
├── higher_order/              # Main analysis modules
│   ├── nodal_strength/        # Node strength computation
│   ├── orchestration/         # Main entry points
│   └── visualization/         # Brain visualization tools
├── launchers/                 # SLURM job scripts
└── preprocessing/             # Data preprocessing tools
```

#### `High_order_TS/`
Basic implementation of higher-order time series analysis:
- **Purpose**: Compute topological indicators (complexity, coherence)
- **Key files**: `simplicial_multivariate.py`, `utils.py`
- **Output**: Indicators and edge projections

#### `High_order_TS_with_scaffold/`
Extended implementation including homological scaffold computation:
- **Purpose**: Advanced topological analysis with scaffold structures  
- **Dependencies**: Requires Javaplex and Jython
- **Output**: Generators and scaffold structures

### Data Directories

#### `Input/`
Input data and examples:
- **Structure**: Organized by dataset (e.g., `lorenzo_data/`)
- **Format**: Typically `.txt` files with z-scored time series
- **Dimensions**: ROI × timepoints matrices

#### `Output/`
Generated analysis results:
- **Structure**: Organized by subject and analysis type
- **Contents**: 
  - `.txt` files: Topological indicators
  - `.hd5` files: Edge projections and network data
  - `.pck` files: Scaffold generators (excluded from git)

#### `Logs/`
Organized by log type:
- `slurm/`: SLURM job outputs and errors
- `tests/`: Test execution logs  
- `development/`: Development and debugging logs

### Support Directories

#### `Notebooks/`
Jupyter notebooks for:
- Data exploration and visualization
- Analysis pipelines
- Result interpretation
- Tutorial examples

#### `External/`
External dependencies organized by language:
- `jython/`: Jython, Javaplex libraries
- `phat/`: PHAT library for persistent homology
- `surfplot/`: Surface plotting utilities

#### `utils/`
General utility scripts and helper functions.

#### `test/`
Test scripts organized by functionality being tested.

## Configuration Files

### Root Level
- `environment.yml`: Conda environment specification
- `requirements.txt`: Python dependencies
- `.gitignore`: Git ignore patterns optimized for the project structure

### Source Code
- `src/config/config.json`: Main analysis configuration
- `src/config/*.txt`: Subject lists for different analyses

## Data Flow

1. **Raw Data**: Stored externally (e.g., `/data/etosato/raw_data/`)
2. **Preprocessing**: Uses `assets/atlases/` to extract ROI time series → `input/`
3. **Analysis**: Processes `input/` data → `output/`
4. **Visualization**: Uses `output/` results to generate brain maps

## Best Practices

### Adding New Atlases
Place new atlases in `assets/atlases/` and update:
- Preprocessing scripts in `src/preprocessing/`
- Configuration files in `src/config/`
- This documentation

### Log Organization
Create new subdirectories in `log/` for new analysis types:
- Use descriptive names
- Add `.gitkeep` files to maintain structure
- Update `.gitignore` patterns as needed

### Documentation Updates
When adding new directories or changing structure:
1. Update this file (`project_structure.md`)
2. Update relevant analysis documentation
3. Update installation/setup instructions if needed