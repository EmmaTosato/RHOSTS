#!/usr/bin/env python
import numpy as np

def analyze_timepoint(filepath, timepoint_index):
    """Analizza un singolo timepoint dal file time series"""
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    # Ottieni la riga corrispondente al timepoint (0-indexed)
    line = lines[timepoint_index].strip()
    values = np.array([float(x) for x in line.split()])
    
    # Calcola statistiche
    mean_val = np.mean(values)
    std_val = np.std(values)
    min_val = np.min(values)
    max_val = np.max(values)
    
    # Conta valori positivi/negativi
    positive = np.sum(values > 0)
    negative = np.sum(values < 0)
    total = len(values)
    
    print("Timepoint {}:".format(timepoint_index))
    print("  Mean: {:.4f}".format(mean_val))
    print("  Std: {:.4f}".format(std_val))
    print("  Min: {:.4f}".format(min_val))
    print("  Max: {:.4f}".format(max_val))
    print("  Positive ROIs: {}/{} ({:.1f}%)".format(positive, total, positive/total*100))
    print("  Negative ROIs: {}/{} ({:.1f}%)".format(negative, total, negative/total*100))
    print("  Range: {:.4f}".format(max_val - min_val))
    
    return {
        'timepoint': timepoint_index,
        'mean': mean_val,
        'std': std_val,
        'min': min_val,
        'max': max_val,
        'positive_count': positive,
        'negative_count': negative,
        'total_rois': total
    }

# Analizza i timepoint problematici e uno normale
filepath = '/data/etosato/RHOSTS/Input/lorenzo_data/cortical_subcortical/134829_ts_zscore_ctx_sub.txt'

print("=== ANALISI TIMEPOINT PROBLEMATICI VS NORMALE ===\n")

# Timepoint normale (dal report: ~6555 cicli)
normal_stats = analyze_timepoint(filepath, 100)
print()

# Timepoint problematici (dal report: bassi cicli)
problem1_stats = analyze_timepoint(filepath, 1203)
print()

problem2_stats = analyze_timepoint(filepath, 1219)
print()

problem3_stats = analyze_timepoint(filepath, 1222)
print()

print("=== CONFRONTO ===")
print("Timepoint normale (100): Mean={:.4f}, Pos={}/{}".format(normal_stats['mean'], normal_stats['positive_count'], normal_stats['total_rois']))
print("Timepoint 1203: Mean={:.4f}, Pos={}/{}".format(problem1_stats['mean'], problem1_stats['positive_count'], problem1_stats['total_rois']))
print("Timepoint 1219: Mean={:.4f}, Pos={}/{}".format(problem2_stats['mean'], problem2_stats['positive_count'], problem2_stats['total_rois']))
print("Timepoint 1222: Mean={:.4f}, Pos={}/{}".format(problem3_stats['mean'], problem3_stats['positive_count'], problem3_stats['total_rois']))

print("\n=== CONCLUSIONI ===")
print("Ipersincronizzazione: quando la maggior parte delle ROI ha lo stesso segno (tutto +, tutto -)")
print("Questo riduce la complessità topologica perché il segnale diventa 'piatto'")
