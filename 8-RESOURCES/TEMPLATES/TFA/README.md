# TFA Template Assets

This directory now serves as an index for the Top Final Algorithm (TFA) scaffolding helpers located one level up under `8-RESOURCES/TEMPLATES/`.

## Contents

- `../tfa.schema.json` — JSON Schema (Draft 2020-12) describing the canonical tuple, artefact graph structure, and policy flags such as `strict_tfa_only` and `quantum_layers_required`.
- `../tfa.repo.example.json` — Minimal repository instance aligned with the portfolio’s 15 domains and the bridge layers (CB/QB/UE/FE/FWD/QS).
- `../tfa_tta_validator.py` — Reference validator that enforces V₁…V₅, computes Φ, performs greedy TTA coverage, checks STRICT TFA-ONLY paths, and verifies required quantum layers.
- `../makefile.snippets.mk` — Makefile include that wires `make scaffold` and `make check` to the validator and quantum-layer scaffolding helpers.
- `../mermaid/poset_T.md` — Mermaid diagram of the per-domain layer poset.
- `../mermaid/thread_hypergraph.md` — Mermaid “hypergraph” illustrating threading edges across artefacts.

## CI Integration

1. Validate repository manifests against `8-RESOURCES/TEMPLATES/tfa.schema.json` (see `.github/workflows/tfa-ci.yml`).
2. Run `python3 8-RESOURCES/TEMPLATES/tfa_tta_validator.py <repo.json> --fail-nonzero` to report Φ, greedy TTA coverage, STRICT TFA-ONLY violations, and quantum-layer presence.
3. Fail the job when `need_readme_nodes` declares a location without an associated README artefact.
4. Track Φ deltas and remediation priorities in programme governance reports.

Adjust Φ weightings (`alpha` … `epsilon`) as needed for programme priorities and update `R.quantum_layers_required` to tune layer expectations.
