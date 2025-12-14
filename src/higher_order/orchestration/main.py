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
    # 1. Only CLI argument: path to JSON config. Everything else is in the config file.
    parser = argparse.ArgumentParser(description="Run RHOSTS Higher-Order Analysis")
    parser.add_argument("--config", required=True, help="Path to JSON configuration file")
    args = parser.parse_args()

    # 2. Load JSON config
    config = load_config(args.config)
    print(f"Loaded configuration from {args.config}")

    # Required parameters
    mode = config['mode']
    scenario = config['scenario']
    subjects_list_file = config['subjects_list_file']
    # Optional parameters with defaults
    num_rois = config.get('num_rois', 116)
    metric = config.get('metric', 'coherence')
    percent = config.get('percent', 0.15)
    
    # Metric -> column/order mapping
    if metric == 'coherence':
        value_col = 5
        order = 'desc'
    elif metric == 'complexity':
        value_col = 1
        order = 'asc'
    else:
        value_col = config.get('custom_metric_col', 5)
        order = config.get('custom_order', 'desc')

    # 3. Load subject list
    subjects = get_subject_list(subjects_list_file)
    print(f"Found {len(subjects)} subjects to process.")

    # 4. Processing Loop
    subject_averages = []
    print(f"Processing: {len(subjects)} subjects, mode={mode}, scenario={scenario}")

    for subj_idx, subj_id in enumerate(subjects, 1):
        try:
            # Resolve paths based on mode
            if mode == 'dv':
                data_path = config['data_path_pattern_dv'].format(subject=subj_id)
                loader_fn = load_single_frame_dv
            else:  
                data_path = config['data_path_pattern_scaffold'].format(subject=subj_id)
                loader_fn = load_single_frame_scaffold
            
            indicators_path = config['indicators_path_pattern'].format(subject=subj_id)

            # Select frames for this subject
            frames = select_frames(
                data_sources=[data_path], 
                scenario=scenario,
                frame=config.get('frame'),
                percent=percent,
                sorted_output_txt=indicators_path,
                value_col=value_col,
                order=order
            )
            
            if not frames:
                print(f"  [{subj_idx}/{len(subjects)}] {subj_id}: No frames selected. Skipping.")
                continue

            # Average over Timepoints 
            time_accum = np.zeros(num_rois, dtype=float)
            valid_frames = 0
            
            for frame in frames:
                try:
                    nodal = loader_fn(data_path, frame, num_rois)
                    time_accum += nodal
                    valid_frames += 1
                except Exception as e:
                    pass  # Silently skip errors
            
            if valid_frames > 0:
                subject_avg = time_accum / valid_frames
                subject_averages.append(subject_avg)
                print(f"  [{subj_idx}/{len(subjects)}] {subj_id}: {valid_frames} frames processed")
            else:
                print(f"  [{subj_idx}/{len(subjects)}] {subj_id}: No valid frames")

        except Exception as e:
            print(f"  [{subj_idx}/{len(subjects)}] {subj_id}: ERROR - {e}")
            continue

    # 5. Average over Subjects
    if not subject_averages:
        print("ERROR: No subjects successfully processed.")
        sys.exit(1)

    group_stack = np.vstack(subject_averages)
    group_mean = np.mean(group_stack, axis=0)
    print(f"Result: shape={group_mean.shape}, range=[{group_mean.min():.2f}, {group_mean.max():.2f}]")

    # 6. Save Output
    output_dir = config.get('output_dir', '/data/etosato/RHOSTS/Output/lorenzo_data/node_strengths')
    output_subdir = os.path.join(output_dir, mode)
    os.makedirs(output_subdir, exist_ok=True)
    
    # Auto-generate filename based on config
    n_subjects = len(subject_averages)
    if scenario == 'all_frames':
        filename = f"{mode}_all_frames_{n_subjects}subj.npy"
    elif scenario == 'top_percent':
        pct = int(percent * 100)
        filename = f"{mode}_top{pct}pct_{metric}_{n_subjects}subj.npy"
    elif scenario == 'single_frame':
        frame_id = config.get('frame', 0)
        filename = f"{mode}_frame{frame_id}_{n_subjects}subj.npy"
    else:
        filename = f"{mode}_{scenario}_{n_subjects}subj.npy"
    
    output_path = os.path.join(output_subdir, filename)
    np.save(output_path, group_mean)
    print(f"Saved results to {output_path}")
    print("Transfer .npy to local machine for visualization.")

if __name__ == "__main__":
    main()
