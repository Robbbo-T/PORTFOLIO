import re, json, pathlib, jsonschema
BASE = pathlib.Path(__file__).parents[1]
def load(p): return json.loads(pathlib.Path(p).read_text())
STL_RE = re.compile(r'^[GFU]\[[0-9]+(ms|s|m),(?:[0-9]+(ms|s|m)|\+inf)\]\(.+\)$')

def test_stl_guards_look_reasonable():
    schema = load(BASE/"schemas/arp4761x.temporal.json")
    sample = {
      "nodes":[{"id":"n1","domain":"PPP","state":"Nominal"},{"id":"n2","domain":"EDI","state":"Derated"}],
      "edges":[{"from":"n1","to":"n2","guard_stl":"G[0s,3s](boiloff_rate>r*)"}]
    }
    jsonschema.validate(instance=sample, schema=schema)
    for e in sample["edges"]:
        assert STL_RE.match(e["guard_stl"]), f"Bad STL guard: {e['guard_stl']}"