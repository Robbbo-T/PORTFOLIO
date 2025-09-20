#!/usr/bin/env python3
"""Apply canonical extension rename policies across the repository."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Sequence

# Allow running both as ``python tools/migrate_extensions.py`` and
# ``python -m tools.migrate_extensions``.
from .extensions_policy import (
    PolicyError,
    RenameOperation,
    ensure_policy_exists,
    load_policy,
    plan_renames,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Perform the rename instead of printing the plan",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Repository root to scan (defaults to current working directory)",
    )
    parser.add_argument(
        "--policy",
        type=Path,
        default=None,
        help="Override path to policy_extensions.yaml",
    )
    return parser.parse_args(argv)


def describe_plan(plan: Sequence[RenameOperation]) -> str:
    lines = ["Pending canonical renames:"]
    for op in plan:
        lines.append(f" - {op.source} -> {op.target}")
    lines.append("Run with --apply to perform the renames.")
    return "\n".join(lines)


def rename_with_case_handling(source: Path, target: Path) -> None:
    if source == target:
        return

    try:
        source.rename(target)
        return
    except OSError:
        if os.name != "nt" or source.parent != target.parent:
            raise

    # Windows is case-insensitive; renaming ``Foo.TXT`` -> ``Foo.txt`` requires
    # a two-step dance. Use a ``.renametmp`` suffix that is ignored by git.
    temp = _reserve_temp_path(source)
    try:
        source.rename(temp)
        temp.rename(target)
    except Exception:
        if temp.exists() and not source.exists():
            try:
                temp.rename(source)
            except Exception:
                pass
        raise


def _reserve_temp_path(source: Path) -> Path:
    base_name = source.name
    parent = source.parent
    counter = 0
    while True:
        suffix = ".renametmp" if counter == 0 else f".renametmp{counter}"
        candidate = parent / f"{base_name}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def apply_plan(plan: Sequence[RenameOperation]) -> None:
    for op in plan:
        if op.target.exists() and op.target != op.source:
            raise RuntimeError(
                f"Cannot rename '{op.source}' because target '{op.target}' already exists"
            )
        rename_with_case_handling(op.source, op.target)


def migrate(root: Path, policy_path: Path | None, apply: bool) -> int:
    try:
        real_policy = ensure_policy_exists(policy_path)
    except FileNotFoundError:
        print("No policy file found; nothing to do.")
        return 0

    try:
        policy = load_policy(real_policy)
    except PolicyError as exc:
        print(f"Failed to load policy: {exc}", file=sys.stderr)
        return 1

    plan = plan_renames(root, policy)
    if not plan:
        print("No changes needed.")
        return 0

    if not apply:
        print(describe_plan(plan))
        return 1

    apply_plan(plan)
    print(f"Renamed {len(plan)} file(s) to canonical extensions.")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.root or Path.cwd()
    root = root.resolve()
    return migrate(root, args.policy, args.apply)


if __name__ == "__main__":  # pragma: no cover - script entry point
    sys.exit(main())
