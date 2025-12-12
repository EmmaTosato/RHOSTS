from brainspace.datasets import load_parcellation
from nilearn import datasets
import numpy as np

lh_parc, rh_parc = load_parcellation('schaefer', scale=100)
print(f"Parcellation shape: LH={lh_parc.shape}, RH={rh_parc.shape}")

fsaverage = datasets.fetch_surf_fsaverage() # Defaults to fsaverage5?
infl_left = datasets.load_surf_mesh(fsaverage.infl_left)
print(f"Nilearn fsaverage surface vertices: LH={infl_left.n_vertices}")

# Try loading fsLR meant for neuromaps if possible, or standard fsaverage5 parcellation
