import os
import sys
import pickle
import argparse
from pathlib import Path

# Add path to find Holes module
sys.path.append("/data/etosato/RHOSTS/High_order_TS_with_scaffold")
try:
    import Holes
except ImportError:
    # If Holes is not found, we might still be able to unpickle if we are lucky, 
    # but likely it will fail. We'll proceed and see.
    pass

def check_file(filepath):
    """
    Checks if a pickle file is valid and counts cycles.
    Returns (True, cycle_count) if valid, (False, 0) otherwise.
    """
    try:
        if os.path.getsize(filepath) == 0:
            return False, 0
        with open(filepath, "rb") as f:
            data = pickle.load(f)
        
        cycle_count = 0
        if isinstance(data, dict):
            for key in data:
                if isinstance(data[key], list):
                    cycle_count += len(data[key])
        
        return True, cycle_count
    except Exception as e:
        # print(f"Error checking {filepath}: {e}")
        return False, 0

def main():
    parser = argparse.ArgumentParser(description="Check integrity of pickle files in a directory.")
    parser.add_argument("directory", help="Directory containing .pck files to check")
    parser.add_argument("--delete", action="store_true", help="Delete corrupted files")
    parser.add_argument("--pattern", default="*.pck", help="File pattern to match (default: *.pck)")
    
    args = parser.parse_args()
    
    target_dir = Path(args.directory)
    if not target_dir.exists():
        print(f"Error: Directory {target_dir} does not exist.")
        sys.exit(1)
        
    print(f"Scanning {target_dir} for {args.pattern}...")
    
    files = list(target_dir.glob(args.pattern))
    print(f"Found {len(files)} files.")
    
    corrupted = []
    valid_count = 0
    
    for i, file_path in enumerate(files):
        if i % 100 == 0:
            print(f"Processed {i}/{len(files)}...")
            
        is_valid, count = check_file(file_path)
        if is_valid:
            valid_count += 1
            print(f"VALID: {file_path} - Cycles: {count}")
        else:
            print(f"CORRUPTED: {file_path}")
            corrupted.append(file_path)
            
    print(f"\nSummary:")
    print(f"Total files: {len(files)}")
    print(f"Valid files: {valid_count}")
    print(f"Corrupted files: {len(corrupted)}")
    
    if args.delete and corrupted:
        print("\nDeleting corrupted files...")
        for f in corrupted:
            try:
                os.remove(f)
                print(f"Deleted: {f}")
            except OSError as e:
                print(f"Error deleting {f}: {e}")

if __name__ == "__main__":
    main()
