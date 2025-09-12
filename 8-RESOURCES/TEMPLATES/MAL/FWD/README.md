# MAL-FWD (Forward Wave Dynamics Service)

Shared Forward Wave Dynamics service for nowcasting, forecasting, and predictive analysis across all domains.

## Purpose

MAL-FWD provides predictive and retrodictive field services with configurable horizons and accuracy baselines.

## Key Operations

- `nowcast` - Current state estimation
- `forecast` - Future state prediction  
- `retrodict` - Historical state reconstruction
- `assimilate` - Data fusion and integration

## Configuration Template

```yaml
mal_fwd:
  service_type: "forward_wave_dynamics"
  prediction_horizons:
    short_term: "1h"
    medium_term: "24h" 
    long_term: "7d"
  data_sources:
    sensors: ["weather", "telemetry", "mission"]
    external: ["noaa", "satellite", "ais"]
  accuracy_baselines:
    nowcast: 0.95
    forecast_1h: 0.90
    forecast_24h: 0.85
  
# Integration points
integration:
  classical_compute: "MAL-CB"
  quantum_compute: "MAL-QB"
  state_management: "MAL-QS"
```

## Metrics Requirements

- Horizons documentation and validation
- Accuracy baselines with confidence intervals  
- Performance benchmarks for real-time operations

## Usage

Configure prediction horizons and accuracy requirements for your domain's forecasting needs.