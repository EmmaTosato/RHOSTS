# Guida personale RHOSTS
## Stato di questa copia
- È la fotografia del progetto ferma al momento in cui non riuscivo a bilanciare RAM e CPU.
- I calcoli risultavano incompleti e lenti: 
  - aumentando i core andavo in OOM.
  - dimunendo i core i calcoli erano lenti
- Perchè? Ogni volta che viene richiesta la costruzione dello scaffold omologico, viene lanciato un interprete Jython (e quindi una JVM) per poter sfruttare le API JavaPlex
- Ho gestito malamente la RAM relegata alle JVM, quindi troppe JVM causavano OOM.

## Soluzione
- Lo script chiede a SLURM 20 GB di RAM per ogni job con #SBATCH --mem=20G, così che il processo venga ucciso dal workload manager se oltrepassa il tetto assegnato.
- Vengono lanciati diversi job, così si divide il carico (--array)
- Prima di lanciare Python imposta JAVA_TOOL_OPTIONS="-Xms2G -Xmx16G", costringendo ogni JVM avviata da Jython a restare entro 16 GB di heap (partendo da 2 GB); in pratica l’OOM viene prevenuto limitando l’heap della JVM.


## Dove trovare la versione attiva
Lo sviluppo prosegue sul branch `main`, dove ho riprogettato la pipeline tenendo conto di RAM e CPU. Passa lì per l'ultima versione stabile.

