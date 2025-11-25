import numpy as np
import h5py


# -----------------------------------------------------------------------------
# FRAME SELECTION LOGIC
# -----------------------------------------------------------------------------

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
        Lista di file HDF5 (o directory nel caso scaffold; usiamo solo il primo
        per leggere i frame nel caso 'all_frames').
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
        # nel caso scaffold, hd5_files[0] non è un hd5 → non usare HDF5
        all_frames = None

    if scenario == "all_frames":
        if all_frames is None:
            raise RuntimeError("Cannot infer frames for 'all_frames' from scaffold folders.")
        return all_frames

    # caso 3 — top/bottom percento
    if scenario == "top_percent":
        if sorted_output_txt is None:
            raise ValueError("sorted_output_txt required for scenario='top_percent'")

        results = np.loadtxt(sorted_output_txt)
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

    strengths = [
        loader_fn(hd5_or_directory, frame, num_ROIs)
        for hd5_or_directory in hd5_files
        for frame in frames
    ]

    strengths = np.stack(strengths, axis=0)
    return strengths.mean(axis=0)
