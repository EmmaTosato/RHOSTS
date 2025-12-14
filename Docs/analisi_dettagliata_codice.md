# Analisi Dettagliata del Codice - `main.py`

Spiegazione riga per riga del nuovo entry point basato su JSON.

---

## Struttura File

```
src/higher_order/orchestration/main.py
```

---

## Import (Righe 1-14)

```python
import argparse      # Per --config argument
import json          # Per leggere config.json
import os            # Per path e makedirs
import sys           # Per exit()
import numpy as np   # Per array nodal strength
import matplotlib
matplotlib.use('Agg')  # Backend headless (senza GUI)
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
```

---

## Funzioni Helper

### `load_config(config_path)`
Carica e restituisce il dizionario JSON dal file config.

### `get_subject_list(subjects_file)`
Legge il file `subjects.txt` e restituisce lista di ID.
- Ignora righe vuote e commenti (`#`)

---

## Funzione `main()`

### Step 1: Caricamento Configurazione

```python
config = load_config(args.config)
mode = config['mode']           # "dv" o "scaffold"
scenario = config['scenario']   # "single_frame", "all_frames", "top_percent"
num_rois = config.get('num_rois', 116)
```

### Step 2: Lista Soggetti

```python
subjects = get_subject_list(config['subjects_list_file'])
```

Legge da file txt, es:
```
134829
393247
745555
```

### Step 3: Mapping Metrica → Colonna

```python
if metric == 'coherence':
    value_col = 5    # Colonna hyper-coherence
    order = 'desc'   # Valori ALTI (top %)
elif metric == 'complexity':
    value_col = 1    # Colonna hyper-complexity  
    order = 'asc'    # Valori BASSI (bottom %)
```

### Step 4: Loop Soggetti

```python
for subj_id in subjects:
    # Costruisco path usando pattern
    data_path = config['data_path_pattern'].format(subject=subj_id)
    indicators_path = config['indicators_path_pattern'].format(subject=subj_id)
    
    # Seleziono frame
    frames = select_frames(...)
    
    # Media sui TIMEPOINTS
    time_accum = np.zeros(num_rois)
    for frame in frames:
        nodal = loader_fn(data_path, frame, num_rois)
        time_accum += nodal
        valid_frames += 1
    
    subject_avg = time_accum / valid_frames
    subject_averages.append(subject_avg)
```

### Step 5: Media Soggetti

```python
group_stack = np.vstack(subject_averages)  # (N_subjects, 116)
group_mean = np.mean(group_stack, axis=0)  # (116,)
```

### Step 6: Salvataggio

```python
np.save(output_npy, group_mean)
```

### Step 7: Visualizzazione (Opzionale)

Se `output.img_path` è definito:
- Usa `surfplot` se DISPLAY disponibile
- Altrimenti fallback a `nilearn`

---

## Esempio Completo

**Input**:
- `config.json` con 5 soggetti, mode=dv, scenario=top_percent, percent=0.15

**Processo**:
1. Carica config
2. Legge 5 ID da `subjects.txt`
3. Per ogni soggetto:
   - Legge `indicators.txt`, ordina per colonna 5 (coherence)
   - Prende top 15% frame (es. 180 frame su 1200)
   - Carica nodal strength per ogni frame
   - Media → vettore (116,) per quel soggetto
4. Media 5 vettori → vettore finale (116,)
5. Salva `.npy` e `.png`

**Output**:
- `group_top15_coherence.npy`: vettore (116,)
- `group_top15_coherence.png`: brain map
