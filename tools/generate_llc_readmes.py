#!/usr/bin/env python3
"""
Idempotently generates canonical README.md files for every TFA/LLC layer
across all domains and CAx tracks.
"""

import pathlib
import textwrap
from typing import Dict, List

# Canonical definition of LLCs, their groups and meanings.
LLC_DEFINITIONS = {
    "SYSTEMS": {
        "SI": {
            "name": "System Integration",
            "meaning": "Orchestration of multiple domains and services (MAP→MAL). Defines system-wide behavior, safety sequences, and data flows",
            "artifacts": ["routes.map.yaml", "thg.temporal.json", "optimo-joins.yaml"],
            "anchor": "#31-systems-group"
        },
        "DI": {
            "name": "Domain Interface", 
            "meaning": "Defines the formal, versioned API contract for a single domain's services (the MALs). This is the boundary layer",
            "artifacts": ["mal.contract.json", "openapi.yaml", "JSON schemas"],
            "anchor": "#31-systems-group"
        }
    },
    "STATIONS": {
        "SE": {
            "name": "Station Envelope",
            "meaning": "Defines the safe operating limits (physical, electrical, environmental) for a specific station (e.g., test bench, integration lab)",
            "artifacts": ["envelope.se.yaml", "checks.se.tests.yaml"],
            "anchor": "#32-stations-group"
        }
    },
    "COMPONENTS": {
        "CV": {
            "name": "Component Vendor", 
            "meaning": "Information about the supplier of a component", 
            "artifacts": ["<VENDOR_CODE>.vendor.yaml"], 
            "anchor": "#33-components-group"
        },
        "CE": {
            "name": "Component Equipment", 
            "meaning": "Defines a specific equipment model or type (e.g., \"Power Control Unit Model X\")", 
            "artifacts": ["<PART_NUMBER>.equipment.yaml"], 
            "anchor": "#33-components-group"
        },
        "CC": {
            "name": "Configuration Cell", 
            "meaning": "A logical grouping of equipment that forms a functional unit", 
            "artifacts": ["<CELL_NAME>.cell.yaml"], 
            "anchor": "#33-components-group"
        },
        "CI": {
            "name": "Configuration Item", 
            "meaning": "A unique, specific instance of a component, linking hardware to its exact software/firmware load", 
            "artifacts": ["<INSTANCE_ID>.item.yaml"], 
            "anchor": "#33-components-group"
        },
        "CP": {
            "name": "Component Part", 
            "meaning": "An atomic, non-decomposable part with data for its Digital Material Passport (DMP)", 
            "artifacts": ["<PART_NUMBER>.part.yaml"], 
            "anchor": "#33-components-group"
        }
    },
    "BITS": {
        "CB": {
            "name": "Classical Bit", 
            "meaning": "Contains the classical, deterministic algorithms, solvers, and computational logic", 
            "artifacts": ["algos/", "contracts/", "tests/"], 
            "anchor": "#34-bits-group"
        }
    },
    "QUBITS": {
        "QB": {
            "name": "Qubit", 
            "meaning": "Manages quantum computing artifacts, including problem formulations and orchestration policies", 
            "artifacts": ["problems/", "orchestration/", "tests/"], 
            "anchor": "#35-qubits-group"
        }
    },
    "ELEMENTS": {
        "UE": {
            "name": "Unit Element", 
            "meaning": "Contains fundamental, reusable, and testable software units (drivers, parsers, validators)", 
            "artifacts": ["ue_manifest.yaml", "ue_*.py"], 
            "anchor": "#36-elements-group"
        },
        "FE": {
            "name": "Federation Entanglement", 
            "meaning": "Defines the rules and contracts for secure, multi-agent or multi-organization collaboration", 
            "artifacts": ["fe_coalition.schema.json", "contracts/"], 
            "anchor": "#36-elements-group"
        }
    },
    "WAVES": {
        "FWD": {
            "name": "Forward/Waves Dynamics", 
            "meaning": "Manages predictive analytics, simulations, and time-series/frequency-domain analysis", 
            "artifacts": ["fwd_metrics.yaml", "thg.links.yaml"], 
            "anchor": "#37-waves-group"
        }
    },
    "STATES": {
        "QS": {
            "name": "Quantum State", 
            "meaning": "The immutable, auditable evidence layer. Stores signed records of system operations and state transitions", 
            "artifacts": ["det_anchor.schema.json", "anchors/"], 
            "anchor": "#38-states-group"
        }
    }
}

def generate_readme_content(group_name: str, llc_code: str, definition: Dict, relative_path_to_root: str) -> str:
    """Generates the Markdown content for an LLC README."""
    name = definition["name"]
    meaning = definition["meaning"]
    artifacts_list = "\n- ".join(f"`{a}`" for a in definition["artifacts"])
    anchor = definition["anchor"]
    
    # Builds the relative link to the hierarchy file
    hierarchy_link = f"{relative_path_to_root}/_LLC-HIERARCHY.md{anchor}"

    return textwrap.dedent(f"""
# Layer: {name} ({llc_code})

**UTCS**: `utcs:tfa:spec:llc:{llc_code.lower()}:v2.1.0`  
**Group**: `{group_name}`

## Canonical Meaning

This layer is responsible for **{meaning}**.

For the full architectural context and governance rules, refer to the canonical definition in the
[**_LLC-HIERARCHY.md**]({hierarchy_link}).

## Artifacts in this Layer

Key artifacts typically found in the `{llc_code}` layer include:
- {artifacts_list}
""").strip()

def main():
    """Traverses the structure and generates the READMEs."""
    portfolio_root = pathlib.Path(__file__).resolve().parents[1]
    domains_root = portfolio_root / "portfolio" / "2-DOMAINS-LEVELS"
    
    if not domains_root.exists():
        print(f"Error: Directory not found -> {domains_root}")
        return

    count = 0
    # Itera sobre todos los directorios LLC que se puedan encontrar
    for group_name, llcs in LLC_DEFINITIONS.items():
        for llc_code, definition in llcs.items():
            # Busca todos los directorios que coincidan con esta capa LLC
            for llc_path in domains_root.glob(f"*/TFA/{group_name}/{llc_code}"):
                if llc_path.is_dir():
                    # Calcula la profundidad para el enlace relativo
                    depth = len(llc_path.relative_to(domains_root).parts)
                    relative_path = "/".join([".."] * depth)
                    
                    readme_content = generate_readme_content(group_name, llc_code, definition, relative_path)
                    
                    readme_path = llc_path / "README.md"
                    readme_path.write_text(readme_content, encoding="utf-8")
                    count += 1
                    print(f"✅ Generated: {llc_path.relative_to(portfolio_root)}/README.md")
    
    print(f"\n🏛️ Generated or updated {count} canonical LLC README.md files.")

if __name__ == "__main__":
    main()