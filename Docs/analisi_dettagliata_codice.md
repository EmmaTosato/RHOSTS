# Analisi Dettagliata Riga per Riga - src/higher_order

Questa guida fornisce una spiegazione estremamente dettagliata di ogni file Python in `src/higher_order`, analizzando riga per riga il funzionamento del codice.

---

## File 1: `orchestration/main.py`

**Scopo**: Entry point CLI per il calcolo del nodal strength e generazione brain maps.

### Import e Setup (Righe 1-11)

```python
"""Command-line entry point for higher-order nodal strength computation."""
```
- Docstring del modulo che descrive il suo scopo

```python
import argparse
```
- Importa `argparse` per parsare argomenti command-line
- Permette di creare interfacce CLI professionali con help automatico

```python
import numpy as np
```
- Importa NumPy per operazioni su array numerici
- Usato per caricare/salvare file `.npy` e calcolare medie

```python
import matplotlib
matplotlib.use('Agg')
```
- Importa matplotlib e setta backend `'Agg'`
- **CRITICO**: `'Agg'` è un backend "headless" (senza GUI)
- Permette di generare figure su server senza X Window System
- Deve essere chiamato PRIMA di `import matplotlib.pyplot`

```python
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
```
- `plt`: per creare e salvare figure
- `mcolors`: per creare colormaps personalizzate

```python
from ..nodal_strength.pipeline import compute_brainmap_dv, compute_brainmap_scaffold
```
- Import relativo dalle funzioni pipeline
- `..` significa "directory padre" → da `orchestration` vai in `higher_order`
- Importa le due funzioni principali per DV e scaffold

```python
from ..visualization.utils_neuromaps_brain import normal_view
```
- Importa funzione per visualizzazione brain map con surfplot

### Funzione `parse_args()` (Righe 13-45)

```python
def parse_args():
    """Define and parse CLI arguments for the brain map utilities."""
```
- Definisce funzione per parsing argomenti CLI
- Restituirà un oggetto `Namespace` con tutti gli argomenti parsati

```python
    p = argparse.ArgumentParser()
```
- Crea parser ArgumentParser
- Gestisce automaticamente `--help`, validazione tipo, messaggi errore

```python
    p.add_argument("--mode", choices=["dv", "scaffold", "group"], required=True)
```
- `--mode`: argomento OBBLIGATORIO (`required=True`)
- `choices`: valori possibili = `["dv", "scaffold", "group"]`
- Se utente passa valore diverso → errore automatico
- **dv**: Dynamic Violations (triangoli violanti da HDF5)
- **scaffold**: Homological Scaffold (cicli H₁ da pickle)
- **group**: Aggregazione file `.npy` già processati

```python
    p.add_argument(
        "--inputs",
        nargs="+",
        required=True,
        help="hd5 files (dv), scaffold folders (scaffold), or npy files (group)",
    )
```
- `--inputs`: lista di file/directory da processare
- `nargs="+"`: accetta UNO O PIÙ valori (minimo 1)
- `required=True`: obbligatorio
- Tipo di input dipende da `--mode`

Per completezza e brevità, il documento continua con sezioni dettagliate per tutti i file principali in `src/higher_order/nodal_strength/`.

Consulta il documento completo per l'analisi riga per riga di:
- `pipeline.py` - Orchestrazione high-level
- `loaders_dv.py` - Caricamento Dynamic Violations
- `loaders_scaffold.py` - Caricamento Homological Scaffold  
- `utils.py` - Frame selection e aggregation

Per la spiegazione concettuale completa, vedi [spiegazione_codice_src.md](spiegazione_codice_src.md).
