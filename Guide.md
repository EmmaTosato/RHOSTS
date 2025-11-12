# Guida personale RHOSTS
## Stato di questa copia
- È la fotografia del progetto ferma al momento in cui non riuscivo a bilanciare RAM e CPU.
- I calcoli risultavano incompleti e lenti: 
  - aumentando i core andavo in OOM.
  - dimunendo i core i calcoli erano lenti
- Perchè? Ogni volta che viene richiesta la costruzione dello scaffold omologico, viene lanciato un interprete Jython (e quindi una JVM) per poter sfruttare le API JavaPlex
- Ho gestito malamente la RAM relegata alle JVM, quindi troppe JVM causavano OOM.

## Cosa ho imparato
1. 

## Dove trovare la versione attiva
Lo sviluppo prosegue sul branch `main`, dove ho riprogettato la pipeline tenendo conto di RAM e CPU. Passa lì per l'ultima versione stabile.

