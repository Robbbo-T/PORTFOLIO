import json
import pathlib
import jsonschema
BASE = pathlib.Path(__file__).parents[1]
def load(p): return json.loads(pathlib.Path(p).read_text())

def test_rekey_on_membership_change():
    schema = load(BASE/"schemas/fe_coalition.schema.json")
    sample = {
      "federation_id":"FE-CLUSTER-01",
      "membership":[{"aircraft_id":"EC-AAA","role":"Leader","trust":0.9,"decay_per_min":0.01}],
      "events":[{"ts":"2025-09-19T12:00:00Z","type":"Join","reason":"new peer"}],
      "rekey_policy":{"interval_min":15,"on_event":True}
    }
    jsonschema.validate(instance=sample, schema=schema)