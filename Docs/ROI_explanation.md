# Spiegazione: ROI Positive vs Negative

## Cosa Significa "ROI Positive/Negative"?

**NON** si riferisce alla posizione anatomica, ma al **segno del Z-score**:

### Z-score = Misura di Attivazione
- **Z-score**: indica quanto l'attivazione di una ROI in quel momento differisce dalla sua media
- **Formula**: Z = (valore_attuale - media_ROI) / deviazione_standard_ROI

### ROI "POSITIVE" (Z > 0)
- **Significa**: ROI più **ATTIVA** del normale
- **Esempio**: Una ROI che normalmente ha attivazione "5" ora ha attivazione "8" → Z positivo
- **Interpretazione**: "Questa area del cervello sta lavorando più del solito"

### ROI "NEGATIVE" (Z < 0)  
- **Significa**: ROI meno **ATTIVA** del normale
- **Esempio**: Una ROI che normalmente ha attivazione "5" ora ha attivazione "2" → Z negativo
- **Interpretazione**: "Questa area del cervello sta lavorando meno del solito"

## Esempi Pratici

### Timepoint NORMALE (es. t=100)
```
ROI_001: Z = +0.3  (leggermente più attiva)
ROI_002: Z = -0.8  (leggermente meno attiva)  
ROI_003: Z = +1.2  (più attiva)
ROI_004: Z = -0.4  (leggermente meno attiva)
...
Risultato: 48 ROI positive, 68 ROI negative → BILANCIATO
```

### Timepoint IPERSINCRONIZZATO POSITIVO (es. t=1203)
```
ROI_001: Z = +2.1  (molto più attiva)
ROI_002: Z = +0.5  (più attiva)
ROI_003: Z = +1.8  (molto più attiva)  
ROI_004: Z = +0.9  (più attiva)
...
Risultato: 95 ROI positive, 21 ROI negative → TUTTO SU!
```

### Timepoint IPERSINCRONIZZATO NEGATIVO (es. t=1219)
```
ROI_001: Z = -1.8  (molto meno attiva)
ROI_002: Z = -2.3  (molto meno attiva)
ROI_003: Z = -0.7  (meno attiva)
ROI_004: Z = -1.4  (molto meno attiva)  
...
Risultato: 17 ROI positive, 99 ROI negative → TUTTO GIÙ!
```

## Perché Causa Pochi Cicli?

### Topologia Normale
- ROI con attivazioni diverse creano "colline" e "valli" nel paesaggio topologico
- Queste variazioni generano molti cicli omologici (buchi, cavità)
- **Esempio**: 6555 cicli

### Topologia Ipersincronizzata  
- Tutte le ROI si muovono insieme (tutto su o tutto giù)
- Il paesaggio diventa "piatto" - poca variabilità
- Pochi buchi/cavità → pochi cicli omologici
- **Esempio**: 3-6 cicli

## Analogia
Immagina l'attivazione cerebrale come un **paesaggio 3D**:
- **Normale**: Montagne, valli, colline → topologia complessa → molti buchi
- **Ipersincronizzata**: Pianura piatta → topologia semplice → pochi buchi

## Cause Possibili di Ipersincronizzazione
1. **Movimento del soggetto** durante la risonanza
2. **Respirazione profonda** o trattenimento del respiro
3. **Artefatti** di acquisizione
4. **Stati fisiologici** particolari (sonnolenza, etc.)

## Conclusione
- **ROI positive/negative** = Più/meno attive del normale (Z-score)
- **Ipersincronizzazione** = Tutte le ROI si muovono insieme
- **Risultato** = Topologia semplice = Pochi cicli omologici
- **I file .pck sono CORRETTI**, non corrotti!
