#!/usr/bin/env python3
import json, sys, hashlib
from jsonschema import validate, Draft202012Validator

def keccak(data: bytes) -> str:
    """Compute Keccak-256 hash using Python's built-in hashlib"""
    k = hashlib.sha3_256()
    k.update(data)
    return "0x" + k.hexdigest()

def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")

def load_json(path): 
    with open(path, "r", encoding="utf-8") as f: 
        return json.load(f)

# Minimal smoke tests
geo = {"name":"wing","units":"SI","reference":{"S":124.0,"c_ref":3.5,"b":35.0},"surfaces":[{"id":"w1","airfoil":"NACA2412","span":17.5,"taper":0.3,"sweep_deg":28.0,"dihedral_deg":5.0}]}
lc  = {"id":"T-001","Mach":0.78,"AoA_rad":0.035,"altitude_m":11000,"mass_kg":65000}
perf= {"artifact_id":"AAA-BL-001","CL":0.52,"CD":0.028,"CM":-0.03,"Mach":0.78,"AoA_rad":0.035}

schemas = {
  "geo":"schemas/aerodynamic_surface.schema.json",
  "load":"schemas/load_case.schema.json",
  "perf":"schemas/performance_summary.schema.json"
}

for key, path in schemas.items():
    sch = load_json(path)
    data = {"geo":geo,"load":lc,"perf":perf}[key]
    Draft202012Validator(sch).validate(data)

print("✅ Schemas valid.")
h = keccak(canonical(perf))
print("canonical_hash:", h)