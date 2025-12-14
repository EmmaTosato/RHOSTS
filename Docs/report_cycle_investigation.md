# Analisi Cicli Bassi nei Generatori

**Data**: 2025-12-12  
**Soggetto**: 134829  
**Task**: Investigazione pochi cicli in alcuni timepoint

## Problema
Dal `verification_report.md` abbiamo identificato che alcuni timepoint (1203, 1219, 1222) del soggetto 134829 hanno molto pochi cicli topologici (1-7) invece del normale (~6555).

## Ipotesi dal Report
Il report suggeriva che fosse dovuto a "ipersincronizzazione" - quando la maggior parte delle ROI si muove nella stessa direzione.

## Analisi Effettuata

### Conteggio Cicli Confermato
- `generators__100.pck`: **6555 cicli** (normale)
- `generators__1203.pck`: **6 cicli** (basso)
- `generators__1219.pck`: **3 cicli** (molto basso)  
- `generators__1222.pck`: **3 cicli** (molto basso)

### Analisi Z-score dei Timepoint

| Timepoint | Mean Z-score | ROI Positive | % Positive | Tipo |
|-----------|-------------|--------------|-----------|------|
| 100 (normale) | -0.0261 | 48/116 | 41.4% | BILANCIATO |
| 1203 | +0.5669 | 95/116 | **81.9%** | IPER+ |
| 1219 | -0.7073 | 17/116 | **14.7%** | IPER- |
| 1222 | +0.3999 | 74/116 | 63.8% | LIEVE+ |

## Conclusioni

### ✅ IPOTESI CONFERMATA
I timepoint con pochi cicli mostrano chiara **ipersincronizzazione**:

1. **Timepoint 1203**: 81.9% ROI positive (ipersincronizzazione positiva)
2. **Timepoint 1219**: 85.3% ROI negative (ipersincronizzazione negativa)  
3. **Timepoint 1222**: Parzialmente ipersincronizzato (63.8% positive)

### Meccanismo
Quando la maggior parte delle ROI ha lo stesso segno (tutte positive o tutte negative), il segnale diventa topologicamente "piatto". Questo riduce drasticamente la complessità topologica e quindi il numero di cicli identificabili.

### Implicazioni
- **I file .pck NON sono corrotti** ✅
- **Il comportamento è fisiologicamente corretto** ✅  
- **Possibili cause**: movimenti del soggetto, respirazione profonda, artefatti
- **Per l'analisi**: considerare esclusione di timepoint ipersincronizzati

## File di Riferimento
- Script analisi: `analyze_timepoints.py`
- Job SLURM: `run_cycle_analysis.sbatch` (Job ID: 181086)
- Output SLURM: `cycle_analysis_181086.out`
- Dati: `Input/lorenzo_data/cortical_subcortical/134829_ts_zscore_ctx_sub.txt`
- Generators: `Output/lorenzo_data/134829/generators/`

## Procedura Seguita
1. Analisi manuale dei file `.pck` con `Test/check_scaffold_integrity.py`
2. Creazione script Python per analisi Z-score dei timepoint
3. Esecuzione via SLURM seguendo regole `.agent`
4. Documentazione risultati in `Logs/cycle_analysis/`
