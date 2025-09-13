Idea Submission: Tunable AB/BA Domain-Wall Waveguides in Bilayer Graphene for Reconfigurable 1D Quantum Channels

Submitter: Amedeo Pelliccia
Date: 2025-09-13
Domain: EDI · CQH · OOO (Electronics & Digital Instruments · Cryogenics/Quantum Interfaces · Operating Systems/Navigation/HPC)
Priority: High

## Problem Statement

AB/BA boundaries (structural twins) in bilayer graphene (BLG) are widely studied for valley-polarized chiral channels. However, device-grade guidance on non-chiral 1D states—arising when DW width and interlayer bias tune confinement and when 1D bands hybridize with the 2D continuum—is scarce. We lack:

- A width–bias–field design map predicting when DWs host (i) low-energy confined non-chiral modes vs (ii) higher-energy quasi-bound states.
- Fabrication recipes to reproducibly set DW width (soliton profile/strain control) and achieve dual-gate interlayer bias with clean encapsulation.
- Measurement protocols linking spectroscopy/transport signatures (Landau fans, conductance steps, quasi-bound resonances) to the model.

This blocks the use of DWs as reconfigurable, low-power, radiation-tolerant on-chip waveguides for avionics-grade cryogenic/quantum electronics.

## Proposed Solution

Deliver a model-to-hardware pipeline that co-designs DW width w, interlayer bias U, and magnetic field B to realize switchable 1D channels:

1. **Theory & Simulation (OOO → OPTIM-DT)**
   - Continuum Dirac + interlayer coupling for BLG with spatially varying stacking; validate with tight-binding.
   - Compute dispersion, mode localization length, and coupling into 2D continuum vs (w, U, B).
   - Transport via KWANT/NEGF to extract conductance plateaus, valley polarization, and Q-factors of quasi-bound modes.
   - Output: Design map highlighting confined vs quasi-bound regimes (e.g., w\sim 2–30\,\mathrm{nm}, U\sim 0–200\,\mathrm{meV}, B=0–10\,\mathrm{T}).
2. **Device Fabrication (EDI · CQH)**
   - h-BN encapsulated BLG, deterministic stacking; create AB/BA DWs by controlled strain/soliton engineering or local gates.
   - Dual graphite gates for clean U control; e-beam-defined contacts and local top gates for DW addressing.
   - Optional nano-split gates to tune effective DW width electrostatically.
3. **Cryogenic Characterization (CQH)**
   - 1.5–10 K magneto-transport: look for 1D channel onset, bias-tunable mode count, Fabry–Pérot-like resonances (quasi-bound states).
   - STM/STS on sister samples: confirm LDOS confinement at DW, track band crossover into 2D continuum with U and B.
4. **Control & Integration (IIS · EDI)**
   - Gate-bias control logic for on-demand switching between chiral and non-chiral regimes.
   - Radiation-tolerance screening and variability analysis for aerospace use cases.

## Expected Impact

- **Technical:** A reproducible DW waveguide primitive: gate-defined, low-loss 1D interconnects with selectable chirality and tunable coupling to the 2D bath. Enables valleytronic routing, filters, and mixers at cryo.
- **Business:** Foundational IP for reconfigurable interconnects in quantum-ready avionics and sensors (mass/power savings, simplified interposer layouts). Positions portfolio for partnerships in quantum-classical edge hardware.
- **AQUA/QS:** Clear CB→QB bridge: classical control (CB) dynamically configures quasi-1D quantum channels (QB), advancing the QS (Quantum Superposition) capability within CQH/EDI stacks.

## Resource Requirements

- **People (core):** 1 PI (quantum/2D materials), 1 device physicist, 1 fabrication engineer, 1 modeling/NEGF specialist, 1 test engineer.
- **Time:** 12–18 months (M1–M6 modeling & mask; M4–M12 fab; M8–M18 measurements & iterations).
- **Tools / Capex:**
  - Modeling: Python/Julia TB + NEGF (KWANT), continuum solvers; HPC queue (OOO).
  - Fab: dry transfer, e-beam, reactive etch, metal evap; h-BN/BLG stacks; dual-gate process.
  - Test: cryostat (≤1.5–10 K), up to 9–14 T magnet, low-noise electronics; optional STM/STS.
- **Ops:** Cleanroom access (≥2 runs), consumables, wafers, probes; data pipeline into OPTIM-DT.

## Success Criteria

- **S1 (Model):** Published design map predicting confined vs quasi-bound regimes; open datasets & scripts.
- **S2 (Spectroscopy/Transport):**
  - Observation of low-energy non-chiral confined modes at targeted w,U with localization to the DW (STS LDOS contrast ≥ 5× vs domains).
  - Quasi-bound resonances when 1D bands cross the 2D continuum; extracted Q-factor ≥ 20 at 4 K.
  - Bias-controlled mode switching on/off ratio ≥ 10³; ballistic segment ≥ 1 µm.
- **S3 (System):** Prototype DW interconnect demonstrating routing/switching at sub-µs gate update; reproducibility across ≥ 3 chips.
- **S4 (Aerospace Readiness):** Preliminary radiation/thermal cycling data meeting CQH/IIS acceptance thresholds.

## Risk Assessment

- **Valley mixing & disorder** → h-BN encapsulation, ultra-clean transfer, minimize edge roughness; post-fab current anneal.
- **DW width variability** → strain-soliton calibration via Raman/AFM; add electrostatic width-trim gates.
- **Gate leakage/drift** → use graphite gates + high-quality dielectrics; bake-out and passivation protocols.
- **Model–hardware mismatch** → close loop with OPTIM-DT: fit TB parameters to STS/transport, iterate masks.

## TFA Integration Point

- **Domains:**
  - EDI (device stack, control electronics), CQH (cryogenic/quantum interfaces), OOO (HPC modeling & data), IIS (control logic/agents).
- **Layers & Bridges:**
  - SYSTEMS/SI: DW-waveguide subsystem integration with cryo platform.
  - COMPONENTS/CI: BLG DW channel + dual-gate stack.
  - BITS/CB→QB: Gate control (CB) configuring quantum transport channels (QB).
  - FE (Federation Entanglement): Link device artifacts to simulation & test datasets across domains.
  - FWD/QS: Operating envelope surfaces over (w,U,B,T) with QS metrics for mode purity and stability.
