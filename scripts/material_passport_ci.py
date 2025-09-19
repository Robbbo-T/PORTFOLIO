#!/usr/bin/env python3
"""Validate blockchain material passport declarations.

The validator enforces repository acceptance criteria:
- passport hashes must match the canonical SHA-256 of each passport payload
- INSTALL lifecycle events must link to S1000D Issue 6 references
- CNT materials require residual catalyst metrics
- publishing is blocked when REACH compliance is false
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Mapping

import yaml

ALLOWED_TYPES = {"graphene", "cnt", "hybrid"}
VALID_STATUSES = {"ACTIVE", "RETIRED", "RECYCLED"}
REQUIRED_INSTALL_FIELDS = {"dmcode", "assembly_pnr"}


def load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} does not contain a mapping at the root")
    return data


def require_mapping(value: Any, path: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{path} must be a mapping")
    return value


def require_list(value: Any, path: str) -> List[Any]:
    if not isinstance(value, list):
        raise ValueError(f"{path} must be a list")
    return value


def require_str(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{path} must be a non-empty string")
    return value


def canonical_hash(passport: Mapping[str, Any]) -> str:
    """Compute the canonical SHA-256 hash of a passport payload."""

    snapshot = copy.deepcopy(passport)
    chain_anchor = snapshot.get("chain_anchor")
    if isinstance(chain_anchor, Mapping):
        chain_anchor.pop("passport_sha256", None)
    canonical = json.dumps(snapshot, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "0x" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def validate_passport(passport: Mapping[str, Any], index: int) -> Dict[str, Any]:
    mp_id = require_str(passport.get("mp_id"), f"passports[{index}].mp_id")

    material = require_mapping(passport.get("material"), f"passports[{index}].material")
    m_type = require_str(material.get("type"), f"passports[{index}].material.type").lower()
    if m_type not in ALLOWED_TYPES:
        raise ValueError(
            f"passports[{index}].material.type '{material.get('type')}' must be one of {sorted(ALLOWED_TYPES)}"
        )

    properties = require_mapping(passport.get("properties", {}), f"passports[{index}].properties")
    residuals = properties.get("residual_metal_ppm")
    if m_type == "cnt":
        residual_map = require_mapping(residuals, f"passports[{index}].properties.residual_metal_ppm")
        if not residual_map:
            raise ValueError(
                f"passports[{index}].properties.residual_metal_ppm must include catalyst ppm data for CNT materials"
            )
        for element, value in residual_map.items():
            if not isinstance(element, str) or not element.strip():
                raise ValueError(
                    f"passports[{index}].properties.residual_metal_ppm contains an invalid element key"
                )
            if not isinstance(value, (int, float)):
                raise ValueError(
                    f"passports[{index}].properties.residual_metal_ppm['{element}'] must be numeric"
                )

    safety = require_mapping(passport.get("safety_hazmat"), f"passports[{index}].safety_hazmat")
    reach = safety.get("reach_compliant")
    if reach is not True:
        raise ValueError(
            f"passports[{index}].safety_hazmat.reach_compliant must be true before publication"
        )

    lifecycle = require_list(passport.get("lifecycle"), f"passports[{index}].lifecycle")
    install_events = 0
    actors: List[str] = []
    for event_index, event in enumerate(lifecycle):
        event_map = require_mapping(event, f"passports[{index}].lifecycle[{event_index}]")
        kind = require_str(event_map.get("kind"), f"passports[{index}].lifecycle[{event_index}].kind")
        require_str(event_map.get("actor"), f"passports[{index}].lifecycle[{event_index}].actor")
        actors.append(event_map.get("actor", ""))
        tx = require_str(event_map.get("tx"), f"passports[{index}].lifecycle[{event_index}].tx")
        if not tx.startswith("0x"):
            raise ValueError(
                f"passports[{index}].lifecycle[{event_index}].tx must be a hex hash with 0x prefix"
            )
        if kind.upper() == "INSTALL":
            install_events += 1
            link = require_mapping(event_map.get("link"), f"passports[{index}].lifecycle[{event_index}].link")
            for field in REQUIRED_INSTALL_FIELDS:
                require_str(link.get(field), f"passports[{index}].lifecycle[{event_index}].link.{field}")

    if install_events == 0:
        raise ValueError(f"passports[{index}] must declare at least one INSTALL lifecycle event")

    chain_anchor = require_mapping(passport.get("chain_anchor"), f"passports[{index}].chain_anchor")
    chain = require_str(chain_anchor.get("chain"), f"passports[{index}].chain_anchor.chain")
    status = require_str(chain_anchor.get("status"), f"passports[{index}].chain_anchor.status").upper()
    if status not in VALID_STATUSES:
        raise ValueError(
            f"passports[{index}].chain_anchor.status '{chain_anchor.get('status')}' must be one of {sorted(VALID_STATUSES)}"
        )

    stored_hash = require_str(
        chain_anchor.get("passport_sha256"), f"passports[{index}].chain_anchor.passport_sha256"
    ).lower()
    if not stored_hash.startswith("0x") or len(stored_hash) != 66:
        raise ValueError(
            f"passports[{index}].chain_anchor.passport_sha256 must be a 0x-prefixed 64-byte hex digest"
        )

    computed_hash = canonical_hash(passport).lower()
    if stored_hash != computed_hash:
        raise ValueError(
            f"passports[{index}].chain_anchor.passport_sha256 mismatch: expected {computed_hash}, found {stored_hash}"
        )

    return {
        "mp_id": mp_id,
        "material_type": m_type,
        "status": status,
        "chain": chain,
        "install_events": install_events,
        "actors": actors,
    }


def validate_dataset(path: Path) -> List[Dict[str, Any]]:
    data = load_yaml(path)
    require_str(data.get("issue"), "root.issue")
    passports = require_list(data.get("passports"), "root.passports")

    summaries: List[Dict[str, Any]] = []
    seen_ids: set[str] = set()
    duplicate_ids: set[str] = set()
    for index, passport in enumerate(passports):
        passport_map = require_mapping(passport, f"passports[{index}]")
        summary = validate_passport(passport_map, index)
        mp_id = summary["mp_id"]
        if mp_id in seen_ids:
            duplicate_ids.add(mp_id)
        seen_ids.add(mp_id)
        summaries.append(summary)
    if duplicate_ids:
        raise ValueError(f"Duplicate passport identifiers detected: {', '.join(sorted(duplicate_ids))}")
    return summaries


def print_summary(results: List[Dict[str, Any]]) -> None:
    total = len(results)
    status_counts: Dict[str, int] = {}
    type_counts: Dict[str, int] = {}
    actors: Dict[str, int] = {}
    for result in results:
        status_counts[result["status"]] = status_counts.get(result["status"], 0) + 1
        type_counts[result["material_type"]] = type_counts.get(result["material_type"], 0) + 1
        for actor in result["actors"]:
            if actor:
                actors[actor] = actors.get(actor, 0) + 1

    print(f"Passports validated: {total}")
    print("  Status counts: " + ", ".join(f"{status}={count}" for status, count in sorted(status_counts.items())))
    print("  Material types: " + ", ".join(f"{typ}={count}" for typ, count in sorted(type_counts.items())))
    print("  Unique actors: " + str(len(actors)))


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate blockchain material passports")
    parser.add_argument("paths", nargs="*", type=Path, help="Passport YAML files to validate")
    args = parser.parse_args(argv)

    paths = args.paths or [Path("8-RESOURCES/MATERIALS/material_passports.yaml")]
    failures = False

    for path in paths:
        if not path.exists():
            print(f"ERROR: {path} does not exist")
            failures = True
            continue
        print(f"\n=== Validating {path} ===")
        try:
            results = validate_dataset(path)
        except yaml.YAMLError as exc:
            print(f"ERROR: Failed to parse YAML in {path}: {exc}")
            failures = True
            continue
        except ValueError as exc:
            print(f"ERROR: Validation error in {path}: {exc}")
            failures = True
            continue
        except Exception as exc:  # pylint: disable=broad-except
            print(f"ERROR: Unexpected error in {path}: {exc}")
            failures = True
            continue
        print_summary(results)

    return 1 if failures else 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
