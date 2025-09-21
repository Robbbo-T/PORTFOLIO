#!/usr/bin/env python3
"""List all git stashes in the repository."""

from __future__ import annotations

import subprocess
import sys


def main() -> int:
    """List all git stashes and return appropriate exit code."""
    try:
        result = subprocess.run(
            ["git", "stash", "list"],
            capture_output=True,
            text=True,
            check=False,
        )
        
        if result.returncode != 0:
            print("Error: Failed to list git stashes.", file=sys.stderr)
            if result.stderr:
                print(f"Git error: {result.stderr.strip()}", file=sys.stderr)
            return 1
        
        stashes = result.stdout.strip()
        if stashes:
            print("Git stashes:")
            print(stashes)
            # Count the number of stashes
            stash_count = len(stashes.split('\n'))
            print(f"\nTotal: {stash_count} stash(es)")
        else:
            print("No git stashes found.")
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":  # pragma: no cover - script entry point
    sys.exit(main())