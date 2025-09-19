import json
import pathlib
import jsonschema
BASE = pathlib.Path(__file__).parents[1]
def load(p): return json.loads(pathlib.Path(p).read_text())

def test_qb_result_rejects_infeasible():
    schema = load(BASE/"schemas/qb_optimization_result.schema.json")
    validator = jsonschema.Draft202012Validator(schema)
    bad = {
      "problem_id":"QB-bad-id with spaces",   # violates pattern
      "method":"QAOA","encoding":"QUBO","timestamp_utc":"2025-09-19T12:00:00Z",
      "decision":{}, "objective":{"value":-1}, "feasible": True,
      "context": {"flight_id": "FL123", "phase_id": "Cruise"}
    }
    try:
        validator.validate(bad)
        assert False, "Expected validation error"
    except jsonschema.ValidationError:
        pass