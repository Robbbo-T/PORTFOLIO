import json
import pathlib
import jsonschema
BASE = pathlib.Path(__file__).parents[1]
def load(p): return json.loads(pathlib.Path(p).read_text())

def test_orchestration_minimum():
    schema = load(BASE/"schemas/qb_orchestration.schema.json")
    sample = {
      "problem_class":"ModesSelect",
      "solvers":[{"name":"qaoa-16l","kind":"QAOA","budget_ms":40,"params":{"layers":16}}],
      "acceptance_policy":{"max_gap_pct":5.0,"must_satisfy":["surge_ok","vbus_ok"]},
      "fallback":"ClassicalSolve"
    }
    jsonschema.validate(instance=sample, schema=schema)