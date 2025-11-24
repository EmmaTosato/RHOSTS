import os
import numpy as np
import nibabel as nib
from scipy.stats import zscore


def compute_roi_timeseries(fmri_data, atlas_data, n_rois):
    """
    Compute ROI-averaged time series from 4D fMRI data and a 3D atlas.

    Parameters
    ----------
    fmri_data : np.ndarray
        4D array of shape (X, Y, Z, T) with fMRI data.
    atlas_data : np.ndarray
        3D array of shape (X, Y, Z) with integer ROI labels in [1..n_rois].
    n_rois : int
        Number of ROIs.

    Returns
    -------
    ts : np.ndarray
        2D array of shape (T, n_rois) with ROI-averaged time series.
        Each column is the time series of one ROI.
    """

    # Number of timepoints
    T = fmri_data.shape[3]

    # Initialize (T, n_rois)
    ts = np.zeros((T, n_rois), dtype=np.float32)

    # Loop over ROIs
    for roi in range(1, n_rois + 1):
        # 1. Create the mask for the current ROI
        mask = (atlas_data == roi)  # (X, Y, Z) boolean

        # 2. If there are no voxels for this ROI, skip
        if not np.any(mask):
            continue

        # 3. Select fMRI voxels belonging to this ROI → (n_voxels, T)
        fmri_voxels = fmri_data[mask, :]

        # 4. Average across voxels to get a single time series → (T,)
        roi_ts = fmri_voxels.mean(axis=0)

        # 5. Store ROI time series in the correct column (roi - 1)
        ts[:, roi - 1] = roi_ts

    return ts


def main():
    # Subject IDs
    ids = ["134829", "393247", "745555", "905147", "943862"]

    # Paths
    base = "/data/etosato/RHOSTS/lorenzo_data/HCP_rsfMRI"                       # folder with .nii.gz files
    atlas_path = "/Preprocessing/cortex_100.nii.gz"  # 3D atlas
    n_rois = 100

    # Output directory for ROI time series
    output_dir = "/Input/lorenzo_data/ts_txt"
    os.makedirs(output_dir, exist_ok=True)

    # Load atlas once
    atlas = nib.load(atlas_path).get_fdata()
    print(f"Atlas shape: {atlas.shape}")

    # Loop over subjects
    for s_id in ids:
        fmri_path = os.path.join(base, f"{s_id}.nii.gz")
        print(f"Processing subject {s_id} from {fmri_path}")

        fmri_data = nib.load(fmri_path).get_fdata()  # (X, Y, Z, T)
        print(f"  fMRI shape: {fmri_data.shape}")

        # Extract ROI-averaged time series: (T, n_rois)
        ts = compute_roi_timeseries(fmri_data, atlas, n_rois)

        # Z-score per ROI (column-wise: time dimension = axis 0)
        ts_z = zscore(ts, axis=0, nan_policy="omit")

        # Save as txt: T rows, n_rois columns
        out_path = os.path.join(output_dir, f"{s_id}_ts_zscore.txt")
        np.savetxt(out_path, ts_z, fmt="%.6f")
        print(f"  Saved: {out_path} with shape {ts_z.shape}")

    print("Done.")


if __name__ == "__main__":
    main()
