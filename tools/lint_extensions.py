#!/usr/bin/env python3
"""Lint helper for canonical extension policy definitions."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running both as ``python tools/lint_extensions.py`` and
# ``python -m tools.lint_extensions``.
try:  # pragma: no cover - direct script execution
    from extensions_policy import (  # type: ignore[import-not-found]
        PolicyError as ToolsPolicyError,
        ensure_policy_exists as tools_ensure_policy_exists,
        load_policy as tools_load_policy,
    )
except ModuleNotFoundError:  # pragma: no cover - module execution
    from tools.extensions_policy import (  # type: ignore[import-not-found]
        PolicyError as ToolsPolicyError,
        ensure_policy_exists as tools_ensure_policy_exists,
        load_policy as tools_load_policy,
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--policy",
        type=Path,
        default=None,
        help="Optional path to policy_extensions.yaml (defaults to repository policy)",
    )
    return parser.parse_args(argv)


def lint(policy_path: Path | None = None) -> int:
    try:
        real_policy_path = tools_ensure_policy_exists(policy_path)
    except FileNotFoundError:
        print(
            "No policy file found; skipping canonical extension lint.",
            file=sys.stderr,
        )
        return 0

    try:
        policy = tools_load_policy(real_policy_path)
    except ToolsPolicyError as exc:
        print(f"Extension policy lint failed: {exc}", file=sys.stderr)
        return 1

    family_count = len(policy.families)
    alias_count = policy.alias_count
    print(
        f"Extension policy OK at {real_policy_path} — version {policy.version}, "
        f"{family_count} families, {alias_count} alias extensions tracked."
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    return lint(args.policy)


if __name__ == "__main__":  # pragma: no cover - script entry point
    sys.exit(main())
