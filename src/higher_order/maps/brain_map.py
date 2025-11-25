from .builders import select_frames, aggregate_frames
from ..nodal_strenght.nodal_strenght_dv import load_single_frame_dv
from ..nodal_strenght.nodal_strength_scaffold import load_single_frame_scaffold

def compute_brainmap_dv(
    hd5_paths,
    scenario,
    frame=None,
    percent=0.15,
    sorted_output_txt=None,
    num_ROIs=100,
    metric="hyper",      # "hyper" or "complexity"
    direction="high",    # "high" (top) or "low" (bottom)
):
    # Mappa metric -> colonna del txt
    if metric == "hyper":
        value_col = 5
    elif metric == "complexity":
        value_col = 1
    else:
        raise ValueError(f"Unknown metric: {metric!r}")

    # Mappa direction -> ordine
    if direction == "high":
        order = "desc"
    elif direction == "low":
        order = "asc"
    else:
        raise ValueError(f"Unknown direction: {direction!r}")

    frames = select_frames(
        hd5_files=hd5_paths,
        scenario=scenario,
        frame=frame,
        percent=percent,
        sorted_output_txt=sorted_output_txt,
        value_col=value_col,
        order=order,
    )

    nodal_strength = aggregate_frames(
        hd5_files=hd5_paths,
        frames=frames,
        loader_fn=load_single_frame_dv,
        num_ROIs=num_ROIs,
    )
    return nodal_strength


def compute_brainmap_scaffold(
    scaffold_directories,
    scenario,
    frame=None,
    percent=0.15,
    sorted_output_txt=None,
    num_ROIs=100,
    metric="complexity",   # default più sensato per scaffold
    direction="low",       # bottom 15% di default
):
    if metric == "hyper":
        value_col = 5
    elif metric == "complexity":
        value_col = 1
    else:
        raise ValueError(f"Unknown metric: {metric!r}")

    if direction == "high":
        order = "desc"
    elif direction == "low":
        order = "asc"
    else:
        raise ValueError(f"Unknown direction: {direction!r}")

    frames = select_frames(
        hd5_files=scaffold_directories,
        scenario=scenario,
        frame=frame,
        percent=percent,
        sorted_output_txt=sorted_output_txt,
        value_col=value_col,
        order=order,
    )

    nodal_strength = aggregate_frames(
        hd5_files=scaffold_directories,
        frames=frames,
        loader_fn=load_single_frame_scaffold,
        num_ROIs=num_ROIs,
    )
    return nodal_strength
