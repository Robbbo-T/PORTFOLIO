import json, hashlib

CANONICAL_SEP = ","

def canonical_json(obj):
    return json.dumps(obj, separators=(",",":"), sort_keys=True)

def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()

def test_qs_hash_replay():
    payload = {
        "utcs_code":"UTCS-MI-AAP-KEM010.FADECX.EVT",
        "timestamp_utc":"2025-09-19T12:34:56Z",
        "event":{"mode":"ASSIST->ECO","reasons":["S<9%"],"limits":{"surge_idx":0.085,"v_bus":792}},
        "trace_refs":["telemetry://fadec-x/seg/123#t0..t1"],
    }
    cj = canonical_json(payload)
    h = sha256_hex(cj)
    assert len(h) == 64