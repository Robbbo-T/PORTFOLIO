#!/usr/bin/env python3
"""Continuous integration checks for MAL controller manifests.

This helper validates manifest files against the MAL JSON schema and applies
additional deterministic control checks:

* Deadline and jitter conformance based on WCET budgets
* RBAC class sanity checks
* Safety-fence expression validation with safe evaluation
* Optional fence-case simulations declared in the manifest tests section

The script is intentionally deterministic so CI runs are reproducible.
"""
from __future__ import annotations

import argparse
import ast
import json
import operator
import random
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path
from functools import lru_cache
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

import yaml
from jsonschema import Draft202012Validator

SCHEMA_PATH = Path("8-RESOURCES/TEMPLATES/MAL/manifest.schema.json")
SAMPLE_MANIFEST = Path("8-RESOURCES/TEMPLATES/MAL/manifest.sample.yaml")
PASSPORT_DATASET = Path("8-RESOURCES/MATERIALS/material_passports.yaml")

ALLOWED_FUNC_MAP: Dict[str, Any] = {
    "abs": abs,
    "max": max,
    "min": min,
    "round": round,
}

@dataclass
class CycleSample:
    """Synthetic observation of a MAL scan cycle."""

    index: int
    duration_ms: float
    jitter_ms: float
    stage_durations: Mapping[str, float]


class SafeEvaluator(ast.NodeVisitor):
    """Safely evaluate guard expressions with a constrained AST visitor."""

    BIN_OPS: Mapping[type, Any] = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
    }
    UNARY_OPS: Mapping[type, Any] = {
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
        ast.Not: operator.not_,
    }
    BOOL_OPS: Mapping[type, Any] = {
        ast.And: all,
        ast.Or: any,
    }
    COMP_OPS: Mapping[type, Any] = {
        ast.Lt: operator.lt,
        ast.LtE: operator.le,
        ast.Gt: operator.gt,
        ast.GtE: operator.ge,
        ast.Eq: operator.eq,
        ast.NotEq: operator.ne,
    }

    def __init__(self, context: Mapping[str, Any]):
        super().__init__()
        self.context = context

    # pylint: disable=invalid-name,missing-function-docstring
    def visit_Expression(self, node: ast.Expression) -> Any:
        return self.visit(node.body)

    def visit_Name(self, node: ast.Name) -> Any:
        if node.id not in self.context:
            raise ValueError(f"Unknown symbol '{node.id}' in expression")
        return self.context[node.id]

    def visit_Constant(self, node: ast.Constant) -> Any:  # type: ignore[override]
        return node.value

    def visit_UnaryOp(self, node: ast.UnaryOp) -> Any:
        op_type = type(node.op)
        if op_type not in self.UNARY_OPS:
            raise ValueError(f"Unsupported unary operator: {op_type.__name__}")
        operand = self.visit(node.operand)
        return self.UNARY_OPS[op_type](operand)

    def visit_BinOp(self, node: ast.BinOp) -> Any:
        op_type = type(node.op)
        if op_type not in self.BIN_OPS:
            raise ValueError(f"Unsupported binary operator: {op_type.__name__}")
        left = self.visit(node.left)
        right = self.visit(node.right)
        return self.BIN_OPS[op_type](left, right)

    def visit_BoolOp(self, node: ast.BoolOp) -> Any:
        op_type = type(node.op)
        if op_type not in self.BOOL_OPS:
            raise ValueError(f"Unsupported boolean operator: {op_type.__name__}")
        values = [self.visit(value) for value in node.values]
        return self.BOOL_OPS[op_type](values)

    def visit_Compare(self, node: ast.Compare) -> Any:
        left_value = self.visit(node.left)
        result = True
        left = left_value
        for op, comparator in zip(node.ops, node.comparators):
            right = self.visit(comparator)
            op_type = type(op)
            if op_type not in self.COMP_OPS:
                raise ValueError(f"Unsupported comparison operator: {op_type.__name__}")
            comparator_result = self.COMP_OPS[op_type](left, right)
            result = result and comparator_result
            left = right
            if not result:
                break
        return result

    def visit_Call(self, node: ast.Call) -> Any:
        if node.keywords:
            raise ValueError("Keyword arguments are not allowed in guard expressions")
        func = self.visit(node.func)
        if func not in ALLOWED_FUNC_MAP.values():
            raise ValueError("Function calls must reference whitelisted helpers")
        args = [self.visit(arg) for arg in node.args]
        return func(*args)

    def generic_visit(self, node: ast.AST) -> Any:  # pylint: disable=signature-differs
        raise ValueError(f"Unsupported AST node: {type(node).__name__}")


def load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"YAML file {path} is not a mapping")
    return data


@lru_cache(maxsize=1)
def load_material_passport_index() -> Dict[str, Mapping[str, Any]]:
    """Load the material passport dataset into a lookup table."""

    if not PASSPORT_DATASET.exists():
        return {}
    dataset = load_yaml(PASSPORT_DATASET)
    passports = dataset.get("passports")
    if not isinstance(passports, list):
        raise ValueError("material_passports.yaml must expose a list under 'passports'")

    index: Dict[str, Mapping[str, Any]] = {}
    for entry in passports:
        if not isinstance(entry, Mapping):
            raise ValueError("Each passport entry must be a mapping")
        mp_id = entry.get("mp_id")
        if isinstance(mp_id, str) and mp_id.strip():
            index[mp_id] = entry
    return index


def gather_manifests(paths: Sequence[Path]) -> List[Path]:
    manifest_paths: List[Path] = []
    if paths:
        for candidate in paths:
            if candidate.is_dir():
                manifest_paths.extend(sorted(candidate.rglob("manifest.yaml")))
            elif candidate.is_file():
                manifest_paths.append(candidate)
    else:
        manifest_paths.extend(sorted(Path("2-DOMAINS-LEVELS").rglob("manifest.yaml")))
    manifest_paths = [path for path in manifest_paths if path.is_file()]
    if not manifest_paths and SAMPLE_MANIFEST.exists():
        manifest_paths.append(SAMPLE_MANIFEST)
    return manifest_paths


def _collect_variable_names(tree: ast.AST) -> List[str]:
    raw_names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    return sorted(name for name in raw_names if name not in ALLOWED_FUNC_MAP)


def _margin(value: Any) -> Optional[float]:
    if isinstance(value, (int, float)):
        magnitude = abs(float(value))
        return max(0.05 * (magnitude if magnitude else 1.0), 0.1)
    if isinstance(value, bool):
        return 1.0
    return None


def _alternate_string(value: Any) -> str:
    base = str(value)
    return f"__not_{base}__"


def _values_for_compare(op: ast.cmpop, constant: Any) -> Tuple[Optional[Any], Optional[Any]]:
    margin = _margin(constant)
    if isinstance(op, (ast.Lt, ast.LtE)):
        if margin is None:
            return None, None
        return constant - margin, constant + margin
    if isinstance(op, (ast.Gt, ast.GtE)):
        if margin is None:
            return None, None
        return constant + margin, constant - margin
    if isinstance(op, ast.Eq):
        if margin is None:
            return constant, _alternate_string(constant)
        return constant, constant + margin
    if isinstance(op, ast.NotEq):
        if margin is None:
            return _alternate_string(constant), constant
        return constant + margin, constant
    return None, None


def _invert_compare(op: ast.cmpop) -> ast.cmpop:
    mapping = {
        ast.Lt: ast.Gt,
        ast.LtE: ast.GtE,
        ast.Gt: ast.Lt,
        ast.GtE: ast.LtE,
        ast.Eq: ast.Eq,
        ast.NotEq: ast.NotEq,
    }
    new_cls = mapping.get(type(op))
    return new_cls() if new_cls else op


def build_contexts(tree: ast.AST, variable_names: Sequence[str]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    safe_ctx: Dict[str, Any] = {name: 0.0 for name in variable_names}
    trip_ctx: Dict[str, Any] = {name: 1.0 for name in variable_names}
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare) and len(node.ops) == 1:
            left = node.left
            right = node.comparators[0]
            op = node.ops[0]
            if isinstance(left, ast.Name) and isinstance(right, ast.Constant):
                safe_val, trip_val = _values_for_compare(op, right.value)
                if safe_val is not None:
                    safe_ctx[left.id] = safe_val
                if trip_val is not None:
                    trip_ctx[left.id] = trip_val
            elif isinstance(right, ast.Name) and isinstance(left, ast.Constant):
                safe_val, trip_val = _values_for_compare(_invert_compare(op), left.value)
                if safe_val is not None:
                    safe_ctx[right.id] = safe_val
                if trip_val is not None:
                    trip_ctx[right.id] = trip_val
    return safe_ctx, trip_ctx


def safe_eval(tree: ast.AST, context: Mapping[str, Any]) -> Any:
    evaluator = SafeEvaluator(context)
    return evaluator.visit(tree)  # type: ignore[arg-type]


def validate_cycle(manifest: Mapping[str, Any]) -> Dict[str, Any]:
    mal = manifest["mal"]
    cycle = mal["cycle"]
    tests = mal["tests"]
    budgets = tests["wcet_budget_ms"]

    period = float(cycle["period_ms"])
    deadline = float(cycle["deadline_ms"])
    jitter_max = float(cycle["jitter_max_ms"])

    if deadline > period:
        raise ValueError(f"Deadline {deadline}ms exceeds period {period}ms")
    if jitter_max > period:
        raise ValueError(f"Jitter limit {jitter_max}ms exceeds cycle period {period}ms")

    budget_values = [float(value) for value in budgets.values() if isinstance(value, (int, float))]
    budget_sum = sum(budget_values)
    if budget_sum > period + 1e-9:
        raise ValueError(
            f"Sum of WCET budgets {budget_sum:.3f}ms exceeds period {period}ms"
        )

    cycle_samples = simulate_cycle_trace(
        budgets,
        jitter_limit=jitter_max,
        deadline=deadline,
        sample_count=16,
    )
    max_duration = max(sample.duration_ms for sample in cycle_samples)
    max_jitter = max(sample.jitter_ms for sample in cycle_samples)
    if max_duration > deadline + 1e-6:
        raise ValueError(
            f"Synthetic cycle duration {max_duration:.3f}ms exceeds deadline {deadline}ms"
        )
    if max_jitter > jitter_max + 1e-6:
        raise ValueError(
            f"Synthetic jitter {max_jitter:.3f}ms exceeds bound {jitter_max}ms"
        )

    jitter_samples = tests.get("jitter_samples_ms", [])
    if jitter_samples:
        observed_max = max(float(item) for item in jitter_samples)
        if observed_max > jitter_max + 1e-6:
            raise ValueError(
                f"Recorded jitter sample {observed_max:.3f}ms exceeds bound {jitter_max}ms"
            )
        if len(jitter_samples) >= 3:
            jitter_p95 = statistics.quantiles(
                [float(item) for item in jitter_samples], n=20
            )[18]
        else:
            jitter_p95 = observed_max
    else:
        jitter_p95 = max_jitter

    return {
        "period_ms": period,
        "deadline_ms": deadline,
        "jitter_max_ms": jitter_max,
        "budget_sum_ms": budget_sum,
        "max_cycle_ms": max_duration,
        "max_jitter_ms": max_jitter,
        "jitter_p95_ms": jitter_p95,
        "samples": cycle_samples,
    }


def simulate_cycle_trace(
    budgets: Mapping[str, Any],
    *,
    jitter_limit: float,
    deadline: float,
    sample_count: int = 12,
) -> List[CycleSample]:
    rng = random.Random(42)
    numeric_items = [
        (stage, float(value))
        for stage, value in budgets.items()
        if isinstance(value, (int, float)) and float(value) > 0
    ]
    budget_total = sum(value for _, value in numeric_items)
    if budget_total <= 0:
        return [
            CycleSample(index=i, duration_ms=0.0, jitter_ms=0.0, stage_durations={})
            for i in range(sample_count)
        ]

    upper_bound = min(deadline, budget_total)
    base_total = min(upper_bound, budget_total * 0.85)
    previous_total = base_total
    samples: List[CycleSample] = []

    for index in range(sample_count):
        if index == 0:
            total = base_total
        else:
            delta = rng.uniform(-jitter_limit * 0.75, jitter_limit * 0.75)
            tentative = previous_total + delta
            total = max(0.0, min(tentative, upper_bound))
            if abs(total - previous_total) > jitter_limit:
                direction = 1.0 if tentative >= previous_total else -1.0
                total = previous_total + direction * jitter_limit * 0.75
                total = max(0.0, min(total, upper_bound))

        stage_durations: Dict[str, float] = {}
        if total <= 0:
            stage_durations = {stage: 0.0 for stage, _ in numeric_items}
        else:
            remaining = total
            for stage, value in numeric_items[:-1]:
                weight = value / budget_total
                stage_value = total * weight
                stage_durations[stage] = stage_value
                remaining -= stage_value
            last_stage = numeric_items[-1][0]
            stage_durations[last_stage] = max(0.0, remaining)

        jitter = 0.0 if index == 0 else abs(total - previous_total)
        samples.append(
            CycleSample(
                index=index,
                duration_ms=total,
                jitter_ms=jitter,
                stage_durations=stage_durations,
            )
        )
        previous_total = total

    return samples


def validate_rbac(rbac: Mapping[str, Any]) -> None:
    seen: set[str] = set()
    for idx, cls in enumerate(rbac.get("classes", [])):
        name = cls.get("name")
        if not name:
            raise ValueError(f"RBAC class at position {idx} is missing a name")
        if name in seen:
            raise ValueError(f"RBAC class '{name}' is duplicated")
        seen.add(name)
        permits = cls.get("permits", [])
        if not isinstance(permits, list) or not permits:
            raise ValueError(f"RBAC class '{name}' must declare at least one permit")


def validate_fences(manifest: Mapping[str, Any]) -> List[Dict[str, Any]]:
    mal = manifest["mal"]
    modes = set(mal["modes"])
    fence_cases: Dict[str, List[Mapping[str, Any]]] = {}
    for case in mal.get("tests", {}).get("fence_cases", []) or []:
        fence_cases.setdefault(case["name"], []).append(case)

    reports: List[Dict[str, Any]] = []
    for fence in mal["fences"]:
        name = fence["name"]
        expr = fence["expr"]
        trip_mode = fence["trip_mode"]
        if trip_mode not in modes:
            raise ValueError(f"Fence '{name}' references unknown trip mode '{trip_mode}'")
        tree = ast.parse(expr, mode="eval")
        variables = _collect_variable_names(tree)
        safe_ctx, trip_ctx = build_contexts(tree, variables)
        safe_value = bool(
            safe_eval(tree, {**ALLOWED_FUNC_MAP, **safe_ctx})
        )
        trip_value = bool(
            safe_eval(tree, {**ALLOWED_FUNC_MAP, **trip_ctx})
        )
        if not safe_value:
            raise ValueError(f"Fence '{name}' evaluates to false under safe synthetic context")
        if trip_value:
            raise ValueError(f"Fence '{name}' did not trip under synthetic context")

        case_results: List[str] = []
        for case in fence_cases.get(name, []):
            inputs = dict(case.get("inputs", {}))
            context = {**safe_ctx, **inputs}
            result = bool(safe_eval(tree, {**ALLOWED_FUNC_MAP, **context}))
            expected = bool(case.get("expected"))
            if result != expected:
                raise ValueError(
                    f"Fence '{name}' case inputs {inputs} expected {expected} but evaluated to {result}"
                )
            case_results.append(f"inputs={inputs} -> {result}")
        reports.append(
            {
                "name": name,
                "variables": variables,
                "safe_context": safe_ctx,
                "trip_context": trip_ctx,
                "cases_checked": case_results,
            }
        )
    return reports


def validate_material_passport_refs(mal: Mapping[str, Any]) -> Optional[List[Dict[str, str]]]:
    """Validate the material_passport_refs block when present."""

    refs = mal.get("material_passport_refs")
    if refs is None:
        return None
    if not isinstance(refs, list) or not refs:
        raise ValueError("material_passport_refs must be a non-empty list when provided")

    index = load_material_passport_index()
    summary: List[Dict[str, str]] = []
    missing: List[str] = []

    for position, item in enumerate(refs):
        if not isinstance(item, Mapping):
            raise ValueError(f"material_passport_refs[{position}] must be a mapping")
        mp_id = item.get("mp_id")
        usage = item.get("usage")
        if not isinstance(mp_id, str) or not mp_id.strip():
            raise ValueError(f"material_passport_refs[{position}].mp_id must be a non-empty string")
        if usage is not None and (not isinstance(usage, str) or not usage.strip()):
            raise ValueError(f"material_passport_refs[{position}].usage must be a non-empty string if provided")
        if index and mp_id not in index:
            missing.append(mp_id)
        summary.append({"mp_id": mp_id, "usage": usage or ""})

    if missing:
        raise ValueError(
            "material_passport_refs references unknown passport IDs: " + ", ".join(sorted(set(missing)))
        )

    return summary


def run_checks(manifest_path: Path, validator: Draft202012Validator) -> Dict[str, Any]:
    manifest = load_yaml(manifest_path)
    validator.validate(manifest)
    mal = manifest["mal"]

    cycle_report = validate_cycle(manifest)
    validate_rbac(mal["rbac"])
    fence_reports = validate_fences(manifest)
    passport_refs = validate_material_passport_refs(mal)

    telemetry_fields = mal["telemetry"]["deterministic_fields"]
    required_fields = {"cycle_id", "ts", "lat_ms", "jitter_ms", "mode", "fences_state", "det_anchor"}
    if not required_fields.issubset(set(telemetry_fields)):
        missing = required_fields.difference(telemetry_fields)
        raise ValueError(f"Telemetry is missing required deterministic fields: {sorted(missing)}")

    return {
        "path": manifest_path,
        "utcs_mi": mal["utcs_mi"],
        "cycle": cycle_report,
        "fences": fence_reports,
        "rbac_classes": len(mal["rbac"]["classes"]),
        "modes": mal["modes"],
        "material_passports": passport_refs,
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Validate MAL manifests and deterministic controls")
    parser.add_argument("paths", nargs="*", type=Path, help="Manifest files or directories to validate")
    parser.add_argument("--schema", type=Path, default=SCHEMA_PATH, help="Path to the MAL manifest JSON schema")
    parser.add_argument("--verbose", action="store_true", help="Print detailed cycle samples")
    args = parser.parse_args(argv)

    if not args.schema.exists():
        raise SystemExit(f"Schema not found at {args.schema}")

    with args.schema.open("r", encoding="utf-8") as handle:
        schema = json.load(handle)
    validator = Draft202012Validator(schema)

    manifest_paths = gather_manifests(args.paths)
    if not manifest_paths:
        print("No MAL manifest files found.")
        return 1

    failures = False
    for manifest_path in manifest_paths:
        print(f"\n=== Validating {manifest_path} ===")
        try:
            report = run_checks(manifest_path, validator)
        except Exception as exc:  # pylint: disable=broad-except
            failures = True
            print(f"ERROR: {exc}")
            continue

        cycle = report["cycle"]
        print(
            "Cycle: period={period_ms:.3f}ms deadline={deadline_ms:.3f}ms budget_sum={budget_sum_ms:.3f}ms".format(
                **cycle
            )
        )
        print(
            "        max_cycle={max_cycle_ms:.3f}ms max_jitter={max_jitter_ms:.3f}ms jitter_p95={jitter_p95_ms:.3f}ms".format(
                **cycle
            )
        )
        print(f"Modes: {', '.join(report['modes'])}")
        print(f"RBAC classes: {report['rbac_classes']}")
        passport_refs = report.get("material_passports") or []
        if passport_refs:
            joined = ", ".join(ref["mp_id"] for ref in passport_refs)
            print(f"Material passports referenced: {len(passport_refs)} ({joined})")
        for fence in report["fences"]:
            print(
                f"Fence '{fence['name']}': safe_ctx={fence['safe_context']} trip_ctx={fence['trip_context']}"
            )
            if args.verbose:
                for case_line in fence["cases_checked"]:
                    print(f"    case {case_line}")
        if args.verbose:
            for sample in cycle["samples"]:
                print(
                    f"    cycle {sample.index}: duration={sample.duration_ms:.3f}ms jitter={sample.jitter_ms:.3f}ms"
                )

    if failures:
        return 1
    print("\nAll MAL manifest checks passed.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
