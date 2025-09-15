# TFA Template Assets

This folder contains self-contained resources for validating and visualising Top Final Algorithm (TFA) repositories.

## Contents

- `tfa.schema.json` — JSON Schema (Draft 2020-12) describing the canonical 7-tuple structure plus structural (`E`) and threading (`X`) graphs.
- `tfa_tta_validator.py` — reference Python helper that evaluates validation rules V1–V5, computes Φ scores, and produces a greedy traceability test set (TTA) with coverage reports.
- `poset_T.mmd` — Mermaid diagram expressing the per-domain partial order over layers.
- `hypergraph_threads.mmd` — Mermaid “hypergraph” using hub nodes to emulate threading edges across artifacts.

## CI Integration

1. Validate repository manifests against `tfa.schema.json`.
2. Run `python3 8-RESOURCES/TEMPLATES/TFA/tfa_tta_validator.py` (or import the module) inside the CI pipeline. Enforce ΔΦ < 0 and require full coverage across `T`.
3. Fail the job when `need_readme_nodes` declares a location without an associated README artifact.
4. Export hashes, identifiers, and traceability anchors to the DET/QAUDIT ledger for auditable evidence chains.

Adjust Φ weightings (`alpha` … `epsilon`) as needed for programme priorities.
