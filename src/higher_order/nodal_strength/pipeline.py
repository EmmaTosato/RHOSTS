"""
High-level orchestration for deriving brain maps from DV or scaffold data.

Questo modulo contiene le funzioni principali che coordinano:
1. La traduzione delle metriche utente (coherence/complexity) in parametri interni
2. La selezione dei frame temporali da analyze
3. L'aggregazione attraverso soggetti e frame
4. Il calcolo finale del nodal strength

Funzioni principali:
- compute_brainmap_dv(): pipeline per modalità Dynamic Violations
- compute_brainmap_scaffold(): pipeline per modalità Homological Scaffold
"""

# Import utilities condivise
from .utils import select_frames, aggregate_frames  # Frame selection e aggregazione
from .loaders_dv import load_single_frame_dv  # Caricatore per file HDF5 DV
from .loaders_scaffold import load_single_frame_scaffold  # Caricatore per directory scaffold


def compute_brainmap_dv(
    hd5_paths,  # Lista di path file HDF5 (uno per soggetto)
    scenario,  # Strategia selezione frame: "single_frame", "all_frames", "top_percent"
    frame=None,  # Frame specifico (usato solo se scenario="single_frame")
    percent=0.15,  # Percentuale frame da selezionare (default 15%)
    sorted_output_txt=None,  # Path al file con indicatori ordinati
    num_ROIs=100,  # Numero di ROI nel dataset
    metric="hyper",  # Metrica interna: "hyper" (coherence) o "complexity"
    direction="high",  # Direzione: "high" (top values) o "low" (bottom values)
):
    """
    Compute nodal strength for dynamic violation (DV) HDF5 inputs.
    
    Questa funzione orchestra il calcolo del nodal strength dai triangoli violanti:
    1. Traduce la metrica in colonna del file sorted_output_txt
    2. Seleziona quali frame temporali analizzare
    3. Carica e aggrega nodal strength attraverso soggetti e frame
    
    Args:
        hd5_paths: Lista di file .hdf5 contenenti edge_weights da violating triangles
        scenario: Come selezionare i frame ("single_frame", "all_frames", "top_percent")
        frame: Quale frame analizzare (solo per scenario="single_frame")
        percent: Percentuale di frame da selezionare (solo per scenario="top_percent")
        sorted_output_txt: File con indicatori ordinati (colonne: time, complexity, ..., hyper, ...)
        num_ROIs: Numero di ROI attese nel dataset
        metric: "hyper" per hyper-coherence, "complexity" per hyper-complexity
        direction: "high" per top percentile, "low" per bottom percentile
        
    Returns:
        nodal_strength: Vettore numpy shape (num_ROIs,) con nodal strength mediato
    """
    
    # STEP 1: Traduzione metrica -> colonna file
    # Il file sorted_output_txt ha diverse colonne con indicatori.
    # Dobbiamo sapere QUALE colonna leggere per ordinare i frame.
    #
    # Struttura tipica del file sorted_output_txt:
    # Colonna 0: timepoint (frame index)
    # Colonna 1: hyper-complexity
    # Colonna 2: complexity FC (fully coherent)
    # Colonna 3: complexity CT (coherent transition)
    # Colonna 4: complexity FD (fully decoherent)
    # Colonna 5: hyper-coherence
    # Colonna 6: average edge violation
    
    if metric == "hyper":
        value_col = 5  # Colonna 5 = hyper-coherence indicator
    elif metric == "complexity":
        value_col = 1  # Colonna 1 = hyper-complexity indicator
    else:
        # Se metrica sconosciuta, solleva errore
        raise ValueError(f"Unknown metric: {metric!r}")

    # STEP 2: Traduzione direzione -> ordine sorting
    # "direction" determina se vogliamo i valori PIÙ ALTI o PIÙ BASSI
    # della metrica selezionata.
    #
    # Esempi:
    # - metric="hyper", direction="high" -> top 15% frame più coerenti
    # - metric="complexity", direction="low" -> bottom 15% frame meno complessi
    
    if direction == "high":
        order = "desc"  # Ordine decrescente -> prendi top values
    elif direction == "low":
        order = "asc"  # Ordine crescente -> prendi bottom values
    else:
        # Se direzione sconosciuta, solleva errore
        raise ValueError(f"Unknown direction: {direction!r}")

    # STEP 3: Selezione frame
    # Chiama select_frames() per determinare QUALI frame temporali analizzare.
    # Questo restituisce una lista di indici, es. [100, 245, 789, ...]
    frames = select_frames(
        hd5_files=hd5_paths,  # Lista file HDF5
        scenario=scenario,  # Strategia selezione
        frame=frame,  # Frame specifico (se applicabile)
        percent=percent,  # Percentuale (se applicabile)
        sorted_output_txt=sorted_output_txt,  # File indicatori
        value_col=value_col,  # Quale colonna usare per ordinare
        order=order,  # Ordine crescente/descrescente
    )

    # STEP 4: Aggregazione
    # Chiama aggregate_frames() per:
    # - Caricare ogni frame selezionato
    # - Calcolare nodal strength per ogni soggetto/frame
    # - Mediare attraverso tutti i soggetti e frame
    nodal_strength = aggregate_frames(
        hd5_files=hd5_paths,  # Lista file HDF5
        frames=frames,  # Lista frame da caricare (output di select_frames)
        loader_fn=load_single_frame_dv,  # Funzione per caricare singolo frame DV
        num_ROIs=num_ROIs,  # Numero ROI attese
    )
    
    # Restituisce vettore nodal strength (num_ROIs,)
    return nodal_strength


def compute_brainmap_scaffold(
    scaffold_directories,  # Lista di directory contenenti generatori scaffold
    scenario,  # Strategia selezione frame
    frame=None,  # Frame specifico (se scenario="single_frame")
    percent=0.15,  # Percentuale frame (default 15%)
    sorted_output_txt=None,  # File con indicatori
    num_ROIs=100,  # Numero ROI
    metric="complexity",  # Default per scaffold: complexity (non hyper)
    direction="low",  # Default per scaffold: low (bottom 15%)
):
    """
    Compute nodal strength using scaffold directories and persistence cycles.
    
    Questa funzione è analoga a compute_brainmap_dv() ma per modalità scaffold.
    
    DIFFERENZE rispetto a DV:
    - Input: directory contenenti file generators__*.pck invece di file .hdf5
    - Default diversi: metric="complexity", direction="low"
      (per scaffold tipicamente si analizzano frame con BASSA complessità,
       che corrispondono a stati più sincronizzati)
    - Loader diverso: load_single_frame_scaffold invece di load_single_frame_dv
    
    La logica di selezione frame e aggregazione è IDENTICA a DV.
    
    Args:
        scaffold_directories: Lista di directory con file generators__*.pck
        scenario: Come selezionare i frame
        frame: Frame specifico (solo se scenario="single_frame")
        percent: Percentuale frame da selezionare
        sorted_output_txt: File con indicatori
        num_ROIs: Numero ROI attese
        metric: Metrica per ordinamento ("hyper" o "complexity")
        direction: Direzione ("high" o "low")
        
    Returns:
        nodal_strength: Vettore numpy shape (num_ROIs,) con nodal strength
    """
    
    # STEP 1: Traduzione metrica -> colonna
    # Identica a compute_brainmap_dv()
    # Il file sorted_output_txt è lo stesso per DV e scaffold
    if metric == "hyper":
        value_col = 5  # Hyper-coherence
    elif metric == "complexity":
        value_col = 1  # Hyper-complexity
    else:
        raise ValueError(f"Unknown metric: {metric!r}")

    # STEP 2: Traduzione direzione -> ordine
    # Identica a compute_brainmap_dv()
    if direction == "high":
        order = "desc"  # Top percentile
    elif direction == "low":
        order = "asc"  # Bottom percentile
    else:
        raise ValueError(f"Unknown direction: {direction!r}")

    # STEP 3: Selezione frame
    # Usa la stessa funzione select_frames()
    # La funzione riconosce automaticamente se gli input sono file HDF5 o directory
    frames = select_frames(
        hd5_files=scaffold_directories,  # Nota: parametro si chiama hd5_files ma accetta anche directory
        scenario=scenario,
        frame=frame,
        percent=percent,
        sorted_output_txt=sorted_output_txt,
        value_col=value_col,
        order=order,
    )

    # STEP 4: Aggregazione
    # Usa la stessa logica ma con loader_fn diverso
    nodal_strength = aggregate_frames(
        hd5_files=scaffold_directories,  # Directory scaffold
        frames=frames,  # Frame selezionati
        loader_fn=load_single_frame_scaffold,  # Loader specifico per scaffold
        num_ROIs=num_ROIs,
    )
    
    return nodal_strength
