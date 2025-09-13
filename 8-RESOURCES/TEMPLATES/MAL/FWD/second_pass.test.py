"""Template test to verify MAL-FWD idempotency.
Calling forecast twice with the same parameters should not change state."""

from pathlib import Path

def forecast(params: dict) -> dict:
    """Placeholder for MAL-FWD forecast logic."""
    return {"delta": 0}

def test_second_pass_forecast_no_delta():
    params = {"horizon": "1h"}
    first = forecast(params)
    second = forecast(params)
    assert second["delta"] == 0
