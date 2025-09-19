import json, pathlib, jsonschema

BASE = pathlib.Path(__file__).parents[1]


def load(p):
    return json.loads(pathlib.Path(p).read_text())

def test_qb_result_minimum():
    schema = load(BASE/"schemas/qb_optimization_result.schema.json")
    det_schema = load(BASE/"schemas/det_anchor.schema.json")
    
    # Create resolver with local schema store
    store = {schema['$id']: schema, det_schema['$id']: det_schema}
    resolver = jsonschema.RefResolver.from_schema(schema, store=store)
    validator = jsonschema.Draft202012Validator(schema, resolver=resolver)
    
    sample = {
      "problem_id":"QB-KEM010_POWER_MODES",
      "method":"QAOA",
      "encoding":"QUBO",
      "timestamp_utc":"2025-09-19T12:00:00Z",
      "decision":{"ASSIST":True,"ECO":False,"vafn_area":1.12},
      "objective":{"value":-123.4,"units":"kJ","gap_pct":2.5},
      "constraints":{"surge_idx":0.09,"v_bus_ok":True},
      "feasible":True,
      "classical_check":{"accepted":True,"violations":[]},
      "trace_refs":["qb://runs/42"],
      "det_anchor": {
        "utcs_code":"UTCS-MI-AAP-KEM_010.QB.EVT",
        "timestamp_utc":"2025-09-19T12:00:00Z",
        "event":{"mode":"QB_SOLN","reasons":["gap<3%"],"limits":{"surge_idx":0.09}},
        "trace_refs":["qb://runs/42#log"],
        "content_hash_sha256":"e3f1e3f1e3f1e3f1e3f1e3f1e3f1e3f1e3f1e3f1e3f1e3f1e3f1e3f1e3f1e3f1",
        "signature":"DET:ed25519:ABCDEF"
      }
    }
    validator.validate(sample)