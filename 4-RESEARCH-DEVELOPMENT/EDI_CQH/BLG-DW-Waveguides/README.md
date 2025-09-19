# BLG Domain Wall Waveguides

## Overview

Bilayer graphene (BLG) domain wall (DW) waveguides for tunable AB/BA domain-wall channels in reconfigurable 1D quantum systems. This project implements a model-to-hardware pipeline for co-designing DW width w, interlayer bias U, and magnetic field B to realize switchable 1D channels.

## Physics Model

### Continuum Dirac Model

The low-energy physics of bilayer graphene is described by a four-band Dirac Hamiltonian with interlayer coupling. For AB/BA domain walls, the system exhibits spatially varying stacking order that creates confined states at the boundary.

### Quick Design Scalings

Key parameter ranges for confined vs quasi-bound regimes:
- Domain wall width: w ∼ 2–30 nm  
- Interlayer bias: U ∼ 0–200 meV
- Magnetic field: B = 0–10 T

### Valley-Chern Physics

In gated BLG the valley Chern number per valley 𝒞ᵥ = ±1 (per spin) changes sign across the DW (total change |Δ𝒞ᵥ| = 2), predicting two co-propagating kink channels per valley in the smooth-wall limit; v₃ splits their dispersions and modulates leakage.

## Technical Specifications

### Device Parameters

#### Interlayer Bias Calibration

```yaml
interlayer_bias_calibration:
  model: "parallel-plate + Hartree screening"
  parameters:
    C_t: 50e-6  # F/m^2, top gate capacitance per unit area
    C_b: 45e-6  # F/m^2, back gate capacitance per unit area
    d_t: 10e-9  # m, top gate dielectric thickness
    d_b: 300e-9 # m, back gate dielectric thickness
    epsilon_r_t: 3.9  # relative permittivity, top dielectric (SiO2)
    epsilon_r_b: 3.9  # relative permittivity, back dielectric (SiO2)
    
  voltage_to_bias_conversion:
    # U = α(V_tg - V_tg0) + β(V_bg - V_bg0)
    alpha: 0.85  # eV/V, top gate efficiency
    beta: 0.15   # eV/V, back gate efficiency
    V_tg0: 0.0   # V, top gate offset voltage
    V_bg0: 0.0   # V, back gate offset voltage
    
  screening_corrections:
    thomas_fermi_length: 0.8e-9  # m, screening length in graphene
    dielectric_environment: "hBN/SiO2"
    temperature_dependence: true
    
  operating_ranges:
    V_tg_min: -10.0  # V
    V_tg_max: 10.0   # V
    V_bg_min: -40.0  # V 
    V_bg_max: 40.0   # V
    max_interlayer_bias: 200e-3  # eV
```

### Material Parameters

```yaml
material_parameters:
  bilayer_graphene:
    lattice_constant: 0.246e-9  # m, in-plane lattice constant
    interlayer_spacing: 0.335e-9  # m, c-axis spacing
    
  hopping_parameters:
    t0: 2.7     # eV, intralayer nearest neighbor
    t1: 0.4     # eV, interlayer (AB sites)
    t3: 0.315   # eV, trigonal warping
    t4: 0.044   # eV, interlayer next-nearest neighbor
    
  dielectric_environment:
    substrate: "hBN"
    encapsulation: "hBN"
    relative_permittivity: 4.5
```

### Domain Wall Geometry

```yaml
domain_wall_parameters:
  profile_type: "tanh"
  characteristic_width: [2e-9, 30e-9]  # m, tunable range
  length: [1e-6, 10e-6]  # m, device length

  creation_method: "strain_engineering"  # or "electrostatic_gating"
  control_mechanism: "dual_gate_bias"

  confinement_metrics:
    localization_length_target: [5e-9, 50e-9]  # m
    energy_gap_target: [1e-3, 50e-3]  # eV
    mode_purity_target: 0.8  # dimensionless
```

## Fabrication & Transfer Notes

- Large-area graphene supply relies on CVD growth on catalytic metal foils with subsequent transfer to insulating stacks, following the scalable process established by Pandey et al. for wafer-scale films with low sheet resistance and minimal defect density (Appl. Phys. Lett. 96, 073102, 2010). Layer-by-layer assembly of such films enables deterministic bilayer stacks prior to AB/BA domain engineering.

## Simulation Framework

The transport simulation is implemented in `simulations/dw_transport.py` using the KWANT package for quantum transport calculations.

### Key Features
- Continuum and tight-binding models
- Magnetic field support 
- Mode extraction and localization analysis
- Conductance calculations vs energy

## Implementation Status

- [x] Basic transport simulation framework
- [x] Domain wall profile implementation  
- [x] Mode extraction capabilities
- [ ] Magnetic field implementation
- [ ] Valley-polarized transport analysis
- [ ] Experimental calibration routines

## References

- Martin et al. - Theory of kink channels in gated BLG
- Ju et al. - Experimental observation of chiral modes
- McCann & Koshino - Canonical low-energy BLG reference
- Pandey et al. - Large-scale graphene films synthesized on metals and transferred to insulators for electronic applications
