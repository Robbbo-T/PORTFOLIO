#!/usr/bin/env python3
"""
Cleanup backup files that indicate merge artifacts or path drift.
This script helps clean up the repository after detecting path drift issues.
"""
import sys
from pathlib import Path

def main():
    """Clean up backup files and merge artifacts."""
    repo_root = Path(".")
    
    print("🧹 Cleaning up backup files and merge artifacts...")
    
    # Backup file patterns to remove
    backup_patterns = ["*.backup", "*.old", "*.orig", "*~"]
    
    removed_files = []
    
    for pattern in backup_patterns:
        matches = list(repo_root.rglob(pattern))
        for match in matches:
            if ".git" not in str(match):
                try:
                    match.unlink()
                    removed_files.append(str(match.relative_to(repo_root)))
                    print(f"   🗑️  Removed: {match.relative_to(repo_root)}")
                except Exception as e:
                    print(f"   ❌ Failed to remove {match}: {e}")
    
    if removed_files:
        print(f"\n✅ Cleanup complete! Removed {len(removed_files)} backup files:")
        for file in removed_files:
            print(f"   - {file}")
        print("\nRecommendation: Review the changes and commit the cleanup.")
    else:
        print("\n✅ No backup files found to clean up.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())