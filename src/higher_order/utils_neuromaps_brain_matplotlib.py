"""
Alternative brain visualization using nilearn (matplotlib-based, no VTK required).
This version works in truly headless environments without xvfb.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from nilearn import datasets, plotting
from brainspace.datasets import load_parcellation


def matplotlib_brain_view(nodal_strength, output_path, cmap='RdYlGn_r', 
                          parcellation=100, vmin=None, vmax=None):
    """
    Generate brain map using nilearn (matplotlib-based, no VTK).
    
    Parameters
    ----------
    nodal_strength : np.ndarray
        Vector of nodal strength values (size 100 for parcellation=100)
    output_path : str
        Path to save output image
    cmap : str
        Matplotlib colormap name
    parcellation : int
        Parcellation resolution (100, 200, 400)
    vmin, vmax : float, optional
        Color range limits
    """
    
    # Load fsaverage surface
    fsaverage = datasets.fetch_surf_fsaverage('fsaverage5')
    
    # Load parcellation
    lh_parc, rh_parc = load_parcellation('schaefer', scale=parcellation)
    
    # Map values to surface vertices
    lh_data = np.zeros(len(lh_parc))
    rh_data = np.zeros(len(rh_parc))
    
    for idx, label in enumerate(lh_parc):
        if label != 0:
            lh_data[idx] = nodal_strength[label - 1]
    
    for idx, label in enumerate(rh_parc):
        if label != 0:
            rh_data[idx] = nodal_strength[label - 1]
    
    # Determine color range
    if vmin is None:
        vmin = np.min(nodal_strength)
    if vmax is None:
        vmax = np.max(nodal_strength)
    
    # Create figure with 4 views (lateral + medial for each hemisphere)
    fig = plt.figure(figsize=(16, 8))
    
    # Left hemisphere - lateral
    ax1 = fig.add_subplot(2, 2, 1, projection='3d')
    plotting.plot_surf_stat_map(
        fsaverage['pial_left'], lh_data,
        hemi='left', view='lateral',
        bg_map=fsaverage['sulc_left'],
        cmap=cmap, vmin=vmin, vmax=vmax,
        colorbar=False, axes=ax1
    )
    ax1.set_title('Left Lateral', fontsize=14)
    
    # Left hemisphere - medial
    ax2 = fig.add_subplot(2, 2, 2, projection='3d')
    plotting.plot_surf_stat_map(
        fsaverage['pial_left'], lh_data,
        hemi='left', view='medial',
        bg_map=fsaverage['sulc_left'],
        cmap=cmap, vmin=vmin, vmax=vmax,
        colorbar=False, axes=ax2
    )
    ax2.set_title('Left Medial', fontsize=14)
    
    # Right hemisphere - lateral
    ax3 = fig.add_subplot(2, 2, 3, projection='3d')
    plotting.plot_surf_stat_map(
        fsaverage['pial_right'], rh_data,
        hemi='right', view='lateral',
        bg_map=fsaverage['sulc_right'],
        cmap=cmap, vmin=vmin, vmax=vmax,
        colorbar=False, axes=ax3
    )
    ax3.set_title('Right Lateral', fontsize=14)
    
    # Right hemisphere - medial
    ax4 = fig.add_subplot(2, 2, 4, projection='3d')
    plotting.plot_surf_stat_map(
        fsaverage['pial_right'], rh_data,
        hemi='right', view='medial',
        bg_map=fsaverage['sulc_right'],
        cmap=cmap, vmin=vmin, vmax=vmax,
        colorbar=True, axes=ax4
    )
    ax4.set_title('Right Medial', fontsize=14)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved matplotlib-based brain map to {output_path}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python utils_neuromaps_brain_matplotlib.py <input.npy> <output.png>")
        sys.exit(1)
    
    npy_path = sys.argv[1]
    output_path = sys.argv[2]
    
    nodal_strength = np.load(npy_path)
    matplotlib_brain_view(nodal_strength, output_path)
