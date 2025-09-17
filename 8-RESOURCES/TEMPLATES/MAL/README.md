# MAL (Main Application Layer) Templates

MAL templates provide horizontal bridge services that are shared across all domains and programs.

## Structure

Each MAL corresponds to a TFA layer and provides shared services:

- `CB/` - Classical Bit services
- `QB/` - Qubit services
- `UE/` - Unit Element services
- `FE/` - Federation Entanglement services
- `FWD/` - Forward Wave Dynamics services
- `QS/` - Quantum State services

## Key Characteristics

- **Horizontal reuse**: MAL services are shared across all domains
- **Bridge functionality**: Provide interfaces between layers
- **Standard contracts**: Common APIs and data formats
- **Policy enforcement**: Security, compliance, and governance

## Usage

1. Select the MAL services needed for your program
2. Configure the service parameters for your use case
3. Wire MAL services to your domain MAP
4. Test the integrated MAP + MAL configuration

See the main 8-RESOURCES README and Quantum-Classical Bridge documentation for detailed usage.

## Deterministic Validation Assets

- `manifest.schema.json` — JSON Schema contract for MAL controller manifests.
- `manifest.sample.yaml` — Reference manifest illustrating cycle budgets, RBAC classes, and fence cases.
- `tests/hil_sil_test_template.py` — Base harness and assertions for MAL HIL/SIL determinism checks.
- `scripts/mal_ci_checks.py` — Repository-wide helper that validates manifests, budgets, and safety fences.

The schema and helper script are exercised by the `mal-ci.yml` GitHub Actions workflow to guarantee manifests remain compliant.
