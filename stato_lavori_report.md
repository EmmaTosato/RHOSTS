# Stato Lavori: Ristrutturazione Pipeline RHOSTS

Ecco il riepilogo del lavoro svolto per semplificare e correggere la pipeline di analisi.

## ✅ Lavoro Completato

### 1. Documentazione e Logica
- **Chiarimento Workflow**: Confermato che la modalità `group` era ridondante. La logica corretta (implementata ora) è:
  1. Per ogni soggetto -> Media su Timepoints (selezionati)
  2. Media tra i vettori risultanti dei Soggetti
- **Documentazione**: Aggiornati `spiegazione_codice_src.md` e creato `analisi_dettagliata_codice.md` in `Docs/`.

### 2. Refactoring Codice (`src/higher_order/orchestration/main.py`)
Ho riscritto completamente `main.py`. Ora:
- **Configurazione unica**: Legge tutto da un file JSON (niente più lunghe stringhe di argomenti CLI).
- **Lista Soggetti**: Legge gli ID da un file di testo (es. `subjects.txt`) invece di passarli uno a uno.
- **Logica Esplicita**:
  - Implementa il doppio loop di mediazione (Timepoints → Subjects) direttamente nel main.
  - Gestisce logicamente gli scenari:
    - **DV**: Top 15% Coherence (Alti valori)
    - **Scaffold**: Bottom 15% Complexity (Bassi valori)
- **Output**: Salva direttamente il `.npy` medio finale e la brain map `.png`.

### 3. Nuovi Script di Supporto
- **`config.json`**: File di configurazione attivo (attualmente puntato su `lorenzo_data` per test).
- **`Docs/config_template.json`**: Template pulito per usi futuri.
- **`run_analysis.sh`**: Nuovo script SLURM semplice per lanciare l'analisi.
- **`Output/lorenzo_data/subjects.txt`**: File con 5 ID di test.

### 4. Pulizia
- Deprecati e rinominati in `.bak` gli script vecchi complicati: `group.sh`, `main.sh`, `launch_wrapper.sh`.

---

## 🚧 Stato Attuale & Prossimi Passi

Il codice è pronto. Stavamo avviando la verifica finale quando ci siamo interrotti.

### Da dove riprendere:

1. **Lanciare Verifica**:
   Eseguire `sbatch run_analysis.sh` per testare la pipeline sui 5 soggetti di prova.

2. **Controllare Output**:
   Verificare che in `Output/lorenzo_data/results/` vengano creati:
   - `group_top15_coherence.npy`
   - `group_top15_coherence.png`

3. **Verifica Estesa (Opzionale)**:
   Provare a cambiare il `config.json` per testare un caso "Scaffold" o "All Frames" per assicurarsi che la flessibilità funzioni.

---

### File Chiave Creati/Modificati
- `src/higher_order/orchestration/main.py` (Nuovo core logic)
- `config.json` (Configurazione)
- `run_analysis.sh` (Launcher)
- `subjects.txt` (Lista ID)
