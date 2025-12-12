import numpy as np
import sys
import os

# Load function from utils (replicated here for simplicity or import if PYTHONPATH set)
def load_normaltxt(path_single_file):
    file_to_open = path_single_file
    data = np.loadtxt(file_to_open)
    return np.transpose(data)

subject = "134829"
filepath = f"/data/etosato/RHOSTS/Input/lorenzo_data/cortical_subcortical/{subject}_ts_zscore_ctx_sub.txt"

print(f"Loading {filepath}...")
data = load_normaltxt(filepath)
print(f"Data shape: {data.shape}") # Should be (n_ROI, T)

timepoints_to_check = [100, 1203, 1219, 1220, 1222, 1500]

print("\n--- Statistics per timepoint ---")
for t in timepoints_to_check:
    if t < data.shape[1]:
        col = data[:, t]
        print(f"t={t}: Min={np.min(col):.4f}, Max={np.max(col):.4f}, Mean={np.mean(col):.4f}, Std={np.std(col):.4f}")
        # Check for zeros or NaNs
        if np.all(col == 0):
            print(f"  [WARNING] All zeros at t={t}")
        if np.isnan(col).any():
            print(f"  [WARNING] NaNs present at t={t}")
    else:
        print(f"t={t}: Out of bounds")

    # Check coherence/signs
    if t < data.shape[1]:
        col = data[:, t]
        pos = np.sum(col > 0)
        neg = np.sum(col < 0)
        print(f"  Signs: {pos} positive, {neg} negative")

