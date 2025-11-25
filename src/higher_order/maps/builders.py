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
    Seleziona la lista di frame secondo lo scenario.

    Parameters
    ----------
    hd5_files : list[str]
        Lista di file HDF5 (o directory nel caso scaffold; nel caso scaffold i
        frame vengono ricavati dai file ``generators__*.pck`` comuni a tutte le
        directory).
    scenario : {"single_frame", "all_frames", "top_percent"}
        Strategia di selezione.
    frame : int or None
        Usato se scenario == "single_frame".
    percent : float
        Percentuale (0–1) dei frame da selezionare nel caso "top_percent".
    sorted_output_txt : str or None
        File txt con timepoints e una metrica (es. hyper-coherence, complexity).
    value_col : int
        Indice della colonna della metrica.
        Esempi:
        - 5 per hyper-coherence
        - 1 per complexity
    order : {"desc", "asc"}
        "desc" → top percento (valori alti)
        "asc"  → bottom percento (valori bassi)

    Returns
    -------
    list[int] : lista di frame selezionati.
    """

    if percent <= 0 or percent > 1:
        raise ValueError("percent must be in the interval (0, 1].")

    # caso 1 — singolo frame
    if scenario == "single_frame":
        if frame is None:
            raise ValueError("frame required for scenario='single_frame'")
        return [frame]

    # caso 2 — tutti i frame (solo per pipeline DV)
    try:
        with h5py.File(hd5_files[0], "r") as f:
            all_frames = sorted(map(int, f.keys()))
    except (OSError, IsADirectoryError):
        # nel caso scaffold, hd5_files[0] non è un hd5 → inferiamo dai file pck
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

    # caso 3 — top/bottom percento
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

        if order == "desc":  # top percento (valori più ALTI)
            idx = np.argsort(values)[-n_top:]
        elif order == "asc":  # bottom percento (valori più BASSI)
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
    Aggrega la nodal strength su soggetti × frame.

    Parameters
    ----------
    hd5_files : list[str]
        Path dei file hd5 (pipeline DV) o directory degli scaffold (pipeline H1).
    frames : list[int]
        Frame selezionati.
    loader_fn : callable
        Funzione che carica un singolo frame e ritorna un vettore nodale:
        loader_fn(hd5_or_dir, frame, num_ROIs) -> np.ndarray(num_ROIs,)
    num_ROIs : int
        Numero di regioni.

    Returns
    -------
    np.ndarray(num_ROIs,) : nodal strength media su soggetti × frame.
    """

    total = np.zeros(num_ROIs, dtype=float)
    count = 0

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

            total += strength
            count += 1

    if count == 0:
        raise RuntimeError("No valid nodal strength vectors computed; check inputs and frames.")

    return total / count
