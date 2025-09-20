# TFA/AQUA-OS Strategic Roadmap 2025-2030

**UTCS**: `utcs:roadmap:summary:doc:RM-0001:v2.1.0`  
**Status**: Active, reviewed quarterly  
**Owner**: Amedeo Pelliccia

---

## 1. Executive Summary

This document outlines the strategic evolution of the TFA (Top Final Algorithm) / AQUA-OS platform from its current v2.0 state through full quantum-classical integration by 2030. Our mission is to build the definitive platform for engineering, certifying, and operating next-generation aerospace systems by embedding safety, compliance, and traceability directly into the development lifecycle.

The roadmap is managed through a **"Roadmap as Code"** system, where this document provides a high-level summary, and all detailed plans, dependencies, KPIs, and risks are stored as version-controlled, machine-readable artifacts.

**Core Strategic Pillars:**
1.  **Compliance as Code (CaC)**: Automate safety and regulatory validation in CI/CD.
2.  **Certification as a Service (CaaS)**: Generate on-demand certification packages.
3.  **Digital Twin Sync**: Create a live, verifiable link between the physical asset and its digital model.
4.  **Quantum Advantage**: Leverage quantum computing for complex optimization and security.

---

## 2. Phase Overview & Timeline

The platform will evolve through four major phases, coordinated across core technology, certification, and program deployment.

```mermaid
gantt
    title TFA Platform Evolution 2025-2030
    dateFormat YYYY-MM
    axisFormat %Y-%m
    
    section Core Platform
    v2.0 TFA Core          :done, core1, 2025-09, 30d
    v2.2 UTCS Alpha        :active, core2, 2025-10, 90d
    v2.5 AGI Integration   :core3, 2026-04, 180d
    v3.0 Digital Twin      :core4, 2027-01, 365d
    v4.0 Quantum Full      :core5, 2028-01, 730d
    
    section Certification
    DO-178C Level C        :cert1, 2025-11, 120d
    DO-178C Level B        :cert2, after cert1, 180d
    ARP4754A Full          :cert3, after cert2, 240d
    DO-178C Level A        :cert4, after cert3, 365d
    
    section Programs
    AMPEL360 BWB          :prog1, 2025-10, 1460d
    GAIA Quantum SAT      :prog2, 2026-01, 1095d
    ARES-X UAS            :prog3, 2026-06, 1095d
    H2-CORRIDOR-X         :prog4, 2026-03, 1460d
```

---

## 3. Critical Path to First Flight & Certification

The roadmap is governed by a critical path that prioritizes the foundational capabilities required for certification and the first flight of the AMPEL360 BWB program. Successful execution of these steps is paramount.

```mermaid
graph LR
    subgraph "Critical Path to Flight"
        A1(UTCS Foundation<br>Q4 2025) --> A2(DET Evidence<br>Q1 2026)
        A2 --> B1(CaaS Automation<br>Q2 2026)
        B1 --> B2(DO-178C Level B<br>Q4 2026)
        B2 --> C1(Digital Twin v1<br>Q2 2027)
        C1 --> C2(DO-178C Level A<br>Q4 2027)
        C2 --> D1(First Flight<br>Q1 2028)
    end
    
    style A1 fill:#d4edda,stroke:#155724
    style A2 fill:#d4edda,stroke:#155724
    style B1 fill:#fff3cd,stroke:#856404
    style B2 fill:#fff3cd,stroke:#856404
    style C1 fill:#f8d7da,stroke:#721c24
    style C2 fill:#f8d7da,stroke:#721c24
    style D1 fill:#cce5ff,stroke:#004085
```

---

## 4. Program Portfolio

The platform's development is driven by and validated against a portfolio of ambitious, real-world aerospace programs.

| Program | Code | Segment | Key Objective |
| :--- | :--- | :--- | :--- |
| **AMPEL360 BWB-Q100** | `AMPEL360` | Air | Certify a next-generation blended-wing-body aircraft. |
| **GAIA Quantum SAT** | `GAIA-SAT` | Space | Demonstrate secure quantum satellite communications. |
| **ARES-X UAS SWARM** | `ARES-X` | Defense | Deploy autonomous, coordinated UAS swarms. |
| **H2-CORRIDOR-X** | `H2-CORRIDOR-X`| Cross | Build a digital twin for European hydrogen infrastructure. |

---

## 5. Key Performance Indicators (KPIs) - Long Term (2030)

Our success will be measured by our ability to transform the aerospace industry across four key vectors.

| Metric | Target | Strategic Impact |
| :--- | :--- | :--- |
| **Certification Cost Reduction** | **-90%** | Make safety financially sustainable and accessible. |
| **Time to Market** | **-60%** | Accelerate innovation in a traditionally slow industry. |
| **Safety Events** | **-99%** | Move from reactive mitigation to proactive, predictive prevention. |
| **Carbon Footprint** | **-40%** | Enable more efficient aircraft and operations. |

---

## 6. How to Use This Roadmap

This document is a high-level summary. The full, detailed, and machine-readable roadmap system resides in the `/roadmap` directory and is managed via the `Makefile`.

*   **For Detailed Plans**: See [`/roadmap/roadmap.yaml`](./roadmap/roadmap.yaml) for a complete list of deliverables, dependencies, risks, and OKRs.
*   **For Live Status**: The [**Live Roadmap Dashboard**](./dashboards/index.html) provides real-time progress, KPI tracking, and risk heatmaps.
*   **For Program Management**: Use `make progress` and `make report` to generate the latest status reports.
*   **For Daily Tasks**: All deliverables are synchronized as issues and milestones in our GitHub repository, governed by the templates in [`/github`](./github).

*This roadmap is a living document, automatically updated by our CI/CD pipeline and reviewed quarterly by the governance board.*
```
