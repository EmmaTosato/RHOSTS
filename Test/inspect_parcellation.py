from brainspace.datasets import load_parcellation
import numpy as np

try:
    lh_parc, rh_parc = load_parcellation('schaefer', scale=100)
    print(f"Left hemisphere shape: {lh_parc.shape}")
    print(f"Right hemisphere shape: {rh_parc.shape}")
    print(f"Unique values left: {np.unique(lh_parc)}")
    print(f"Unique values right: {np.unique(rh_parc)}")
except Exception as e:
    print(f"Error: {e}")
