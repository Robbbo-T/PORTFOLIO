#!/usr/bin/env python3
"""Helpers for enforcing canonical file extensions policies."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Mapping, Sequence, Tuple

import yaml

DEFAULT_POLICY_PATH = Path("7-GOVERNANCE/POLICY/policy_extensions.yaml")
DEFAULT_IGNORE_DIRECTORIES = {
    ".git",
    ".hg",
    ".svn",
    ".tox",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "env",
    "envs",
    "node_modules",
    "__pycache__",
    "dist",
    "build",
    ".idea",
    ".vscode",
}


class PolicyError(RuntimeError):
    """Raised when the policy definition is invalid."""


@dataclass(frozen=True)
class ExtensionFamily:
    """Represents a canonical extension family defined in the policy."""

    name: str
    canonical: str
    aliases: Tuple[str, ...]


@dataclass(frozen=True)
class ExtensionPolicy:
    """Container for the parsed extension policy."""

    version: str | int
    path: Path
    families: Tuple[ExtensionFamily, ...]
    alias_map: Dict[str, str]
    ignore_directories: Tuple[str, ...]

    def canonical_for(self, extension: str) -> str | None:
        """Return the canonical extension for *extension* if one exists."""

        return self.alias_map.get(extension.casefold())

    @property
    def alias_count(self) -> int:
        """Return the total number of alias extensions tracked by the policy."""

        return sum(len(family.aliases) for family in self.families)

    @property
    def directories_to_ignore(self) -> set[str]:
        """Return the union of default and policy-defined ignore directories."""

        return {d.casefold() for d in DEFAULT_IGNORE_DIRECTORIES}.union(
            {d.casefold() for d in self.ignore_directories}
        )


def _normalise_extension(raw: str, *, allow_empty: bool = False) -> str:
    if raw is None:
        if allow_empty:
            return ""
        raise PolicyError("Extension entry cannot be null")

    extension = raw.strip()
    if not extension:
        if allow_empty:
            return ""
        raise PolicyError("Extension entry cannot be empty")

    if not extension.startswith("."):
        extension = f".{extension}"

    if len(extension) <= 1:
        raise PolicyError("Extensions must contain characters after the dot")

    return extension


def _extract_aliases(raw_aliases: object) -> List[str]:
    if raw_aliases is None:
        return []

    if isinstance(raw_aliases, str):
        candidates: Iterable[str] = [raw_aliases]
    elif isinstance(raw_aliases, Mapping):
        candidates = raw_aliases.keys()
    elif isinstance(raw_aliases, Sequence):
        candidates = raw_aliases
    else:
        raise PolicyError(
            "Alias collections must be a string, sequence, or mapping"
        )

    aliases: List[str] = []
    for alias in candidates:
        alias_normalised = _normalise_extension(str(alias))
        aliases.append(alias_normalised)
    return aliases


def load_policy(path: Path | None = None) -> ExtensionPolicy:
    """Load the extension policy from *path*.

    Raises :class:`FileNotFoundError` if the policy file is absent and
    :class:`PolicyError` if the content is malformed.
    """

    policy_path = path or DEFAULT_POLICY_PATH
    data = policy_path.read_text(encoding="utf-8")
    try:
        parsed = yaml.safe_load(data) or {}
    except yaml.YAMLError as exc:  # pragma: no cover - surfaced to caller
        raise PolicyError(f"Invalid YAML syntax in {policy_path}: {exc}") from exc

    if not isinstance(parsed, Mapping):
        raise PolicyError("Policy document must be a mapping")

    version = parsed.get("version", "1")
    families_raw = parsed.get("families", {})
    if not isinstance(families_raw, Mapping):
        raise PolicyError("'families' must be a mapping of family definitions")

    ignore_raw = parsed.get("ignore_directories", [])
    if isinstance(ignore_raw, str):
        ignore_iter: Iterable[str] = [ignore_raw]
    elif isinstance(ignore_raw, Sequence):
        ignore_iter = ignore_raw
    else:
        raise PolicyError("'ignore_directories' must be a sequence of strings")
    ignore_directories = tuple(str(entry).strip() for entry in ignore_iter if str(entry).strip())

    alias_map: Dict[str, str] = {}
    families: List[ExtensionFamily] = []
    canonical_seen: Dict[str, str] = {}

    for family_name, body in sorted(families_raw.items()):
        if not isinstance(body, Mapping):
            raise PolicyError(
                f"Family '{family_name}' must be defined as a mapping"
            )

        canonical_raw = body.get("canonical")
        if canonical_raw is None:
            raise PolicyError(
                f"Family '{family_name}' is missing required 'canonical' entry"
            )
        canonical = _normalise_extension(str(canonical_raw))
        canonical_key = canonical.casefold()
        if canonical_key in canonical_seen:
            other = canonical_seen[canonical_key]
            raise PolicyError(
                f"Canonical extension '{canonical}' reused in '{family_name}' and '{other}'"
            )
        canonical_seen[canonical_key] = family_name

        aliases = _extract_aliases(body.get("aliases") or body.get("variants") or body.get("synonyms"))

        normalised_aliases: List[str] = []
        for alias in aliases:
            alias_key = alias.casefold()
            if alias_key == canonical_key:
                continue
            existing = alias_map.get(alias_key)
            if existing and existing != canonical:
                raise PolicyError(
                    f"Alias '{alias}' in family '{family_name}' conflicts with canonical '{existing}'"
                )
            alias_map[alias_key] = canonical
            normalised_aliases.append(alias)

        families.append(
            ExtensionFamily(
                name=str(family_name),
                canonical=canonical,
                aliases=tuple(normalised_aliases),
            )
        )

    return ExtensionPolicy(
        version=version,
        path=policy_path,
        families=tuple(families),
        alias_map=alias_map,
        ignore_directories=tuple(ignore_directories),
    )


@dataclass(frozen=True)
class RenameOperation:
    """Represents a potential rename from an alias extension to the canonical one."""

    source: Path
    target: Path
    canonical_extension: str


def iter_candidate_files(root: Path, policy: ExtensionPolicy) -> Iterator[Path]:
    """Yield files below *root* that have an extension covered by the policy."""

    ignore = policy.directories_to_ignore
    for current_root, dirnames, filenames in os_walk(root):
        dirnames[:] = [d for d in dirnames if d.casefold() not in ignore]
        for filename in filenames:
            path = Path(current_root, filename)
            suffix = path.suffix
            if not suffix:
                continue
            suffix_cf = suffix.casefold()
            if policy.canonical_for(suffix) is None and suffix_cf not in policy.alias_map:
                continue
            yield path


def plan_renames(root: Path, policy: ExtensionPolicy) -> List[RenameOperation]:
    """Return the set of required rename operations under *root*."""

    plan: List[RenameOperation] = []
    seen_targets: set[Path] = set()
    for path in iter_candidate_files(root, policy):
        suffix = path.suffix
        canonical = policy.canonical_for(suffix)
        if canonical is None:
            continue
        target = path.with_suffix(canonical)
        if target == path:
            continue
        if target.exists():
            raise PolicyError(
                f"Cannot rename '{path}' to '{target}' because the target already exists"
            )
        if target in seen_targets:
            raise PolicyError(
                f"Canonical target collision detected for '{path}' -> '{target}'"
            )
        seen_targets.add(target)
        plan.append(
            RenameOperation(
                source=path,
                target=target,
                canonical_extension=canonical,
            )
        )

    plan.sort(key=lambda op: (str(op.source.parent), op.source.name))
    return plan


def os_walk(root: Path):
    """Wrapper around :func:`os.walk` to keep imports local."""

    import os

    return os.walk(root, followlinks=False)


def ensure_policy_exists(path: Path | None = None) -> Path:
    """Return the path to the policy file if it exists, else raise FileNotFoundError."""

    policy_path = path or DEFAULT_POLICY_PATH
    if not policy_path.exists():
        raise FileNotFoundError(policy_path)
    return policy_path


__all__ = [
    "DEFAULT_POLICY_PATH",
    "DEFAULT_IGNORE_DIRECTORIES",
    "ExtensionFamily",
    "ExtensionPolicy",
    "RenameOperation",
    "PolicyError",
    "ensure_policy_exists",
    "iter_candidate_files",
    "load_policy",
    "os_walk",
    "plan_renames",
]
