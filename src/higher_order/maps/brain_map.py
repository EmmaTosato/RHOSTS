from ..utils.frame_selection import select_frames
from ..utils.aggregation import aggregate_frames
from ..core.nodal_strength_dv import load_single_frame_dv

def compute_brainmap_dv(
    hd5_paths,
    scenario,
    frame=None,
    percent=0.15,
    sorted_output_txt=None,
    num_ROIs=100,
):
    frames = select_frames(hd5_paths, scenario, frame, percent, sorted_output_txt)
    nodal_strength = aggregate_frames(
        hd5_paths, frames, loader_fn=load_single_frame_dv, num_ROIs=num_ROIs
    )
    return nodal_strength

from ..utils.frame_selection import select_frames
from ..utils.aggregation import aggregate_frames
from ..core.nodal_strength_scaffold import load_single_frame_scaffold

def compute_brainmap_scaffold(
    scaffold_directories,
    scenario,
    frame=None,
    percent=0.15,
    sorted_output_txt=None,
    num_ROIs=100,
):
    frames = select_frames(scaffold_directories, scenario, frame, percent, sorted_output_txt)
    nodal_strength = aggregate_frames(
        scaffold_directories, frames, loader_fn=load_single_frame_scaffold, num_ROIs=num_ROIs
    )
    return nodal_strength
