#!/usr/bin/env python3
"""
Batch generate brain map images from all .npy files in a directory.

Usage:
    python batch_generate_images.py <npy_dir> <output_dir> [mode]
    
Example:
    python batch_generate_images.py Output/lorenzo_data/node_strengths/dv Output/lorenzo_data/images/dv
"""

import sys
import os
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')

# Add project root to path
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
sys.path.insert(0, repo_root)

from src.higher_order.visualization.utils_neuromaps_brain import normal_view


def batch_generate_images(npy_dir, output_dir, cmap='green_yellow_red'):
    """
    Generate images for all .npy files in a directory.
    
    Parameters
    ----------
    npy_dir : str
        Directory containing .npy files
    output_dir : str
        Directory to save .png images
    cmap : str
        Colormap to use
    """
    npy_files = list(Path(npy_dir).glob("*.npy"))
    
    if not npy_files:
        print(f"No .npy files found in {npy_dir}")
        return
    
    print(f"Found {len(npy_files)} .npy files")
    os.makedirs(output_dir, exist_ok=True)
    
    for i, npy_path in enumerate(npy_files, 1):
        print(f"\n[{i}/{len(npy_files)}] Processing {npy_path.name}...")
        
        try:
            # Load data
            nodal_strength = np.load(npy_path)
            
            # Generate figure
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
            
            # Save image
            output_path = Path(output_dir) / npy_path.name.replace('.npy', '.png')
            fig.savefig(output_path, dpi=150, bbox_inches='tight')
            print(f"  ✓ Saved to {output_path}")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print(f"\n✅ Completed! Images saved to {output_dir}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    
    npy_directory = sys.argv[1]
    output_directory = sys.argv[2]
    colormap = sys.argv[3] if len(sys.argv) > 3 else 'green_yellow_red'
    
    if not os.path.exists(npy_directory):
        print(f"Error: Directory not found: {npy_directory}")
        sys.exit(1)
    
    batch_generate_images(npy_directory, output_directory, cmap=colormap)
