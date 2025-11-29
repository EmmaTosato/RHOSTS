import os
import sys
import pickle
import argparse
from pathlib import Path

def check_file(filepath):
    """
    Checks if a pickle file is valid.
    Returns True if valid, False otherwise.
    """
    try:
        if os.path.getsize(filepath) == 0:
            return False
        with open(filepath, "rb") as f:
            pickle.load(f)
        return True
    except Exception as e:
        print(f"Error checking {filepath}: {e}")
        return False

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
            
        if check_file(file_path):
            valid_count += 1
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
