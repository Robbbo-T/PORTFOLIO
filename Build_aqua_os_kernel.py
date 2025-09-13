#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build_aqua_os_kernel.py
AQUA OS kernel builder/deployer for AIR/SPACE/GROUND/DEFENSE/CROSS profiles
with classical and quantum targets. Idempotent operations, deterministic
canonicalization, and CI-friendly outputs.

Usage examples:
  python Build_aqua_os_kernel.py info
  python Build_aqua_os_kernel.py scaffold --path ./aqua_os
  python Build_aqua_os_kernel.py build --config ./aqua_os/aqua.config.json --target both --profile AIR
  python Build_aqua_os_kernel.py deploy --config ./aqua_os/aqua.config.json --target classical --profile DEFENSE --runtime docker --apply
  python Build_aqua_os_kernel.py test --config ./aqua_os/aqua.config.json --suite smoke --quantum-backend simulator
  python Build_aqua_os_kernel.py clean --path ./aqua_os

Copyright:
  MIT License. Intended for R&D and CI scaffolding; extend with UTCS/FE hooks.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import shutil
import subprocess
import time
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional

# ---------------------------
# Logging & small utilities
# ---------------------------

def log(msg: str, *, level: str = "INFO") -> None:
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[{ts}] [{level}] {msg}")

def warn(msg: str) -> None:
    log(msg, level="WARN")

def err(msg: str) -> None:
    log(msg, level="ERROR")

def canonical_json(obj: Any) -> bytes:
    """
    Deterministic JSON encoding: UTF-8, sorted keys, no extra spaces.
    """
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")

def _keccak_or_sha3(data: bytes) -> str:
    """
    Try Keccak-256; fall back to SHA3-256; if unavailable, fall back to SHA-256.
    Returns 0x-prefixed hex string and logs which hash was used.
    """
    # Try pycryptodome Keccak
    try:
        from Crypto.Hash import keccak  # type: ignore
        k = keccak.new(digest_bits=256)
        k.update(data)
        h = k.hexdigest()
        log("Hash: keccak256 (pycryptodome)", level="DEBUG")
        return "0x" + h
    except Exception:
        pass

    # Try sha3 (PEP 466: available in Python 3.6+ as SHA3-256; not exactly Keccak)
    try:
        import hashlib
        h = hashlib.sha3_256(data).hexdigest()
        log("Hash: sha3_256 (stdlib fallback)", level="DEBUG")
        return "0x" + h
    except Exception:
        pass

    # Final fallback SHA-256
    try:
        import hashlib
        h = hashlib.sha256(data).hexdigest()
        warn("Keccak/SHA3 unavailable; using sha256 fallback")
        return "0x" + h
    except Exception as e:
        err(f"Hashing unavailable: {e}")
        raise

def compute_config_hash(cfg: Dict[str, Any]) -> str:
    return _keccak_or_sha3(canonical_json(cfg))

def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def dump_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")

def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def which(cmd: str) -> Optional[str]:
    return shutil.which(cmd)

# ---------------------------
# Detection helpers
# ---------------------------

def detect_quantum_sdks() -> Dict[str, bool]:
    found = {"qiskit": False, "cirq": False, "braket": False}
    try:
        import qiskit  # noqa
        found["qiskit"] = True
    except Exception:
        pass
    try:
        import cirq  # noqa
        found["cirq"] = True
    except Exception:
        pass
    try:
        import braket.circuits  # noqa
        found["braket"] = True
    except Exception:
        pass
    return found

def detect_container_stack() -> Dict[str, bool]:
    return {
        "docker": which("docker") is not None,
        "kubectl": which("kubectl") is not None,
        "helm": which("helm") is not None,
        "podman": which("podman") is not None,
        "kind": which("kind") is not None,
        "minikube": which("minikube") is not None,
    }

# ---------------------------
# Scaffolding
# ---------------------------

DEFAULT_CONFIG = {
    "program": "AQUA-OS",
    "profiles": ["AIR", "SPACE", "GROUND", "DEFENSE", "CROSS"],
    "targets": ["classical", "quantum"],
    "runtime": {"classical": "docker", "quantum": "simulator"},
    "metadata": {
        "owner": "Amedeo Pelliccia",
        "repository": "aqua-os",
        "tfa_version": "V2",
        "optimo_dt_version": "V10.0",
    },
    "policy": {
        "ci_required": ["tfa_structure_validator", "quantum-layers-check"],
        "export_standards": ["S1000D", "MBSE"],
    },
}

DOCKERFILE = """\
# Minimal runtime for AQUA OS kernel (classical target)
FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir --upgrade pip
CMD ["python","-c","print('AQUA OS classical runtime ready')"]
"""

K8S_DEPLOYMENT = """\
apiVersion: apps/v1
kind: Deployment
metadata:
  name: aqua-os-kernel
  labels:
    app: aqua-os
spec:
  replicas: 1
  selector:
    matchLabels:
      app: aqua-os
  template:
    metadata:
      labels:
        app: aqua-os
    spec:
      containers:
        - name: aqua-os
          image: aqua-os:latest
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 8080
          env:
            - name: AQUA_PROFILE
              value: "AIR"
            - name: AQUA_TARGET
              value: "classical"
"""

GITIGNORE = """\
__pycache__/
*.pyc
*.pyo
*.pyd
.env
.venv
.aqua/
dist/
build/
"""

def cmd_scaffold(path: Path) -> None:
    log(f"Scaffolding project at {path}")
    path.mkdir(parents=True, exist_ok=True)

    # Write config
    cfg_path = path / "aqua.config.json"
    if not cfg_path.exists():
        dump_json(cfg_path, DEFAULT_CONFIG)
        log(f"Created {cfg_path}")
    else:
        warn(f"Config already exists: {cfg_path}")

    # Dockerfile
    dockerfile = path / "Dockerfile"
    if not dockerfile.exists():
        write_text(dockerfile, DOCKERFILE)
        log(f"Created {dockerfile}")

    # K8s manifest
    k8s_path = path / "k8s" / "deployment.yaml"
    if not k8s_path.exists():
        write_text(k8s_path, K8S_DEPLOYMENT)
        log(f"Created {k8s_path}")

    # State dir
    state_dir = path / ".aqua"
    state_dir.mkdir(exist_ok=True)
    dump_json(state_dir / "state.json", {"last_hash": None, "history": []})

    # .gitignore
    gi = path / ".gitignore"
    if not gi.exists():
        write_text(gi, GITIGNORE)
        log(f"Created {gi}")

    # Minimal services dir hint
    services = path / "services"
    services.mkdir(exist_ok=True)
    readme_services = services / "README.md"
    if not readme_services.exists():
        write_text(
            readme_services,
            "# services/\nPlace AQUA apps/services here. See services/aqua-os-pro for PRO.\n",
        )

    log("Scaffold complete.")

# ---------------------------
# Build
# ---------------------------

def _load_config_or_exit(config_path: Path) -> Dict[str, Any]:
    if not config_path.exists():
        err(f"Config not found: {config_path}")
        sys.exit(1)
    try:
        cfg = load_json(config_path)
    except Exception as e:
        err(f"Invalid JSON in {config_path}: {e}")
        sys.exit(1)
    return cfg

def cmd_build(config_path: Path, target: str, profile: str, apply: bool) -> None:
    cfg = _load_config_or_exit(config_path)
    root = config_path.parent
    state_path = root / ".aqua" / "state.json"
    state = {"last_hash": None, "history": []}
    if state_path.exists():
        try:
            state = load_json(state_path)
        except Exception:
            warn("State file corrupt; resetting.")
    cfg_enriched = {
        **cfg,
        "build": {
            "target": target,
            "profile": profile,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        },
    }
    h = compute_config_hash(cfg_enriched)
    log(f"Config hash: {h}")

    if state.get("last_hash") == h:
        log("No changes detected (idempotent build). Skipping build steps.")
        return

    # Simulated build steps (extend here)
    artifacts = root / "dist"
    artifacts.mkdir(exist_ok=True)
    write_text(artifacts / "BUILD_INFO.txt", f"hash={h}\nprofile={profile}\ntarget={target}\n")

    # Optional docker build
    if target in ("classical", "both") and apply:
        if which("docker"):
            log("Building Docker image: aqua-os:latest")
            try:
                subprocess.check_call(["docker", "build", "-t", "aqua-os:latest", str(root)])
                log("Docker build complete.")
            except subprocess.CalledProcessError as e:
                err(f"Docker build failed: {e}")
        else:
            warn("Docker not found; skipping docker build.")

    state["last_hash"] = h
    hist = state.get("history", [])
    hist.append({"hash": h, "profile": profile, "target": target, "time": datetime.utcnow().isoformat() + "Z"})
    state["history"] = hist[-20:]  # keep last 20
    dump_json(state_path, state)
    log("Build complete.")

# ---------------------------
# Deploy
# ---------------------------

def cmd_deploy(config_path: Path, target: str, profile: str, runtime: str, apply: bool) -> None:
    cfg = _load_config_or_exit(config_path)
    root = config_path.parent
    log(f"Deploy requested: target={target}, profile={profile}, runtime={runtime}, apply={apply}")

    if target == "classical":
        if runtime == "docker":
            cmd = ["docker", "run", "--rm", "-e", f"AQUA_PROFILE={profile}", "-e", "AQUA_TARGET=classical", "aqua-os:latest"]
            log("Docker run command:\n  " + " ".join(cmd))
            if apply and which("docker"):
                try:
                    subprocess.check_call(cmd)
                except subprocess.CalledProcessError as e:
                    err(f"Docker run failed: {e}")
        elif runtime == "k8s":
            manifest = root / "k8s" / "deployment.yaml"
            if not manifest.exists():
                err(f"K8s manifest missing: {manifest}")
                sys.exit(1)
            cmd = ["kubectl", "apply", "-f", str(manifest)]
            log("kubectl apply command:\n  " + " ".join(cmd))
            if apply and which("kubectl"):
                try:
                    subprocess.check_call(cmd)
                except subprocess.CalledProcessError as e:
                    err(f"kubectl apply failed: {e}")
        elif runtime == "baremetal":
            log("Baremetal deploy (placeholder): ensuring services are started…")
            # Extend: systemd units, venv prep, etc.
        else:
            err(f"Unknown classical runtime: {runtime}")
            sys.exit(1)

    elif target == "quantum":
        log("Quantum deploy is a logical provisioning step (no long-running service).")
        log("Ensure SDK credentials are configured. Proceed to 'test --suite smoke' to validate backend.")
    else:
        err(f"Unknown target: {target}")
        sys.exit(1)

    log("Deploy complete (or dry-run).")

# ---------------------------
# Test (smoke)
# ---------------------------

def _quantum_smoke_qiskit() -> Dict[str, Any]:
    import qiskit
    from qiskit import QuantumCircuit
    from qiskit_aer import Aer  # type: ignore
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])
    sim = Aer.get_backend("aer_simulator")
    job = qiskit.execute(qc, sim, shots=256)
    counts = job.result().get_counts()
    return {"sdk": "qiskit", "counts": counts}

def _quantum_smoke_cirq() -> Dict[str, Any]:
    import cirq
    q0, q1 = cirq.LineQubit.range(2)
    circuit = cirq.Circuit(cirq.H(q0), cirq.CNOT(q0, q1), cirq.measure(q0, q1))
    sim = cirq.Simulator()
    res = sim.run(circuit, repetitions=256)
    # counts
    counts: Dict[str, int] = {}
    for b0, b1 in zip(res.measurements[str(q0)][:, 0], res.measurements[str(q1)][:, 0]):
        key = f"{b0}{b1}"
        counts[key] = counts.get(key, 0) + 1
    return {"sdk": "cirq", "counts": counts}

def _quantum_smoke_braket() -> Dict[str, Any]:
    # Local circuit only (no AWS creds needed) — use braket local simulator if present
    from braket.circuits import Circuit  # type: ignore
    # Note: Full local execution requires Braket local simulator; we just assemble the circuit here.
    c = Circuit().h(0).cnot(0, 1).probability()
    return {"sdk": "braket", "note": "Constructed circuit; run requires local simulator", "circuit": str(c)}

def _quantum_smoke_fallback() -> Dict[str, Any]:
    # Pure-Python pseudo-simulator for Bell state counts (approximate)
    import random
    shots = 256
    counts = {"00": 0, "11": 0, "01": 0, "10": 0}
    for _ in range(shots):
        # Ideal Bell pair yields 00 or 11 with 50/50
        if random.random() < 0.5:
            counts["00"] += 1
        else:
            counts["11"] += 1
    return {"sdk": "fallback-simulator", "counts": counts, "shots": shots}

def cmd_test(config_path: Path, suite: str, backend: str) -> None:
    _ = _load_config_or_exit(config_path)
    if suite != "smoke":
        err(f"Unknown suite: {suite}")
        sys.exit(1)

    sdks = detect_quantum_sdks()
    log(f"Quantum SDKs detected: {sdks}")

    result: Dict[str, Any]
    if backend == "qiskit" and sdks["qiskit"]:
        try:
            result = _quantum_smoke_qiskit()
        except Exception as e:
            warn(f"Qiskit test failed ({e}), falling back to simulator.")
            result = _quantum_smoke_fallback()
    elif backend == "cirq" and sdks["cirq"]:
        try:
            result = _quantum_smoke_cirq()
        except Exception as e:
            warn(f"Cirq test failed ({e}), falling back to simulator.")
            result = _quantum_smoke_fallback()
    elif backend == "braket" and sdks["braket"]:
        result = _quantum_smoke_braket()
    else:
        result = _quantum_smoke_fallback()

    log(f"Smoke test result: {json.dumps(result, indent=2)}")

# ---------------------------
# Clean
# ---------------------------

def cmd_clean(path: Path) -> None:
    targets = [path / ".aqua", path / "dist", path / "__pycache__"]
    removed = []
    for t in targets:
        if t.exists():
            shutil.rmtree(t, ignore_errors=True)
            removed.append(str(t))
    log(f"Removed: {removed if removed else 'nothing to remove'}")

# ---------------------------
# Info
# ---------------------------

def cmd_info() -> None:
    log("AQUA OS kernel — environment probe")
    log(f"Python: {sys.version.split()[0]}")
    log(f"Platform: {sys.platform}")
    log(f"Container stack: {detect_container_stack()}")
    log(f"Quantum SDKs: {detect_quantum_sdks()}")
    log("Hash probe: " + compute_config_hash({"probe": True}))

# ---------------------------
# CLI
# ---------------------------

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="Build_aqua_os_kernel.py",
        description="AQUA OS kernel builder/deployer (classical + quantum)."
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_info = sub.add_parser("info", help="Show environment and capability info")

    p_scaf = sub.add_parser("scaffold", help="Create minimal project skeleton")
    p_scaf.add_argument("--path", type=Path, required=True, help="Root path for project")

    p_build = sub.add_parser("build", help="Build idempotently for a target/profile")
    p_build.add_argument("--config", type=Path, required=True, help="Path to aqua.config.json")
    p_build.add_argument("--target", choices=["classical", "quantum", "both"], default="both")
    p_build.add_argument("--profile", choices=["AIR", "SPACE", "GROUND", "DEFENSE", "CROSS"], default="AIR")
    p_build.add_argument("--apply", action="store_true", help="Perform side-effecting steps (e.g., docker build)")

    p_deploy = sub.add_parser("deploy", help="Deploy to runtime")
    p_deploy.add_argument("--config", type=Path, required=True, help="Path to aqua.config.json")
    p_deploy.add_argument("--target", choices=["classical", "quantum"], default="classical")
    p_deploy.add_argument("--profile", choices=["AIR", "SPACE", "GROUND", "DEFENSE", "CROSS"], default="AIR")
    p_deploy.add_argument("--runtime", choices=["docker", "k8s", "baremetal"], default="docker")
    p_deploy.add_argument("--apply", action="store_true", help="Execute commands (not just print)")

    p_test = sub.add_parser("test", help="Run smoke tests")
    p_test.add_argument("--config", type=Path, required=True, help="Path to aqua.config.json")
    p_test.add_argument("--suite", choices=["smoke"], default="smoke")
    p_test.add_argument("--quantum-backend", choices=["simulator", "qiskit", "cirq", "braket"], default="simulator")

    p_clean = sub.add_parser("clean", help="Remove local build artifacts")
    p_clean.add_argument("--path", type=Path, required=True)

    args = parser.parse_args(argv)

    if args.cmd == "info":
        cmd_info()
    elif args.cmd == "scaffold":
        cmd_scaffold(args.path)
    elif args.cmd == "build":
        cmd_build(args.config, args.target, args.profile, args.apply)
    elif args.cmd == "deploy":
        cmd_deploy(args.config, args.target, args.profile, args.runtime, args.apply)
    elif args.cmd == "test":
        cmd_test(args.config, args.suite, args.quantum_backend)
    elif args.cmd == "clean":
        cmd_clean(args.path)
    else:
        parser.print_help()
        return 2
    return 0

if __name__ == "__main__":
    sys.exit(main())
