#!/usr/bin/env python3
"""
Generate brain map images locally from .npy files.

Usage:
    python generate_images_local.py <input.npy> <output.png>
    
Example:
    python generate_images_local.py Output/lorenzo_data/node_strengths/dv/134829_all_frames.npy Output/lorenzo_data/images/dv/134829_all_frames.png
"""

import sys
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend

# Add project root to path
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
sys.path.insert(0, repo_root)

from src.higher_order.utils_neuromaps_brain import normal_view


def generate_image(npy_path, output_path, cmap='green_yellow_red'):
    """
    Generate brain map image from .npy file.
    
    Parameters
    ----------
    npy_path : str
        Path to input .npy file containing nodal strength values
    output_path : str
        Path to save output .png image
    cmap : str
        Colormap to use ('green_yellow_red', 'RdBu_r', 'custom')
    """
    print(f"Loading {npy_path}...")
    nodal_strength = np.load(npy_path)
    
    print(f"Generating brain map (cmap={cmap})...")
    fig = normal_view(
        nodal_strength,
        cmap=cmap,
        edges=False,
        surftype='inflated',
        xlabel='Nodal Strength',
        q_thresh=0.0,
        brightness=0.7,
        exp_form=True,
        parcellation=100
    )
    
    # Create output directory if needed
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    print(f"Saving to {output_path}...")
    fig.savefig(output_path, dpi=150, bbox_inches='tight')
    print("Done!")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    
    npy_file = sys.argv[1]
    output_file = sys.argv[2]
    
    if not os.path.exists(npy_file):
        print(f"Error: Input file not found: {npy_file}")
        sys.exit(1)
    
    # Optional: colormap argument
    cmap = sys.argv[3] if len(sys.argv) > 3 else 'green_yellow_red'
    
    generate_image(npy_file, output_file, cmap=cmap)
