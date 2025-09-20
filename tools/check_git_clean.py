#!/usr/bin/env python3
"""Ensure the git working tree is clean before running destructive operations."""

from __future__ import annotations

import os
import subprocess
import sys


def main() -> int:
    force = os.getenv("FORCE", "0") == "1"
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=False,
    )
    dirty = bool(result.stdout.strip())

    if dirty and not force:
        print(
            "Working tree not clean. Commit/stash changes or set FORCE=1 to override.",
            file=sys.stderr,
        )
        return 1

    message = "Git tree clean (or FORCE=1)." if dirty and force else "Git tree clean."
    print(message)
    return 0


if __name__ == "__main__":  # pragma: no cover - script entry point
    sys.exit(main())
