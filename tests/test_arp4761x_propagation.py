import json, pathlib, jsonschema

BASE = pathlib.Path(__file__).parents[1]


def load(p):
    return json.loads(pathlib.Path(p).read_text())

def test_cross_domain_minimum():
    schema = load(BASE/"schemas/arp4761x.cross_domain.json")
    sample = {
      "scenarios": [{
        "id":"CDS-001",
        "title":"PPP leak → EDI HV bay → LCC dispatch delay",
        "initiators":["HZ-002"],
        "domains":["PPP","EDI","LCC"],
        "paths":[{"from":"PPP","to":"EDI","mechanism":"H2 plume near HVDC","latency_ms":2000,"attenuation":0.3},
                  {"from":"EDI","to":"LCC","mechanism":"power shed → gate return","latency_ms":60000,"attenuation":0.8}],
        "cross_controls":["vent routing","AFDI isolation","taxi queue priority"]
      }]
    }
    jsonschema.validate(instance=sample, schema=schema)