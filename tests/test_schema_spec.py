import json, pathlib
import jsonschema

BASE = pathlib.Path(__file__).parents[1]

def load(p):
    return json.loads(pathlib.Path(p).read_text())

def test_fadec_spec_schema():
    schema = load(BASE / "schemas/FADEC_X.spec.json")
    # ejemplo mínimo válido
    spec = {
        "hvdc": {"v_nom": 800, "v_min": 650, "v_max": 1050, "afdi_latency_ms": 2},
        "surge": {"s_min": 0.07, "trip_latency_ms": 50},
        "fuel_cell": {"p_cont_kw": 1500, "p_peak_kw": 3500, "peak_duration_s": 300, "ramp_kw_per_s": 300},
        "amb": {"reserve_energy_j": 1.0e6, "rundown_time_s": 60},
        "modes": ["NORMAL","ASSIST","DEGRADED"],
        "trip_table": [
            {"monitor":"AFDI","threshold":"TRIP","action":"isolate_bus_zone; fc_cmd=0; mode=DEGRADED","latency_ms":2}
        ]
    }
    jsonschema.validate(instance=spec, schema=schema)

def test_hazard_schema():
    schema = load(BASE / "schemas/arp4761.hazard.json")
    reg = {"hazards": [{
        "id":"HZ-001","title":"HVDC arc","severity":"Hazardous","initial_likelihood":"Possible",
        "controls":["AFDI","segregation"],"residual_risk":"Remote","verification":"bench AFDI"
    }]}
    jsonschema.validate(instance=reg, schema=schema)

def test_det_anchor_schema():
    schema = load(BASE / "schemas/det_anchor.schema.json")
    anchor = {
        "utcs_code":"UTCS-MI-AAP-KEM010.FADECX.EVT",
        "timestamp_utc":"2025-09-19T12:34:56Z",
        "event":{"mode":"ASSIST->ECO","reasons":["S<9%"],"limits":{"surge_idx":0.085,"v_bus":792}},
        "trace_refs":["telemetry://fadec-x/seg/123#t0..t1"],
        "content_hash_sha256":"e3f1e3f1e3f1e3f1e3f1e3f1e3f1e3f1e3f1e3f1e3f1e3f1e3f1e3f1e3f1e3f1",
        "signature":"DET:ed25519:ABCDEF"
    }
    jsonschema.validate(instance=anchor, schema=schema)