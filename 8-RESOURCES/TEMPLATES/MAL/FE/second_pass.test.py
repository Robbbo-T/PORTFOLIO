"""Template test to verify MAL-FE idempotency.
Run MAL-FE twice with the same manifest; the second run must report no delta."""

from pathlib import Path

def apply_manifest(manifest: Path) -> dict:
    """Placeholder for MAL-FE apply logic.
    Returns a dict with a 'delta' key indicating if changes occurred."""
    return {"delta": 0}

def test_second_pass_no_delta(tmp_path: Path):
    manifest = tmp_path / "manifest.yaml"
    manifest.write_text(
        "actions:\n"
        "  - name: example_action\n"
        "    type: noop\n",
        encoding="utf-8"
    )
    first = apply_manifest(manifest)
    second = apply_manifest(manifest)
    assert second["delta"] == 0
