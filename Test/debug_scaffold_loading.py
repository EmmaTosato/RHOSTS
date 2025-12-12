import pickle as pk
import os
import sys
sys.path.append("/data/etosato/RHOSTS/High_order_TS_with_scaffold")

# Path to the file
path = "/data/etosato/RHOSTS/Output/lorenzo_data/134829/generators/generators__0.pck"
hom_group = 1

print(f"Loading {path}...")

if not os.path.exists(path):
    print("File does not exist!")
    sys.exit(1)

try:
    with open(path, "rb") as f:
        gen = pk.load(f)
    print("Pickle loaded successfully.")
    print(f"Keys in loaded object: {list(gen.keys()) if isinstance(gen, dict) else 'Not a dict'}")
    
    if hom_group in gen:
        cycles = gen[hom_group]
        print(f"Found hom_group={hom_group} with {len(cycles)} cycles.")
        if len(cycles) > 0:
            print(f"First cycle: {cycles[0]}")
            # Try to replicate loader logic
            try:
                 w = float(cycles[0].persistence_interval())
                 print(f"First cycle persistence: {w}")
            except Exception as e:
                 print(f"Error accessing persistence: {e}")
    else:
        print(f"hom_group={hom_group} NOT found in pickle.")

except Exception as e:
    print(f"Failed to inspect pickle: {e}")
