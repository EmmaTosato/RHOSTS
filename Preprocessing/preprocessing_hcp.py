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
    base = "/data/etosato/RHOSTS/Preprocessing/HCP_rsfMRI"
    cortex_atlas_path = "/data/etosato/RHOSTS/Preprocessing/atlases/cortex_100.nii.gz"
    sub_atlas_path = "/data/etosato/RHOSTS/Preprocessing/atlases/subcortex_16.nii"

    # ROIs for the cortical atlas and the subcortical one
    n_rois_ctx = 100
    n_rois_sub = 16

    # Output directory for ROI time series
    output_dir = "/data/etosato/RHOSTS/Input/lorenzo_data/cortical_subcortical"
    os.makedirs(output_dir, exist_ok=True)

    # Load atlas once
    cortex_atlas = nib.load(cortex_atlas_path).get_fdata().astype(int)
    sub_atlas    = nib.load(sub_atlas_path).get_fdata().astype(int)

    print("Cortical atlas shape:    ", cortex_atlas.shape)
    print("Subcortical atlas shape: ", sub_atlas.shape)

    # Loop over subjects
    for s_id in ids:
        fmri_path = os.path.join(base, f"{s_id}.nii.gz")
        print(f"\nProcessing subject {s_id}:\n  {fmri_path}")

        fmri_data = nib.load(fmri_path).get_fdata()
        print("  fMRI shape:", fmri_data.shape)

        # Extract cortex time series (T × 100)
        ts_ctx = compute_roi_timeseries(fmri_data, cortex_atlas, n_rois_ctx)
        # Extract subcortical time series (T × 16)
        ts_sub = compute_roi_timeseries(fmri_data, sub_atlas, n_rois_sub)
        
        # Concatenate → (T × 116)
        ts_all = np.concatenate([ts_ctx, ts_sub], axis=1)

        # Z-score per ROI (column-wise: time dimension = axis 0)
        ts_all_z = zscore(ts_all, axis=0, nan_policy="omit")

        # Save as txt: T rows, n_rois columns
        out_path = os.path.join(output_dir, f"{s_id}_ts_zscore_ctx_sub.txt")
        np.savetxt(out_path, ts_all_z, fmt="%.6f")
        print(f"  Output saved in: {out_path}")
        print(f"  Final shape: {ts_all_z.shape}")

    print("Done.")


if __name__ == "__main__":
    main()
