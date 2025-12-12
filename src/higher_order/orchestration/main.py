"""
Main entry point for RHOSTS Higher-Order Analysis.
Configured via JSON file.
"""

import argparse
import json
import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# Import loaders and utilities
from ..nodal_strength.loaders_dv import load_single_frame_dv
from ..nodal_strength.loaders_scaffold import load_single_frame_scaffold
from ..nodal_strength.utils import select_frames
from ..visualization.utils_neuromaps_brain import normal_view


def load_config(config_path):
    with open(config_path, 'r') as f:
        return json.load(f)

def get_subject_list(subjects_file):
    """Read subject IDs from a text file."""
    if not os.path.exists(subjects_file):
        raise FileNotFoundError(f"Subjects file not found: {subjects_file}")
    with open(subjects_file, 'r') as f:
        # Read lines, strip whitespace, ignore empty lines/comments
        subjects = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return subjects

def main():
    parser = argparse.ArgumentParser(description="Run RHOSTS Higher-Order Analysis")
    parser.add_argument("--config", required=True, help="Path to JSON configuration file")
    args = parser.parse_args()

    # 1. Load Configuration
    config = load_config(args.config)
    print(f"Loaded configuration from {args.config}")

    mode = config['mode']  # "dv" or "scaffold"
    scenario = config['scenario']
    num_rois = config.get('num_rois', 116)
    
    # 2. Get Subject List
    subjects = get_subject_list(config['subjects_list_file'])
    print(f"Found {len(subjects)} subjects to process.")

    # 3. Parameter Mapping for Frame Selection
    metric = config.get('metric', 'coherence')
    percent = config.get('percent', 0.15)
    
    # Logic: 
    # Coherence -> High Values (Desc) -> Col 5 (Hyper-Coherence)
    # Complexity -> Low Values (Asc) -> Col 1 (Hyper-Complexity)
    if metric == 'coherence':
        value_col = 5
        order = 'desc'
    elif metric == 'complexity':
        value_col = 1
        order = 'asc'
    else:
        # Fallback/Custom (user can define col/order in config if needed in future)
        value_col = config.get('custom_metric_col', 5)
        order = config.get('custom_order', 'desc')

    # 4. Processing Loop
    subject_averages = []

    for subj_id in subjects:
        try:
            # Resolve paths
            data_path = config['data_path_pattern'].format(subject=subj_id, mode=mode)
            indicators_path = config['indicators_path_pattern'].format(subject=subj_id, mode=mode)
            
            # Select Frames
            # Note: For 'top_percent', we need the indicators file.
            # For 'all_frames' in Scaffold, we need the directory.
            # select_frames handles input types (file vs dir) internally based on mode/input.
            
            # Prepare inputs for select_frames
            # DV mode uses hdf5 file, Scaffold uses directory
            if mode == 'dv':
                input_source = data_path
                loader_fn = load_single_frame_dv
            else: # scaffold
                # data_path should be the directory for scaffold
                # If pattern points to a file inside, we should take dirname?
                # User config pattern usually points to the resource.
                # For scaffold, it's a directory.
                input_source = data_path 
                loader_fn = load_single_frame_scaffold

            # Select frames for this subject
            frames = select_frames(
                hd5_files=[input_source], # Pass as list
                scenario=scenario,
                frame=config.get('frame'),
                percent=percent,
                sorted_output_txt=indicators_path,
                value_col=value_col,
                order=order
            )
            
            if not frames:
                print(f"WARNING: No frames selected for subject {subj_id}. Skipping.")
                continue

            # Average over Timepoints (Inner Loop)
            # Implements: "Medio sui timepoints"
            time_accum = np.zeros(num_rois, dtype=float)
            valid_frames = 0
            
            for frame in frames:
                try:
                    nodal = loader_fn(input_source, frame, num_rois)
                    time_accum += nodal
                    valid_frames += 1
                except Exception as e:
                    print(f"  Error loading frame {frame} for {subj_id}: {e}")
            
            if valid_frames > 0:
                subject_avg = time_accum / valid_frames
                subject_averages.append(subject_avg)
                # print(f"Processed subject {subj_id}: {valid_frames} frames.")
            else:
                print(f"WARNING: No valid frames loaded for subject {subj_id}.")

        except Exception as e:
            print(f"ERROR processing subject {subj_id}: {e}")
            continue

    # 5. Average over Subjects (Outer Loop)
    # Implements: "Medio sui soggetti"
    if not subject_averages:
        print("ERROR: No subjects successfully processed.")
        sys.exit(1)

    group_stack = np.vstack(subject_averages)
    group_mean = np.mean(group_stack, axis=0) # Shape: (num_rois,)
    print(f"Computed Group Matrix Mean over {len(subject_averages)} subjects.")

    # 6. Save Outputs
    output_npy = config['output']['npy_path']
    output_img = config['output']['img_path']
    
    # Ensure output dirs exist
    os.makedirs(os.path.dirname(output_npy), exist_ok=True)
    if output_img:
        os.makedirs(os.path.dirname(output_img), exist_ok=True)

    np.save(output_npy, group_mean)
    print(f"Saved results to {output_npy}")

    # 7. Visualization
    if output_img:
        print(f"Generating brain map at {output_img}...")
        try:
            cmap = mcolors.LinearSegmentedColormap.from_list(
                "green_yellow_red", ["#2ca25f", "#ffffbf", "#d73027"]
            )
            
            fig = None
            if os.environ.get("DISPLAY") is None:
                print("Using Nilearn fallback (headless).")
                from ..visualization.utils_nilearn_brain import nilearn_view
                fig = nilearn_view(
                    current_nodestrength=group_mean,
                    cmap='RdBu_r',
                    title=f"Group Mean - {metric}"
                )
            else:
                fig = normal_view(
                    current_nodestrength=group_mean,
                    edges=True,
                    cmap=cmap,
                    q_thresh=0.0,
                    center_cbar=True,
                    alpha_graymap=0.99,
                    xlabel=r"$\langle s_i \rangle$"
                )
            
            if fig:
                fig.savefig(output_img, dpi=300, bbox_inches="tight")
                print(f"Saved image to {output_img}")
                plt.close(fig)
        except Exception as e:
            print(f"Warning: Visualization failed: {e}")

if __name__ == "__main__":
    main()
