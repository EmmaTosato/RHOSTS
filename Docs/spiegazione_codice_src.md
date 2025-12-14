# Spiegazione Completa del Codice in `src`

Questa guida spiega tutti i moduli nella directory `src` del progetto RHOSTS.

---

## 📋 Panoramica Generale

Il codice in `src` è organizzato in due macro-aree:

1. **`src/preprocessing`** - Pre-processamento dati fMRI HCP
2. **`src/higher_order`** - Pipeline per l'analisi higher-order (configurata via JSON)

### Struttura Directory `src`

```
src/
├── run_analysis.sh          # Script SLURM di lancio
├── preprocessing/
│   ├── preprocessing.sh
│   └── preprocessing_hcp.py
└── higher_order/
    ├── __init__.py
    ├── orchestration/
    │   └── main.py          # Entry point (legge config JSON)
    ├── nodal_strength/
    │   ├── loaders_dv.py
    │   ├── loaders_scaffold.py
    │   └── utils.py
    └── visualization/
        ├── utils_neuromaps_brain.py
        └── utils_nilearn_brain.py
```

---

## 🎯 Configurazione via JSON

Il nuovo sistema usa un file `config.json` per tutti i parametri:

```json
{
  "mode": "dv",
  "scenario": "top_percent",
  "percent": 0.15,
  "metric": "coherence",
  "subjects_list_file": "/path/to/subjects.txt",
  "data_path_pattern": "/path/{subject}/{subject}_edge_projection.hd5",
  "indicators_path_pattern": "/path/{subject}/{subject}_indicators.txt",
  "num_rois": 116,
  "output": {
    "npy_path": "/path/output.npy",
    "img_path": "/path/output.png"
  }
}
```

### Parametri

| Parametro | Valori | Descrizione |
|-----------|--------|-------------|
| `mode` | `"dv"`, `"scaffold"` | Tipo di analisi |
| `scenario` | `"single_frame"`, `"all_frames"`, `"top_percent"` | Selezione frame |
| `percent` | 0.0-1.0 | Percentuale frame (per `top_percent`) |
| `metric` | `"coherence"`, `"complexity"` | Metrica per selezione |
| `subjects_list_file` | path | File txt con lista ID soggetti |
| `data_path_pattern` | pattern | Pattern con `{subject}` per file dati |
| `num_rois` | int | Numero ROI (default: 116) |

---

## 🔬 Parte 1: Preprocessing (`src/preprocessing`)

### `preprocessing_hcp.py`

**Obiettivo**: Estrarre time series ROI-averaged da dati fMRI 4D.

**Input**:
- fMRI data: `.nii.gz` 4D `(X, Y, Z, T)`
- Atlanti: corticale (100 ROI) + sottocorticale (16 ROI)

**Output**: File `.txt` con matrice `(T, 116)` normalizzata z-score.

---

## 🧠 Parte 2: Higher-Order Analysis (`src/higher_order`)

### Workflow Principale

```
┌─────────────────────────────────────────────────────────┐
│                    config.json                           │
│  (mode, scenario, subjects_list, patterns, output)       │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│                    main.py                               │
│  1. Legge config JSON                                    │
│  2. Carica lista soggetti da subjects.txt                │
│  3. Per ogni soggetto:                                   │
│     - Seleziona frame (top 15% coherence, etc.)          │
│     - Carica nodal strength per ogni frame               │
│     - MEDIA SUI TIMEPOINTS → vettore soggetto            │
│  4. MEDIA SUI SOGGETTI → vettore finale                  │
│  5. Salva .npy e genera brain map .png                   │
└─────────────────────────────────────────────────────────┘
```

### Due Modalità di Analisi

**DV (Dynamic Violations)**:
- Input: file `.hd5` con edge projections da triangoli violanti
- Metrica default: `coherence` (valori ALTI = più sincronizzato)
- Colonna indicatori: 5 (hyper-coherence)

**Scaffold (Homological Scaffold)**:
- Input: directory con file `generators__*.pck`
- Metrica default: `complexity` (valori BASSI = più sincronizzato)
- Colonna indicatori: 1 (hyper-complexity)

### Scenari di Selezione Frame

| Scenario | Descrizione |
|----------|-------------|
| `single_frame` | Analizza un solo frame (richiede `frame` nel config) |
| `all_frames` | Analizza tutti i frame disponibili |
| `top_percent` | Seleziona top/bottom % secondo metrica |

---

## 📊 Logica di Aggregazione

Come richiesto dal paper (Santoro et al., Nature Physics 2023):

> "Results are averaged over all 100 HCP subjects and scans"

Il codice implementa esplicitamente:

```python
# Per ogni soggetto
for subj_id in subjects:
    # Media sui TIMEPOINTS selezionati
    for frame in selected_frames:
        nodal = load_nodal_strength(subj_id, frame)
        time_accum += nodal
    subject_avg = time_accum / n_frames
    subject_averages.append(subject_avg)

# Media sui SOGGETTI
group_mean = mean(subject_averages)  # Vettore finale (116,)
```

---

## 🚀 Come Lanciare

```bash
# 1. Crea/modifica config.json
# 2. Assicurati che subjects.txt contenga gli ID
# 3. Lancia:

sbatch src/run_analysis.sh config.json
```

**Output**:
- `.npy`: vettore nodal strength `(num_rois,)`
- `.png`: brain map (se ambiente supporta rendering)

---

## 🔑 Concetti Chiave

### Downward Projection
- **Dai triangoli agli archi**: peso arco = media pesi triangoli
- **Dagli archi ai nodi**: nodal strength = somma pesi archi incidenti

### Frame Selection
- La selezione è basata su file `indicators.txt`
- Colonna 5 = hyper-coherence, Colonna 1 = hyper-complexity
- `coherence` prende valori ALTI, `complexity` prende valori BASSI
