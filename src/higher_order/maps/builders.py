"""Helper utilities to select frames and aggregate nodal strengths."""

import glob
import os
import warnings

import numpy as np
import h5py


# -----------------------------------------------------------------------------
# FRAME SELECTION LOGIC
# -----------------------------------------------------------------------------
def _list_scaffold_frames(directory):
    """Return sorted frame indices inferred from ``generators__*.pck`` files."""
    pattern = os.path.join(directory, "generators__*.pck")
    frames = []
    for path in glob.glob(pattern):
        name = os.path.basename(path)
        try:
            frame_str = name.split("__", 1)[1].split(".pck", 1)[0]
            frames.append(int(frame_str))
        except (IndexError, ValueError):
            warnings.warn(
                f"Ignoring scaffold file with unexpected name: {name}",
                RuntimeWarning,
                stacklevel=2,
            )
    return sorted(frames)


def select_frames(
    hd5_files,
    scenario,
    frame=None,
    percent=0.15,
    sorted_output_txt=None,
    value_col=5,
    order="desc",
):
    """
    Select frame indices according to the chosen scenario.

    Parameters
    ----------
    hd5_files : list[str]
        List of HDF5 files (or directories for scaffold mode; when using
        scaffold, frame numbers are inferred from ``generators__*.pck`` files
        present in every directory).
    scenario : {"single_frame", "all_frames", "top_percent"}
        Selection strategy.
    frame : int or None
        Used only when ``scenario == 'single_frame'``.
    percent : float
        Fraction (0–1) of frames to keep when using the "top_percent" strategy.
    sorted_output_txt : str or None
        Text file containing timepoints and a metric (e.g., hyper-coherence or
        complexity) sorted by value.
    value_col : int
        Column index for the metric in ``sorted_output_txt``.
        Examples:
        - 5 for hyper-coherence
        - 1 for complexity
    order : {"desc", "asc"}
        "desc" → take the highest values (top percent)
        "asc"  → take the lowest values (bottom percent)

    Returns
    -------
    list[int]
        Selected frame indices.
    """

    if percent <= 0 or percent > 1:
        raise ValueError("percent must be in the interval (0, 1].")

    # case 1 — single frame
    if scenario == "single_frame":
        if frame is None:
            raise ValueError("frame required for scenario='single_frame'")
        return [frame]

    # case 2 — all frames (used in the DV pipeline)
    # We first attempt to open the first input as an HDF5 file (DV mode); if
    # that fails, we are in scaffold mode and need to infer frames from
    # ``generators__*.pck`` files present in every subject directory.
    try:
        with h5py.File(hd5_files[0], "r") as f:
            all_frames = sorted(map(int, f.keys()))
    except (OSError, IsADirectoryError):
        # scaffold inputs are directories, so infer frames from the generator pickles
        per_directory_frames = [_list_scaffold_frames(d) for d in hd5_files]
        if scenario == "all_frames":
            if not all(per_directory_frames):
                raise RuntimeError(
                    "Cannot infer frames for 'all_frames': no generators__*.pck files found."
                )
            common_frames = set(per_directory_frames[0])
            for frames in per_directory_frames[1:]:
                common_frames &= set(frames)
            if not common_frames:
                raise RuntimeError(
                    "Cannot infer frames for 'all_frames': scaffold directories do not share common frames."
                )
            all_frames = sorted(common_frames)
        else:
            all_frames = None

    if scenario == "all_frames":
        if all_frames is None:
            raise RuntimeError("Cannot infer frames for 'all_frames' from scaffold folders.")
        return all_frames

    # case 3 — top/bottom percentage of frames
    if scenario == "top_percent":
        if sorted_output_txt is None:
            raise ValueError("sorted_output_txt required for scenario='top_percent'")

        if not os.path.exists(sorted_output_txt):
            raise FileNotFoundError(
                f"sorted_output_txt not found: {sorted_output_txt}"
            )

        results = np.loadtxt(sorted_output_txt)
        results = np.atleast_2d(results)
        if results.ndim != 2 or results.shape[1] <= value_col:
            raise ValueError(
                f"sorted_output_txt must have at least {value_col + 1} columns; got shape {results.shape}."
            )
        timepoints = results[:, 0].astype(int)
        values = results[:, value_col]

        n_top = int(np.ceil(len(timepoints) * percent))

        if order == "desc":  # top percentage (highest values)
            idx = np.argsort(values)[-n_top:]
        elif order == "asc":  # bottom percentage (lowest values)
            idx = np.argsort(values)[:n_top]
        else:
            raise ValueError(f"Unknown order: {order!r}, use 'asc' or 'desc'.")

        return timepoints[idx].tolist()

    raise ValueError(f"Unknown scenario: {scenario!r}")


# -----------------------------------------------------------------------------
# AGGREGATION LOGIC (comune a DV e SCAFFOLD)
# -----------------------------------------------------------------------------

def aggregate_frames(hd5_files, frames, loader_fn, num_ROIs):
    """
    Aggregate nodal strength across subjects and frames.

    Parameters
    ----------
    hd5_files : list[str]
        Paths to hd5 files (DV pipeline) or scaffold directories (H1 pipeline).
    frames : list[int]
        Selected frame indices.
    loader_fn : callable
        Function that loads a single frame and returns a nodal strength vector:
        ``loader_fn(hd5_or_dir, frame, num_ROIs) -> np.ndarray(num_ROIs,)``
    num_ROIs : int
        Number of brain regions expected in the nodal vector.

    Returns
    -------
    np.ndarray(num_ROIs,)
        Mean nodal strength across all valid subjects and frames.
    """

    total = np.zeros(num_ROIs, dtype=float)
    count = 0  # number of successfully processed subject/frame pairs

    for hd5_or_directory in hd5_files:
        for frame in frames:
            try:
                strength = np.asarray(loader_fn(hd5_or_directory, frame, num_ROIs), dtype=float)
            except Exception as exc:  # pragma: no cover - defensive logging
                warnings.warn(
                    f"Skipping subject={hd5_or_directory}, frame={frame}: {exc}",
                    RuntimeWarning,
                    stacklevel=2,
                )
                continue

            if strength.shape[0] != num_ROIs:
                warnings.warn(
                    f"Skipping subject={hd5_or_directory}, frame={frame}: expected length {num_ROIs}, got {strength.shape[0]}",
                    RuntimeWarning,
                    stacklevel=2,
                )
                continue

            # Accumulate the nodal strength vector and track the number of samples
            total += strength
            count += 1

    if count == 0:
        raise RuntimeError("No valid nodal strength vectors computed; check inputs and frames.")

    return total / count
