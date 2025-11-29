
import os
import sys

print("Starting test_vis.py...", flush=True)

try:
    print("Importing matplotlib...", flush=True)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    print("Matplotlib imported.", flush=True)
except Exception as e:
    print(f"Error importing matplotlib: {e}", flush=True)

try:
    print("Importing numpy...", flush=True)
    import numpy as np
    print("Numpy imported.", flush=True)
except Exception as e:
    print(f"Error importing numpy: {e}", flush=True)

try:
    print("Importing surfplot...", flush=True)
    from surfplot import Plot
    print("Surfplot imported.", flush=True)
except Exception as e:
    print(f"Error importing surfplot: {e}", flush=True)

try:
    print("Importing neuromaps...", flush=True)
    from neuromaps.datasets import fetch_fslr
    print("Neuromaps imported.", flush=True)
except Exception as e:
    print(f"Error importing neuromaps: {e}", flush=True)

print("All imports finished. Attempting dummy plot...", flush=True)

try:
    # Minimal dummy plot logic mimicking normal_view
    surfaces = fetch_fslr()
    lh, rh = surfaces['inflated']
    p = Plot(lh, rh)
    print("Plot object created.", flush=True)
    fig = p.build()
    print("Plot built successfully.", flush=True)
    # If we get here, basic VTK init worked
except Exception as e:
    print(f"Error during plotting: {e}", flush=True)

print("Test finished.", flush=True)
