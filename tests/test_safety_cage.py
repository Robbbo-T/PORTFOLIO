import time

class Supervisor:
    def __init__(self):
        self.mode = "NORMAL"
        self.v_bus = 800
    def event_afdi(self):
        t0 = time.perf_counter_ns()
        self.mode = "DEGRADED"; fc_cmd = 0; self.isolated = True
        dt_ms = (time.perf_counter_ns()-t0)/1e6
        return dt_ms, fc_cmd

def test_trip_latency_afdi():
    sup = Supervisor()
    dt_ms, fc_cmd = sup.event_afdi()
    assert dt_ms <= 2.0
    assert fc_cmd == 0
    assert sup.mode == "DEGRADED"