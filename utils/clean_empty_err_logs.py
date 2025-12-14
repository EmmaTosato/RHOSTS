#!/usr/bin/env python3
"""
Utility script to clean up empty .err log files.

Scans the Logs directory recursively and deletes any .err files that are empty.
This helps keep the log directory clean after SLURM jobs complete successfully.

Usage:
    python clean_empty_err_logs.py [--dry-run]

Options:
    --dry-run  Show what would be deleted without actually deleting
"""

import os
import sys
from pathlib import Path
from typing import List

# Default logs directory (relative to this script's location)
LOGS_DIR = Path(__file__).parent.parent / "Logs"


def find_empty_err_files(logs_dir: Path) -> List[Path]:
    """Find all empty .err files in the logs directory."""
    empty_files = []
    
    for err_file in logs_dir.rglob("*.err"):
        if err_file.is_file() and err_file.stat().st_size == 0:
            empty_files.append(err_file)
    
    return empty_files


def clean_empty_err_logs(logs_dir: Path = LOGS_DIR, dry_run: bool = False) -> int:
    """
    Delete all empty .err files in the logs directory.
    
    Args:
        logs_dir: Path to the logs directory
        dry_run: If True, only print what would be deleted
        
    Returns:
        Number of files deleted (or would be deleted in dry-run mode)
    """
    if not logs_dir.exists():
        print(f"Error: Logs directory not found: {logs_dir}")
        return 0
    
    empty_files = find_empty_err_files(logs_dir)
    
    if not empty_files:
        print("No empty .err files found.")
        return 0
    
    print(f"Found {len(empty_files)} empty .err file(s):")
    
    for err_file in empty_files:
        relative_path = err_file.relative_to(logs_dir)
        if dry_run:
            print(f"  [DRY-RUN] Would delete: {relative_path}")
        else:
            print(f"  Deleting: {relative_path}")
            err_file.unlink()
    
    if dry_run:
        print(f"\nDry run complete. {len(empty_files)} file(s) would be deleted.")
    else:
        print(f"\nCleanup complete. {len(empty_files)} file(s) deleted.")
    
    return len(empty_files)


def main():
    dry_run = "--dry-run" in sys.argv or "-n" in sys.argv
    
    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        sys.exit(0)
    
    clean_empty_err_logs(dry_run=dry_run)


if __name__ == "__main__":
    main()
