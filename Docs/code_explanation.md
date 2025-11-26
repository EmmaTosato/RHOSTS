# **Example Folder**

Contains `.sh` files for running different scripts

# Input Data

- Resting-state fMRI data
- From 100 unrelated subjects from the HCP 900 subjects data release
    
    https://zenodo.org/records/7210076#.Y0qhx-9BxhE
    
- Parcellazione corticale: 100 regioni corticali (Schaefer atlas) + 19 regioni subcorticali = **119 ROI**
- Preprocessing
    - Rimozione motion e segnali confondenti (CSF, WM, GSR)
    - Bandpass filtering (0.01–0.15 Hz)
    - Time series ROI-averaged e z-scored

# **High Order TS**

## simplicial_multivariate.py

### **1. Parallel Processing with Pool**

- Uses Python’s multiprocessing.Pool to run function calls in parallel across CPU cores.
- Crea un **pool di processi paralleli**, uno per ogni core

### 2. ts_simplicial

- Tutti i processi condividono questo **oggetto**, costruito una volta sola dal dataset
- Struttura contente edges and triplets per tutti i time point
- Pre computazione del simplicial, indicatori etc → `simplicial_complex_mvts` in [utils.py](http://utils.py), e parte con `def __init__()`
- Dopo questa riga, `ts_simplicial` ha già in memoria
    - tutti gli edges e triangoli con i relativi z-score e valori massimi
    - le funzioni pronte per generare i complessi simpliciali a ogni istante t, perchè la classe le contiene

### 3. launch_code_one_t

Per ogni istante temporale viene lanciata la funzione per costruire il simplicial complex ed estrarre topological features.

```python
list_simplices_positive, list_violation_fully_coherence, hyper_coherence = ts_simplicial.create_simplicial_complex(t)
```

- Lista di **simplici**, **violazioni** e **ipercoerenza**.
    
    Dalla funzione `def create_simplicial_complex` nella classe `simplicial_complex_mvts`
    
    Ottengo:
    
    1. `list_simplices_positive`
        1. Simplici (nodi, archi, triplette) nella filtrazione 
        2. Il loro peso. Ricorda che è stato flippato, quindi dopo il flip abbiamo:
            1. Valori **negativi** ⇒ simplici **coerenti**
            2. Valori **positivi** ⇒ simplici **decoerenti**
    2. In `list_violation_fully_coherence` ogni elemento è una tupla
        1. Quali sono i triangoli violanti positivi → coerenti
        2. Una flag che indica gli spigoli mancanti quando il triangolo tenta di entrare
    3. `hyper_coherence` = l’ipercoerenza
    

```python
dgms1 = compute_persistence_diagram_cechmate(list_simplices_positive)
```

- **Persistence diagram**
    - Lista di 3 array (H0, H1, H2) con 2 colonne: birth and death
    - Ogni riga in ogni array è una struttura topologica
    
    - Funzioni in utils.py
        - `compute_persistence_diagram_cechmate`
        - `cm.phat_diagrams`

```python
max_filtration_weight = ts_simplicial.find_max_weight(t)
```

- **Massimo valore** assoluto di cofluttuazione (**z-score**) tra edge e triplet al tempo
    1. Qui NON è arrotondato per eccesso come in def create_simplicial_complex

```python
dgms1_clean = clean_persistence_diagram_cechmate(
        dgms1, max_filtration_weight)
```

- **Sostituisce i punti death = inf**

```python
hyper_complexity = persim.sliced_wasserstein(dgms1_clean, np.array([]))
```

- Computa l’indicatore **hyper-complexity**
    1. come la **Sliced Wasserstein distance**
    2. Calcola la distanza tra il diagramma attuale ad un tempo $t$ e il diagramma vuoto
    3. Quanto il sistema al tempo $t$ è **topologicamente complesso /strutturato**
        1. proiettando i punti su più direzioni
        2. confrontando le proiezioni ordinate (L1-distance → Manhattan distance)
        
    
    $$
    \text{iper-complessità} = \text{distanza di Wasserstein tra il diagramma \( H_1 \) e quello vuoto}
    $$
    

```python
dgms1_complexity_FC = dgms1_clean[(dgms1_clean[:, 0] < 0) & (dgms1_clean[:, 1] <= 0)]
dgms1_complexity_CT = dgms1_clean[(dgms1_clean[:, 0] < 0) & (dgms1_clean[:, 1] > 0)]
dgms1_complexity_FD = dgms1_clean[( dgms1_clean[:, 0] > 0) & (dgms1_clean[:, 1] > 0)]
```

- **Classificazione dei cicli 1D**
    
    Vogliamo sapere se un ciclo proviene:
    
    - interazioni sincronizzate (**FC**)
    - da interazioni anti-sincronizzate (**FD**)
    - da un mix (**CT**).
    
    1. Fully Coherent (FC) → birth < 0 e death < 0
        1. Cicli nati e morti solo da interazioni coerenti
    2. Coherent Transition (CT) → birth < 0 e death > 0
        1. Cicli che nascono da interazioni coerenti ma vengono chiusi da decoerenti.
    3. Fully Decoherent (FD) → birth > 0 e death > 0
        1. Cicli nati e chiusi solo da interazioni decoerenti.
        

```python
complexity_FC = persim.sliced_wasserstein(dgms1_complexity_FC, np.array([]))
```

- **Calcola la distanza Wasserstein**
    1. Il sottoinsieme del diagramma di persistenza selezionato (FC, CT, FD)
    2. Il diagramma vuoto [], che rappresenta uno spazio senza struttura topologica.
    
    ⇒ Questa distanza quantifica quanto è importante topologicamente quella famiglia di cicli
    
    ⇒ Quanto “complesso” è il contributo FC, CT o FD
    

```python
flag_violations_list = np.array(list_violation_fully_coherence, dtype="object")[:, 2]
```

- **Estrazione delle violazioni**
    
    Estrae il numero di spigoli mancanti per ciascun triangolo violante
    

```python
avg_edge_violation = np.mean(flag_violations_list)
```

- **Calcolo di quanti lati in media mancano nei triangoli che violano la simplicial closure**
    
    indica quanto "gravi" sono mediamente le violazioni
    

```python
edge_weights = compute_edgeweight(list_violation_fully_coherence, n_ROI)
```

- **Costruzione della proiezione downward** della lista delle violazioni Δv
    1. Vedi spiegazione [funzione](https://www.notion.so/Code-1bb44ec442e080489074d86963b23fd4?pvs=21) + [output](https://www.notion.so/Code-1bb44ec442e080489074d86963b23fd4?pvs=21) data per node strength
    2. Ottengo la lista di edges così definita 
        
        $edge\_weights[(i, j)] = [\text{somma\_pesi}, \text{numero\_occorrenze}]$
        
        1. nodo $i$ 
        2. nodo $j$
        3. Somma dei pesi dei triangoli violanti contenenti $(i, j)$
        4. Numero di triangoli che contengono $(i, j)$

## utils.py

### **class simplicial_complex_mvts**

Viene chiamata la casse quando si costruisce l’oggetto `ts_simplicial` . Questo per tutti i time points con il Pool process.

### def __init__

- Initialization
- **Z-score Normalization** of each signal **(**`compute_zscore_data()`**)**
- z-score?
    
    > Lo z-score misura quanto un valore si discosta dalla media, in termini di deviazioni standard.
    > 
    
    $$
    z = \frac{x- \mu}{ \sigma}
    $$
    

- Shuffling for Null Model (if enabled)
- Precomputes edges and triplets for reducing memory usage (`compute_edges_triplets()`).

### def compute_edges_triplets

### **EDGES**

1. Calcola quanti possibili **archi** si possono formare dai ROI (nodi)
    1. Binomiale 
2. Calcola gli **indici** di tutte le possibili coppie di regioni cerebrali
    1. $i< j$
    2. ROI = 4 
        
        u = [0, 0, 0, 1, 1, 2]
        
        v = [1, 2, 3, 2, 3, 3]
        
        Coppie ROI = (0,1), (0,2), (0,3), (1,2), (1,3), (2,3)
        
3. Calcola la **co-fluttuazione istantanea** tra time series
    - **Co-fluctuation**
        
        > Misuriamo il modo  in cui due nodi (ad esempio, regioni cerebrali) sono collegati nel tempo
        > 
        - $z_i(t)⋅z_j(t)$
            - **1-Order Co-Fluctuation**
            - Element wise product between 2 time series
        - $z_i(t)⋅z_j(t)⋅z_k(t)$
            - **2-Order Co-Fluctuation**
            - Element wise product between 3 time series
        - etc
            - **k-Order Fluctuation**
            - Element wise product between k time series
        
    
    1. Facendo il **prodotto element wise**
        1. Se entrambi i valori sono alti (o bassi), il prodotto è positivo e grande → indica forte co-fluttuazione.
        2. Se uno è positivo e l’altro negativo, il prodotto è negativo, indicando sincro inversa.
        3. Se uno o entrambi sono vicini a zero, il prodotto è vicino a zero, cioè poca sincronizzazione.
    2. `c_prod` è una matrice: ogni riga è la serie temporale di una coppia ROI ottenuta dal prodotto element - wise 
    3. Usa batch per processare tot coppie alla volta, tipo ROI = 119
        1. 0 - 117 
        2. 117 - 233
        3. 233 - 348
        4. etc.
4. Calcolo di **media e deviazione** standard
    1. Media nel tempo di ogni riga → quindi per ogni coppia  
    2. Deviazione standard nel tempo di ogni riga
    3. Ogni coppia `(i,j)` è ora rappresentata da [media, std] → variabile`ets_zscore`
5. Calcolo **z-score assoluto** e aggiornamento del massimo
    1. E’ un vettore lungo T (time points)
    2. Per ogni tempo $t$, trovo il massimo z-score assoluto tra tutte le coppie del batch
    3. Tiene conto dei batch precedenti quindi alla fine `self.ets_max` contiene,  per ogni istante temporale $t$, il valore più alto (in termini di z-score) trovato tra tutte le coppie di regioni cerebrali analizzate.
    4. *“A tempo t, qual è stata la coppia di ROI più sincronizzata rispetto al suo comportamento normale?”*
6. Dizionario per associare indice k a coppia $(i, j)$ 

### TRIPLETS

- Numero totale di triplette
    - Ad esempio qua, con 119 ROI ho 273819 combinazioni possibili
    - Considerando che devo passarle tutte e poi fare la moltiplicazione di time series
- Calcolare il prodotto istantaneo
- Calcolare media e deviazione standard nel tempo
- Calcolare z-score assoluto dinamico
- Trovare, per ogni tempo $t$, il massimo z-score assoluto tra tutte le triplette

### def create_simplicial_complex

> Funzione che crea l'elenco dei semplici (e fornisce anche l'elenco delle violazioni)
> 
1. Crea una lista vuota per i complessi
2. `m_weight` è lo z-score più alto tra tutti gli edges e triplette (si guarda ad`self.ets_max` e `triplets_max` definite prima, che corrispondo ai massimi z-score per edges e triplets ad ogni istante temporale) *arrotondato per eccesso* ad un valore discreto (.ceil)
3. Tutti i nodi entrano insieme, nello stesso momento, e tutti hanno lo stesso peso
4. Computa il peso degli archi, **z-score istantaneo**
    1. Prende i valori 
        1. al tempo `t_current` (è una colonna) 
        2. e agli indici $i$ e $j$ (righe) 
        
        → quindi ho due valori = i valori della time series z-scorati
        
    2. Fa il prodotto 
    3. Lo normalizza → z-score
    4. Corregge il peso in base alla regola della coerenza → `correction_for_coherence`
        1. Per gli edge in realtà è ridondante
        2. Per triplette è necessaria 
5. Dopo aver chiamato `fix_violations` funzione ritorna
    - `list_simplices_for_filtration` = i simplici nella filtrazione
        - Simplici (nodi, archi, triplette)
        - Il loro peso
    - `list_violations` = i violating triangles
        - Quali sono i triangoli violanti
        - Una flag che indica gli spigoli mancanti quando il triangolo tenta di entrare
    - `percentage_of_triangles_discarded` = l’ipercoerenza
    
    → tutto per un istante t 
    

### def correction_for_coherence

- `coherence_function`
- Valori concordi → C’è coerenza **→** Il peso viene reso **positivo**
- Valori discordi→  C’è decoerenza **→** Il peso viene forzato **negativo**

### def fix_violations

> Funzione che rimuove tutti i triangoli violati per creare un filtraggio corretto
> 
- Si **ordinano** i simplici del complesso secondo i loro pesi
- I pesi dei simplici sono ordinati in modo **decrescente**, dal più grande al più piccolo
    - i simplici “forti” (con peso alto) devono entrare prima → interazioni più forti → più coerenza
    - i simplici “deboli” (con peso basso), entrano dopo →  interazioni più deboli → meno coerenza
- Poi nodi + archi vengo inclusi in `list_simplices_for_filtration` (filtrazione)
    - Il peso diventa negativo perché dovrò ottenere una lista in ordine crescente → necessario per il persistence diagram
        - Quindi il simplicio con peso più alto diventa il più basso
        - il diagramma si aspetta quest’ordine
    - gli indici dei simplici sono messi in `set_simplices`
- Se è un triangolo, crea le 3 combinazioni di 2 elementi per quel triangolo
    - Se le 3 combinazioni sono presenti nella filtrazione → triangolo è **topologicamente valido**
        - Viene aggiunto a `list_simplices_for_filtration` e peso invertito
        - E se era coerente (peso ≥ 0), lo conti tra quelli positivi validi
    - Se non tutti i lati sono presenti → **violating triangles.** Ma il triangolo può essere
        - coerente  (--- o +++)
        - incorente
        
        → entrambi vengono salvati ma useremo solo i coerenti (`violation_triangles`) 
        
    
    <aside>
    📌
    
    In altre parole: 
    
    - noi abbiamo ordinato i pesi dal più grande al più piccolo
    - quindi, se un triangolo entra prima di un suo lato, vuol dire che il peso del triangolo è maggiore di quel lato
    - e se Il triangolo ha peso maggiore di almeno uno dei suoi lati, allora è violazione
    - può succedere che manchino 2 lati o anche 3, e nell’ultimo caso vuol dire che il peso del triangolo è maggiore di tutti i 3 lati (si trovano sotto nell’ordinamento crescente fatto all’inizio)
    </aside>
    
    <aside>
    📖
    
    I simplices violanti possono essere considerati **strutture ipercoerenti**, 
    
    - perchè il loro peso è > 0
    - poiché le loro cofluttuazioni di gruppo sono più forti di quelle delle loro parti.
    - Riflettono stati higher-order non catturabili da analisi pairwise.
    </aside>
    
- Vengono anche indicati numero di spigoli mancanti quando il triangolo tenta di entrare
    - flag = 3 → tutti gli spigoli sono già presenti nella filtrazione → il triangolo può entrare
    - flag = 2 , flag = 1 , flag  = 0 → mancano `3 - flag` nella filtrazione → violating triangles per `3 - flag` spigoli
    
- Calcolo **hyper-coherence** indicator
    - Definition
        
        $$
        \text{iper-coerenza} = \frac{\# \text{triangoli violanti con peso > 0}}{\# \text{triangoli con peso > 0}}
        $$
        
    - How?
        
        Usa solo i triangoli positivi, quindi quelli coerenti
        
        1. `violation_triangles` sono positivi
        2. `triangles_count` sono positivi
        
    
- La funzione ritorna:
    - `list_simplices_for_filtration` = i simplici nella filtrazione
        - Simplici (nodi, archi, triplette)
        - Il loro peso
    - `list_violating_triangles` = i violating triangles
        - Quali sono i triangoli violanti
        - Una flag che indica gli spigoli mancanti quando il triangolo tenta di entrare
    - `hyper_coherence` = l’ipercoerenza
    
    → tutto per un istante t 
    

### def coherence_function

- Regola della coerenza pura
    - Se entrambi positivi→  segnali sincronizzati in alto → concordi
    - Se entrambi negativi → segnali sincronizzati in basso → concordi
    - Se uno + e uno ****→ ****segnali opposti → discordi
- Posso avere exponent = 0 o exponent = 1
- Quindi facendo l’esponenziale di -1 posso avere
    - res = 1 → **fully coherent**
    - res = -1 → **decoherent**
- Per gli EDGE
    
    
    | ROI1 | ROI2  | Coerenza? |
    | --- | --- | --- |
    | **+** | **+**  | ✅ sì |
    | **–** | **–**  | ✅ sì |
    | **+** | **–**  | ❌ no |
- Per le TRIPLETTE
    
    
    | ROI1 | ROI2 | ROI3 | Coerenza? |
    | --- | --- | --- | --- |
    | **+**  | **+** | **+** | ✅ sì |
    | **-** | **-** | **-** | ✅ sì |
    | **+** | **-** | **+** | ❌ no |
    | **-** | **-** | **+** | ❌ no |

### def clean_persistence_diagram_cechmate

- con order = 1 seleziona `dgms[1]`
- Quindi per per default, si lavora con $H₁$ = i cicli
- Poi scorre le coppie `(birth, death)` nel diagramma di persistenza di $H₁$.
- Se un feature ha death = ∞ → lo sostituisce con `max_filtration` (cioè il massimo peso usato a quel tempo t).

→ E’ qui che mi tengo solo il gruppo omologico $H_1$

### def compute_persistence_diagram_cechmate

- `cm` è il modulo [Cechmate](https://github.com/scikit-tda/cechmate/blob/master/cechmate/solver.py#L63), una libreria per la topological data analysis (**TDA**).
- In un diagramma di persistenza abbiamo una lista di coppie di numeri (**birth, death**).
    
    > “Quali strutture topologiche (componenti, cicli, cavità) emergono nei  dati e quanto a lungo persistono nella filtrazione simpliciale.”
    > 
    - Se birth e death sono molto lontani → la struttura è persistente, quindi importante
    - Se birth ≈ death → è rumore
    - Se death = ∞ → la struttura non scompare mai
    
    <aside>
    📖
    
    La differenza death – birth è la **persistenza** → più è alta, più la struttura è stabile
    
    </aside>
    
- Noi otteniamo `dgms`, una lista di 3 array, ciascuno contiene un **diagramma di persistenza**.
    
    
    | Indice | Nome | Cosa misura |
    | --- | --- | --- |
    | `dgms[0]` | features di **$H_0$** | Componenti connesse) |
    | `dgms[1]` | features di **$H₁$** | Loop |
    | `dgms[2]` | features di **$H₂$** | Cavità  |

- In ognuno di questi array  ha quindi
    - 2 colonne = birth and death
        1. colonna 0 = birth 
            1. valore della filtrazione quando la feature appare
            2. peso del simplesso che ha dato origine al feature
        2. colonna 1 = death 
            1. valore della filtrazione quando la feature scompare
            2. peso del simplesso che lo ha fatto sparire.
    - n_features = n righe che corrispondono alle topological features

### def compute_edgeweight

- Itera su tutte le violazioni (`list_violations`)
    - triangolo $[i, j, k]$
    - weight è il peso della co-fluttuazione triadica
- Ciclo su tutte le 3 combinazioni di spigoli nel triangolo
    - $(i,j), (i,k), (j,k)$
    - Se lo stesso spigolo $(i, j)$ è già comparso in un triangolo precedente della lista `list_violations:`
        - somma il nuovo peso a quello già accumulato
        - Incrementa il conteggio di 1
        - Altrimenti, lo aggiungi per la prima volta
- Quindi `edge_weight` è un dizionario in cui
    - le chiavi $(i, j)$ rappresentano gli archi
    - I valori $[w_{sum}, count]$ rappresentano:
        - la somma dei pesi dei triangoli violanti che includono quell’arco
        - quanti triangoli violanti contengono quell’arco
- Concettualmente:
    - **Proietto** perché attribuisco il peso del triangolo $w_{ijk}$ a ciascuno dei suoi spigoli $(i,j), (i,k), (j,k)$
    - Se un arco $(i, j)$ appare molto spesso nei triangoli violanti $Δv$, significa è costantemente parte di triangoli che mostrano forte co-fluttuazione triadica → quindi coinvolto in interazioni sincronizzate di ordine superiore

# High Order TS Scaffold

## utils.py

### def fix_violations

> Funzione che rimuove tutti i triangoli violati per creare un filtraggio corretto
> 
- *Vedi sopra per spiegazione*
- `list_simplices_scaffold_all`
    - contiene tutti i simplici topologicamente validi. Include:
        - nodi
        - archi
        - triangoli coerenti che rispettano la simplicial closure
    - OrderedDict()
        - La chiave è il simplicio (lista di vertici) convertito in stringa
        - Il valore è una lista:
            1. Indice di ordine = l’indice in cui entra nella filtrazione
            2. Peso negativo = segno invertito per costruire la filtrazione crescente
- Ogni nodo viene inserito con peso negativo e indice fisso perché entrano tutti "insieme" nel complesso
- Per gli archi
    - Se l’arco ha peso diverso da quello precedente, incrementa l’indice
    - Così simplici con lo stesso peso hanno lo stesso ordine di ingresso.
    - Ricorda: Essendo che i simplici sono ordinati, i pesi uguali saranno vicini
- Per i triangoli
    - I triangoli che rispettano la closure (i loro 3 lati sono già nel complesso) sono inseriti nello scaffold.
    - Il peso viene invertito, come da convenzione nel persistence diagram.

### compute_scaffold (...)

- Funzione che chiama jython code per computare lo scaffold
- **Homological scaffold**
    - Un grafo pesato costruito dai generatori di H₁
    - Ogni ciclo persistente diventa una struttura concreta fatta di archi (edges) e nodi (nodes).
- Un grafo pesato costruito dai generatori di H₁: ogni ciclo persistente diventa una struttura concreta fatta di archi (edges) e nodi (nodes).
- Serve per:
    - capire quali archi sono topologicamente rilevanti
    - rappresentazione grafo like

→ struttura topologica concreta che ti dice dove è localizzata la complessità

## persistent_homology_calculation.py

> Calcolare la persistent homology (in particolare H₁) a partire da un dizionario di simplici filtrati, e salvare i generatori persistenti come cicli concreti (liste di archi) in un file `.pck`.
> 

- converte la stringa in formato JSON ordinato (`OrderedDict`)
- estrae i parametri da sys.argv: dimensione massima, directory output, tag output, path a javaplex, flag salvataggio
- costruisce una lista dei pesi dei simplici e li ordina
- crea un oggetto `ExplicitSimplexStream`
    - una stream è una sequenza ordinata di simplici, ciascuno con:
    - Serve come input al calcolo della persistent homology. Infatti Javaplex usa la stream per:
        - sapere quali simplici ci sono
        - e in che ordine entrano nel complesso
- Per ogni simplex nel dizionario:
    - se è un vertice, lo aggiunge al tempo 0
    - altrimenti lo aggiunge con l’indice di ingresso fornito
- chiude la stream con `finalizeStream()`
- crea un algoritmo per la persistent homology su campo Z₂ fino a dimensione `dimension + 1`
- calcola
    - gli intervalli di persistenza (`computeIntervals`)
    - anche i generatori annotati (`computeAnnotatedIntervals`)
- per ogni dimensione da 1 a dimensione massima:
    - estrae la lista degli intervalli (birth, death) e dei generatori associati
    - per ogni generatore:
        - costruisce i cicli usando `Holes.Cycle` con: dimensione, lista simplici, peso al birth, peso al death
        - aggiunge il ciclo al dizionario dei generatori
- salva l’intero dizionario dei generatori in un file `.pck` nella cartella `gen/`
- stampa a terminale le informazioni base (filtrazione creata, dimensioni, validità, path file generato)

# Output

## Indicators

A row for each time point (the range is defined in the input)

1. Time
2. Hyper complexity indic.
3. Hyper complexity FC
4. Hyper complexity CT 
5. Hyper complexity FD
6. Hyper coherence indicator
7. Average edge violation
8. (Edge weight in formato hdf5 se indicato nelle flag)

![Screenshot 2025-07-01 alle 11.51.09.png](attachment:2a4c931a-e85a-4a64-8390-b3baf432a055:Screenshot_2025-07-01_alle_11.51.09.png)

## Node strength projecting

Proiettando la forza nodale:

1. $\Delta V$ approach: dai triangoli → archi → nodi.
2. Scaffold approach: dai cicli persistenti → archi → nodi.

### What is Nodal strength?

In una rete **pesata**, la forza del nodo $i$ è la **somma dei pesi degli archi incidenti** a $i$. È l’analogo pesato del grado.

$$
⁍
$$

- **Non orientata:** $w_{ij}=w_{ji}$ e si sommano tutti gli archi che toccano $i$.
- **Orientata:**
    - **out-strength** $s_i^{\text{out}}=\sum_j w_{ij}$
    - **in-strength** $s_i^{\text{in}}=\sum_j w_{ji}$

In reti **non pesate** (tutti i $w_{ij}\in\{0,1\}$), la forza coincide con il **grado** del nodo.

<aside>
🔑

Non conta *quanti* vicini ha (quello è il grado), ma quanto forti sono, nel complesso, i legami che lo collegano al resto della rete. 

</aside>

### From the violating triangles ∆v

- Fig. 5 Paper - Mapping
    
    *“Figure 5a reports a brain map of the most discriminative nodes by projecting the magnitudes of the violating triangles Δv on a nodal level. This is equivalent to considering the nodal strength extracted from Δv.”*
    
- Methods
    
    *“To analyse the information provided by the list of violations $Δv$ on an edge/node level, we rely on downwards projections. That is, for each edge $(i, j)$, we assign a weight $w_{ij}$ equal to the average sum of the weights of triangles defined by that edge, that is, triangles of the form $(i, j, ·)$ with a weight $w_{ij·}$, and the average is computed over the number of triangles $n_{ij·}$ defined by that edge.* 
    
    *Similarly, we define the nodal strength $w_i$ of node $i$ as the sum of weights of the triangles connected to node i after the edge projection.”*
    
- 📖 Downwards projections and Nodal strength
    - Δv è la lista dei triangoli che violanti
    - Ogni triangolo ha un peso  → misura la forza della violazione.
    - Considera un arco $(i,j)$, questo arco può appartenere a più triangoli violanti $(i,j,k)$.
    - il peso dell’arco $w_{ij}$ = media dei pesi dei triangoli che contengono $(i,j)$
    - Ogni arco “eredita” un peso che riassume l’influenza dei triangoli violanti a cui partecipa.
    - Ora hai un grafo di archi pesati
    - La forza nodale di un nodo $i$, $w_i$, si calcola come la somma dei pesi di tutti gli archi che toccano $i$
    - Così un nodo ha più forza se partecipa a molti archi che a loro volta sono coinvolti in triangoli violanti ad alto peso.
    
    <aside>
    🔑
    
    Proiettiamo i triangoli prima sugli archi e poi sui nodi.
    
    </aside>
    
- 💻  Computation of Downwards projections - Nodal strength
    - `compute_nodal_strength`
    - Partiamo dal file hdf5 con un dataset per ogni **istante temporale**
    - Ogni dataset ha una shape ($N_\text{triangles}$, 4)
        - E’ l’output di compute_edgeweight in utils.py
        - Quindi ogni riga è un triangolo violante
        - Le colonne indicano questo:
            1. nodo $i$ 
            2. nodo $j$
            3. Somma dei pesi dei triangoli violanti che includono $(i, j)$ → `sum_w`
            4. Numero di triangoli violanti che contengono $(i, j)$ → `count`
    - Loop sulle righe del dataset precedente
        - Prendo ogni arco e ne calcolo la media perché dal dataset ho la somma e il count dei triangoli
        - Salvo questo peso mediato nel dizionario `edge_weight`
    - Proiezione archi → nodi (forza nodale)
        - per ogni riga nel dizionario precedente
        - sommo  `w_ij` sia a `nodal_strength[i]` sia a `nodal_strength[j]` ottenendo così la nodal strength per ogni nodo
- Fig. 5 Paper - 15% most coherent
    - txt con risultati
    - Prendo la colonna dell’iper coerenza
    - Metto in ordine decrescente
    - Prendo il 15% dei time points (= righe) più coerenti
    

### From the Homological Scaffold

- Definition of Homological Scaffold
    
    *“To obtain a finer description of the topological features present in the persistence diagram, we consider the persistence homological scaffold as proposed in ref. 8. In a nutshell, this object is a weighted network composed of all the cycle paths corresponding to generators gi weighted by their persistence $π_{g_i}$. In other words, if an edge e belongs to multiple one-dimensional cycles $g_0, g_1, ..., g_s$, its weight $\bar w^{\pi}e$ is defined as the sum of the generators’ persistence*
    
    $$
    \bar w^{\pi}e \;=\; \sum{g_i:\; e\in g_i} \pi_{g_i}.
    $$
    
- 📖 Homological Scaffold
    - Rete pesata
    - Formata da tutti i cammini ciclici dei generatori di una certa dimensione
        - Ovvero: gli archi del grafo sono l’unione di tutti gli archi che compaiono nei generatori
        - Esempio: tutti gli archi che compaiono nei loop (generatori 1D) in $~~H_1~~$
    - Il peso di un arco $e$ è la persistenza $\pi$ del generatore $g$
        - Se l’arco $e$ compare in due generatori con persistenze $a$ e $b$ allora il peso sarà la somma di queste persistenze
- 💻  Computation of Homological Scaffold
    - Partiamo dal file .pck ad **un** certo **time point**
    - Ci dice quali sono i gruppi di omologia presenti, troveremo sempre H1
    - Dentro ci sono **generatori** omologici H1
        - ovvero i generatori non trivial
        - i loop = cicli 1D persistenti nel tempo
        - ognuno di questi ci dice
            - quali archi formano il loop,
            - la loro persistenza (birth–death interval).
    - Costruzione **scaffold**
        - è una rete pesata
        - gli **archi** sono l’unione di tutti gli archi che compaiono nei cicli
        - il peso di un arco è la **somma** della **la persistenza di tutti i cicli** che contengono quell’arco
- Fig. 5 Paper - Mapping
    
    *“Similar analyses can be produced by focusing on the hyper-complexity indicator and the nodal strength of the homological scaffold constructed from the persistent homology generators of H1.*
    
- Methods
    
    *“In the case of the homological scaffold, since it is a weighted network, the node strength $\bar{w}_i$ of node  $i$ is defined, in the classical way, as the sum of the weights of edges connected to the node $i$.”*
    
- 📖 Nodal strength
    - Dalla rete pesata abbiamo gli archi pesati
    - Ora dobbiamo proiettare sui nodi
    - La forza di un nodo $i$ è definita come la somma degli archi connessi a quel nodo $i$
        - Ad esempio se abbiamo arco $(i, j)$ con $w = 4$ e $(i,k)$ con $w = 6$, la forza di i sarà $10$
    - Questo misura quanto un nodo è coinvolto (globalmente) nei cicli persistenti.
    
- 💻  Computation of  Nodal strength
    - La forza nodale è cioè la somma dei pesi degli archi incidenti al nodo $i$
- Fig. 5 Paper - 15% lowest complexity
    
    *In particular, Fig. 5c depicts the brain map obtained when isolating the 15% of frames with lowest hyper-complexity, which are those associated with more synchronized dynamical phases.”*
    

## Hyper Complexity

*“By construction, the these three contributions sum up to the total hyper-complexity.”*

 

- Plottare i punti (uno per ogni timepoint) in uno **spazio ternario** (triangolo equilatero)
- Ogni punto ha coordinate derivate dai **contributi normalizzati**:
    - FC = fully coherent
    - CT = coherence transition
    - FD = fully decoherent
- FC, CT, FD sono componenti non negative che sommano a un totale → l’indicatore di **ipercomplessità**
- Si normalizza perchè la posizione di un punto nel triangolo non dipende dai valori assoluti
- Poi si estraggono le coordinate per plottare il contributo di queste coordinate in un punto