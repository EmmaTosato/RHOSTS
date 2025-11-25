import numpy as np
import h5py

def compute_nodal_strength_dv(triangle_data, num_ROIs=100):
    edge_weights = {}

    # Per ogni triangolo violante
    for row in triangle_data:
        # i due vertici che definiscono l’arco
        i, j = int(row[0]), int(row[1])
        # la somma dei pesi dei triangoli (i,j,k) che includono quell’arco
        sum_w = row[2]
        # quanti triangoli includono quell’arco
        count = row[3]
        # considera lo stesso arco (i,j) = (j,i)
        edge = tuple(sorted((i, j)))
        if count > 0:
            # media dei pesi dei triangoli che contengono (i,j)
            w_ij = sum_w / count
            # aggiungo l'arco al dizionario (ridondante)
            if edge not in edge_weights:
                edge_weights[edge] = w_ij

    # Inizializza la forza nodale per tutti i nodi
    nodal_strength = np.zeros(num_ROIs)

    # Iterazione su ogni arco violante
    for (i, j), w_ij in edge_weights.items():
        # Proietto il peso degli archi sui nodi
        if i < num_ROIs:
            nodal_strength[i] += w_ij
        if j < num_ROIs:
            nodal_strength[j] += w_ij

    return nodal_strength


def load_single_frame_dv(hd5_file, frame, num_ROIs):
    with h5py.File(hd5_file, "r") as f:
        data = f[str(frame)][:]
    return compute_nodal_strength_dv(data, num_ROIs=num_ROIs)
