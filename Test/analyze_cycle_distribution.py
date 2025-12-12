#!/usr/bin/env python
import numpy as np
import pickle
import sys
import os

# Add path to find Holes module
sys.path.append("/data/etosato/RHOSTS/High_order_TS_with_scaffold")
try:
    import Holes
except ImportError:
    pass

def count_cycles(filepath):
    """Conta i cicli in un file .pck"""
    try:
        with open(filepath, "rb") as f:
            data = pickle.load(f)
        
        cycle_count = 0
        if isinstance(data, dict):
            for key in data:
                if isinstance(data[key], list):
                    cycle_count += len(data[key])
        return cycle_count
    except:
        return 0

def analyze_timepoint_zscore(filepath, timepoint_index):
    """Analizza Z-score per un timepoint"""
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    line = lines[timepoint_index].strip()
    values = np.array([float(x) for x in line.split()])
    
    mean_val = np.mean(values)
    positive = np.sum(values > 0)
    total = len(values)
    
    return mean_val, positive, total

# Analizza diversi timepoint 
input_file = '/data/etosato/RHOSTS/Input/lorenzo_data/cortical_subcortical/134829_ts_zscore_ctx_sub.txt'
generators_dir = '/data/etosato/RHOSTS/Output/lorenzo_data/134829/generators/'

print("=== ANALISI SISTEMATICA TIMEPOINT ===")
print("Timepoint | Cicli | Mean Z-score | ROI Positive | % Positive | Tipo")
print("-" * 70)

# Lista di timepoint da analizzare
timepoints_to_check = [50, 100, 150, 200, 500, 1000, 1203, 1219, 1222, 1500, 2000, 2500, 3000, 3500]

for tp in timepoints_to_check:
    # Controlla se il file generators esiste
    gen_file = f"{generators_dir}generators__{tp}.pck"
    if os.path.exists(gen_file):
        cycles = count_cycles(gen_file)
        mean_z, pos_count, total = analyze_timepoint_zscore(input_file, tp)
        pos_perc = (pos_count / total) * 100
        
        # Classifica il tipo in base alla % di ROI positive
        if pos_perc > 75:
            tipo = "IPER+"
        elif pos_perc < 25:
            tipo = "IPER-"
        else:
            tipo = "NORM"
            
        print(f"{tp:8d} | {cycles:5d} | {mean_z:11.4f} | {pos_count:11d} | {pos_perc:8.1f} | {tipo}")
    else:
        print(f"{tp:8d} | FILE NOT FOUND")

print("\nLEGENDA:")
print("IPER+: Ipersincronizzazione positiva (>75% ROI positive)")
print("IPER-: Ipersincronizzazione negativa (<25% ROI positive)")
print("NORM:  Normale (25-75% ROI positive)")

# Analizza la distribuzione generale
print("\n=== DISTRIBUZIONE GENERALE ===")
total_files = len([f for f in os.listdir(generators_dir) if f.endswith('.pck')])
print(f"Totale file generators: {total_files}")

# Conta file con bassi cicli
low_cycle_files = []
for i in range(0, 3600, 100):  # Controlla ogni 100 timepoint
    gen_file = f"{generators_dir}generators__{i}.pck"
    if os.path.exists(gen_file):
        cycles = count_cycles(gen_file)
        if cycles < 100:  # Soglia arbitraria per "pochi cicli"
            low_cycle_files.append((i, cycles))

print(f"File con <100 cicli (campione ogni 100): {len(low_cycle_files)}")
if low_cycle_files:
    print("Timepoint con pochi cicli:")
    for tp, cycles in low_cycle_files[:10]:  # Mostra i primi 10
        print(f"  {tp}: {cycles} cicli")
