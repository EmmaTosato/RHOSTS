"""Scaffold-based nodal strength helpers."""

import numpy as np
import networkx as nx
import pickle as pk
import os

def load_scaffold_singletime(directory, single_time, hom_group=1):
    """Load a single scaffold graph from disk and construct a weighted NetworkX graph."""
    path = os.path.join(directory, f"generators__{single_time}.pck")

    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Scaffold file not found for frame {single_time}: {path}"
        )

    try:
        with open(path, "rb") as f:
            gen = pk.load(f)
    except (OSError, pk.UnpicklingError, EOFError) as exc:
        raise RuntimeError(f"Failed to load scaffold pickle {path}: {exc}") from exc

    # Graph initialization
    G = nx.Graph()

    # 
    try:
        cycles = gen[hom_group]
    except (KeyError, TypeError) as exc:
        raise RuntimeError(
            f"hom_group={hom_group} missing or malformed in scaffold pickle {path}"
        ) from exc

    # Each persistence cycle corresponds to a collection of edges; the
    # persistence interval is treated as the cycle weight and is added to every
    # edge in that cycle. When multiple cycles traverse the same undirected
    # edge, their weights accumulate, capturing how often an edge participates
    # in the scaffold across generators.
    for cycle in cycles:
        w = float(cycle.persistence_interval())
        for e in cycle.cycles():
            u, v = int(e[0]), int(e[1])
            if G.has_edge(u, v):
                G[u][v]["weight"] += w
            else:
                G.add_edge(u, v, weight=w)
    return G


def compute_nodal_strength_scaffold(G, num_ROIs=100):
    """Convert a scaffold graph into a nodal strength vector."""
    # Project weighted edges to node-level strength using NetworkX degree with
    # the edge weights accumulated above.
    nodal = np.zeros(num_ROIs)
    for node, strength in G.degree(weight="weight"):
        if isinstance(node, int) and node < num_ROIs:
            nodal[node] = strength
    return nodal


def load_single_frame_scaffold(directory, frame, num_ROIs):
    """Load and convert a single scaffold frame into nodal strengths."""
    G = load_scaffold_singletime(directory, frame)
    return compute_nodal_strength_scaffold(G, num_ROIs=num_ROIs)
