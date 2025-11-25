import numpy as np
import networkx as nx
import pickle as pk
import os

def load_scaffold_singletime(directory, single_time, hom_group=1):
    path = os.path.join(directory, f"generators__{single_time}.pck")
    with open(path, "rb") as f:
        gen = pk.load(f)

    G = nx.Graph()

    for cycle in gen[hom_group]:
        w = float(cycle.persistence_interval())
        for e in cycle.cycles():
            u, v = int(e[0]), int(e[1])
            if G.has_edge(u, v):
                G[u][v]["weight"] += w
            else:
                G.add_edge(u, v, weight=w)
    return G


def compute_nodal_strength_scaffold(G, num_ROIs=100):
    nodal = np.zeros(num_ROIs)
    for node, strength in G.degree(weight="weight"):
        if isinstance(node, int) and node < num_ROIs:
            nodal[node] = strength
    return nodal


def load_single_frame_scaffold(directory, frame, num_ROIs):
    G = load_scaffold_singletime(directory, frame)
    return compute_nodal_strength_scaffold(G, num_ROIs=num_ROIs)
