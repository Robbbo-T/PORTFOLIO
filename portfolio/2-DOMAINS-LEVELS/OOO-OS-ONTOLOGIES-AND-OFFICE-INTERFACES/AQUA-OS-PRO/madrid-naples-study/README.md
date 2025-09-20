# Madrid-Naples Study Case — Predictive Route Optimization

## Overview
Study case for predictive route optimization on LEMD (Madrid) → LIRN (Naples) at cruise Mach, with a 10-minute receding-horizon loop.

## Route Parameters
- **Departure**: LEMD (Madrid-Barajas Airport)
- **Destination**: LIRN (Naples International Airport)
- **Distance**: ~814 nm (great-circle)
- **Aircraft**: AMPEL360 BWB-Q100 (MSN-0001 "BOB")
- **Cruise**: M ≈ 0.78, FL350–390, bank ≤ 25°, RVSM
- **Estimated Flight Time**: ~1h 46m (no wind)

## Route Corridors Evaluated
### North Corridor
LEMD → BCN FIR → Provence → Ligurian coast → Tyrrhenian entry to LIRN
- Often smoother if convective cells sit south of the Gulf of Lion

### Mid-Med Corridor  
LEMD → Baleares DCTs → W Tyrrhenian
- Shorter distance but more exposed to maritime convection line-ups

## Optimization Loop (Every 20-30s)
1. **Ingest**: 400-600 km weather corridor along active leg
   - ECMWF tiles (winds/temp/fronts)
   - EDR polygons from IATA Turbulence Aware
   - Convective activity and icing probability

2. **Estimate**: UKF/EnKF sensor fusion
   - GNSS/INS/AHRS/air-data streams
   - Optional quantum-IMU bias-stable aid
   - Local wind/turbulence field estimation

3. **Optimize**: 10-min micro-trajectory (lat, lon, FL, time)
   - Minimize: ∫(w_f·ṁ_fuel + w_t·EDR² + w_c·1_conv + w_i·P_icing) dt
   - Subject to: bank ≤ 25°, Mach hold, airspace constraints

4. **Output**: Delta-FMS commands (HDG/ALT/CI) + 4D trajectory proposal

## Weather Data Sources
- **ECMWF Open Data**: Global operational (0.5° grid)
- **RAP/HRRR**: High-frequency nowcasts (where available)
- **IATA Turbulence Aware**: Real-time EDR from airline fleets
- **GraphCast**: AI nowcast for bias correction (0-20 min horizon)

## Performance Model
- **Base**: OpenAP-calibrated for BWB-Q100
- **Upgrade Path**: BADA (when licensed)
- **Dynamics**: Point-mass 2.5D model with wind-relative kinematics

## Quantum-Classical Bridge Integration
- **CB**: Classical NMPC solver (CasADi/acados)
- **QB**: Optional QAOA/VQE ensemble optimization
- **UE**: Meteorological unit elements (wind, EDR, icing fields)
- **FE**: Multi-aircraft federation for risk-field sharing
- **FWD**: Nowcast shim and wave dynamics prediction
- **QS**: State provenance (α=proposed, β=loaded, ψ=executing, φ=archived)

## Expected Outcomes
- **Sensitivity Analysis**: 
  - +30 kt tailwind: ~7 min time gain
  - -20 kt headwind: ~5 min time loss
  - Convective avoidance: 2-5 nm detour for smooth air

- **Risk Mitigation**:
  - EDR avoidance for passenger comfort
  - Convective cell dodging for safety
  - Icing probability minimization
  - Fuel optimization vs. time trade-offs

## Implementation Files
```
madrid-naples-study/
├── README.md                    # This file
├── route-definition.yaml        # Route parameters and constraints
├── weather-sources.yaml         # Data source configurations
├── optimization-config.yaml     # NMPC parameters and cost weights
├── simulation-scenarios/        # Test scenarios and validation cases
├── results/                     # Optimization results and analysis
└── validation/                  # Performance validation scripts
```

## Validation Criteria
- [ ] Route completion within ±2% of baseline time
- [ ] Weather avoidance effectiveness (EDR reduction ≥ 50%)
- [ ] Fuel efficiency within 3% of optimal
- [ ] Real-time performance (≤ 300ms per optimization cycle)
- [ ] QS state transitions properly logged
- [ ] FE federation policies enforced

## Status
🚧 **In Development** - Initial implementation phase

*Version: 1.0-ALPHA*  
*Last Updated: 2025-01-27*