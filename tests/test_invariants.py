import math
from hypothesis import given, strategies as st

# Interfaces mínimas simuladas
def controller_step(demand_kw, env):
    # Dummy: asegura invariante de ejemplo
    out = {
        "fc_assist_kw": max(0.0, min(env["fc_max_kw"], demand_kw*0.3)),
        "surge_idx": max(env["S_min"], 0.08),
        "v_bus": 800.0
    }
    return out

@st.composite
def power_profiles(draw):
    n = draw(st.integers(min_value=10, max_value=200))
    return [draw(st.floats(min_value=0, max_value=5000)) for _ in range(n)]

@given(demand=power_profiles(), env=st.fixed_dictionaries({"S_min": st.just(0.07), "fc_max_kw": st.just(3500)}))
def test_invariant_surgesafe(demand, env):
    for step in demand:
        out = controller_step(step, env)
        if out["fc_assist_kw"] > 0:
            assert out["surge_idx"] >= env["S_min"]

def test_invariant_vbus():
    out = controller_step(1000, {"S_min":0.07, "fc_max_kw":3500})
    assert 650 <= out["v_bus"] <= 1050