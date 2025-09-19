import yaml, re, pathlib

BASE = pathlib.Path(__file__).parents[1]

REQ_RE = re.compile(r"FADEC_X/[^#]+#?[A-Za-z0-9_-]*")

# Cada hazard debe linkar al menos a una prueba y a un requisito

def test_hazard_links_present():
    reg = yaml.safe_load((BASE/"ASSURANCE/ARP4761/hazard_register_hybrid_fc.yaml").read_text())
    for hz in reg.get("hazards", []):
        links = hz.get("links", {})
        tests = links.get("tests", [])
        reqs = links.get("requirements", [])
        assert tests and reqs, f"Hazard {hz.get('id')} sin links suficientes"
        for r in reqs:
            assert REQ_RE.match(r), f"Requisito mal formado: {r}"