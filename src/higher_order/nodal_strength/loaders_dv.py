"""Helpers to load dynamic violation data and compute nodal strength."""

import numpy as np
import h5py

def compute_nodal_strength_dv(triangle_data, num_ROIs=100):
    """Convert violating triangle descriptors into per-node strength estimates."""
    # ``triangle_data`` stores one row per edge (i, j) and encodes how many
    # violating triangles contained that edge and the total weight accumulated
    # across those triangles. Each row is expected to be shaped like:
    #   [i, j, sum_w, count]
    # where ``sum_w`` is the sum of weights for all triangles incident to (i, j)
    # and ``count`` is the number of such triangles.
    edge_weights = {}

    # Iterate over each violating triangle-derived edge descriptor
    for row in triangle_data:
        # vertices that define the edge
        i, j = int(row[0]), int(row[1])
        # sum of the weights of triangles (i, j, k) that include this edge
        sum_w = row[2]
        # how many triangles include this edge
        count = row[3]
        # treat (i, j) as the same edge as (j, i)
        edge = tuple(sorted((i, j)))
        if count > 0:
            # average weight of the triangles that contain (i, j)
            w_ij = sum_w / count
            # store the edge weight once so the nodal projection is applied only
            # to unique undirected edges
            if edge not in edge_weights:
                edge_weights[edge] = w_ij

    # Initialize nodal strength for every node. Nodes not present in the edge
    # list will keep a value of zero.
    nodal_strength = np.zeros(num_ROIs)

    # Accumulate nodal strength from each violating edge
    for (i, j), w_ij in edge_weights.items():
        # Project edge weights onto the connected nodes
        if i < num_ROIs:
            nodal_strength[i] += w_ij
        if j < num_ROIs:
            nodal_strength[j] += w_ij

    return nodal_strength


def load_single_frame_dv(hd5_file, frame, num_ROIs):
    """Load one DV frame from an HDF5 file and compute nodal strength."""
    with h5py.File(hd5_file, "r") as f:
        # DV files expose one dataset per frame, keyed by the frame index as a
        if str(frame) not in f:
            raise KeyError(f"Frame {frame} not found in {hd5_file}")
        data = f[str(frame)][:]

    nodal = compute_nodal_strength_dv(data, num_ROIs=num_ROIs)
    if nodal.shape[0] != num_ROIs:
        raise ValueError(
            f"Computed nodal strength has length {nodal.shape[0]}, expected {num_ROIs} (file={hd5_file}, frame={frame})."
        )
    return nodal
