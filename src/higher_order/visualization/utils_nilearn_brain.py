import numpy as np
import matplotlib.pyplot as plt
from nilearn import plotting, datasets
from brainspace.datasets import load_parcellation

def nilearn_view(current_nodestrength, parcellation='schaefer', scale=100, 
                 cmap='RdBu_r', title=None):
    """
    Generate a surface plot using nilearn (headless compatible).
    """
    # Load parcellation
    # Brainspace loads 32k vertex parcellations (fsaverage)
    lh_parc, rh_parc = load_parcellation(parcellation, scale=scale)
    
    # Initialize data arrays
    lh_data = np.zeros(lh_parc.shape)
    rh_data = np.zeros(rh_parc.shape)
    
    # Map node values to vertices
    n_rois = len(current_nodestrength)
    n_left = n_rois // 2
    
    # Fill Left Hemisphere
    for i in range(1, n_left + 1):
        mask = (lh_parc == i)
        if np.any(mask):
            lh_data[mask] = current_nodestrength[i-1]
            
    # Fill Right Hemisphere
    # Check if we have enough values for RH
    for i in range(1, len(np.unique(rh_parc))): 
        mask = (rh_parc == i)
        if np.any(mask):
            val_idx = n_left + i - 1
            if val_idx < n_rois:
                rh_data[mask] = current_nodestrength[val_idx]

    # Fetch fsaverage surface
    # IMPORTANT: Must specify mesh='fsaverage' to get high-res (163k vertices? Wait, brainspace says 32k)
    # Brainspace 32k (density='32k') usually corresponds to fsLR 32k (HCP).
    # But nilearn fetch_surf_fsaverage returns FreeSurfer fsaverage meshes.
    # fsaverage5 = 10k, fsaverage6 = 40k, fsaverage = 163k.
    # 
    # If load_parcellation returns ~32k vertices, it's likely fsLR 32k.
    # Nilearn plotting usually expects fsaverage (FreeSurfer).
    # Vertex mismatch is likely inevitable if we mix fsLR parcellation with fsaverage mesh directly.
    #
    # However, let's try to fetch fsaverage and see if we can use it.
    # If mismatched, we might need to use a specific surface file or resample?
    # BUT, the user's code uses `fetch_fslr` and `load_parcellation` together, implying they match (fsLR 32k).
    # nilearn.plotting.plot_surf accepts any mesh file (gifti/gii).
    # So we should fetch fsLR 32k using neuromaps (like the original code) or confirm vertex count.
    
    # Let's try to use the same surface source as the original code if possible, or compatible one.
    # The original code used: surfaces = fetch_fslr(density='32k') -> lh, rh
    # These are .gii files. Nilearn can plot .gii files!
    
    from neuromaps.datasets import fetch_fslr
    surfaces = fetch_fslr(density='32k')
    lh_mesh, rh_mesh = surfaces['inflated']
    lh_sulc, rh_sulc = surfaces['sulc']
    
    # Create figure
    fig = plt.figure(figsize=(12, 6))
    
    # Plot Lateral views
    # Note: plot_surf_roi maps ROI values to surface. 
    # We constructed vertex-wise data (lh_data) already. 
    # So we should use plot_surf (stat_map) instead of plot_surf_roi (which takes atlas + indices)?
    # Actually plot_surf takes a stat_map which is (n_vertices,). lh_data is exactly that.
    
    plotting.plot_surf(lh_mesh, surf_map=lh_data,
                          hemi='left', view='lateral',
                          bg_map=lh_sulc, bg_on_data=True,
                          darkness=.5, cmap=cmap, colorbar=True,
                          figure=fig, title=title)
                          
    return fig
