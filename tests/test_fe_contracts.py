import json, pathlib, jsonschema

BASE = pathlib.Path(__file__).parents[1]


def load(p):
    return json.loads(pathlib.Path(p).read_text())

def test_fe_contract_minimum():
    schema = load(BASE/"schemas/fe_federation_contract.schema.json")
    det_schema = load(BASE/"schemas/det_anchor.schema.json")
    
    # Create resolver with local schema store
    store = {schema['$id']: schema, det_schema['$id']: det_schema}
    resolver = jsonschema.RefResolver.from_schema(schema, store=store)
    validator = jsonschema.Draft202012Validator(schema, resolver=resolver)
    
    sample = {
      "federation_id":"FE-IBERIA-T2-CLUSTER",
      "policy":"SafetyFirst",
      "members":[{"aircraft_id":"EC-XYZ","role":"Leader","capabilities":["PowerShare","TaxiQueue"]},
                  {"aircraft_id":"EC-ABC","role":"Peer","capabilities":["PowerShare"]}],
      "quorum":{"size":2,"consensus":"Majority"},
      "coordination":{"topics":["PowerShare","TaxiQueue"],"period_ms":500,"latency_budget_ms":50},
      "security":{"auth":"mTLS","integrity":"SHA-256","replay_protection":True}
    }
    validator.validate(sample)