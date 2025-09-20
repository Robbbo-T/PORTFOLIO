import subprocess
import sys
import pathlib


def run(cmd, *, cwd=None):
    result = subprocess.run(cmd, text=True, capture_output=True, cwd=cwd)
    return result.returncode, result.stdout + result.stderr


def test_canonical_verify_passes_when_no_plan(tmp_path):
    policy_dir = tmp_path / "7-GOVERNANCE" / "POLICY"
    policy_dir.mkdir(parents=True, exist_ok=True)
    (policy_dir / "policy_extensions.yaml").write_text(
        "version: 1\nfamilies: {}\n",
        encoding="utf-8",
    )

    tools_dir = tmp_path / "tools"
    tools_dir.mkdir(parents=True, exist_ok=True)

    repo_root = pathlib.Path(__file__).resolve().parent.parent
    for script_name in ["tools/extensions_policy.py", "tools/migrate_extensions.py"]:
        source = repo_root / script_name
        destination = tmp_path / script_name
        destination.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

    rc, output = run(
        [sys.executable, str(tmp_path / "tools/migrate_extensions.py")],
        cwd=tmp_path,
    )
    assert rc == 0
    assert "No changes needed" in output
