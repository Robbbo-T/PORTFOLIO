# Amedeo Pelliccia · Portfolio

Strict **TFA-only** domains. Snapshot: 2025-09-10T12:02:06.022990Z

## ASSEMBLING GENERAL INTELLIGENCE (AGI) — For Aerospace Knowledge Competencies
**Author**: Amedeo Pelliccia  
**Starting Date**: 25/11/2024  
**TFA Snapshot**: 2025-09-10T12:02:06.022990Z

### Policy - STRICT TFA-ONLY
- Each domain uses **`TFA/`** as the canonical container.
- Subgroups: **SYSTEMS/** (SI, SE, DI), **COMPONENTS/** (CE, CC, CI, CP, CV), **ELEMENTS/** (FE), **STATES/** (QS), **META/** (README).
- **NO FLAT LLC FOLDERS** under `2-DOMAINS-LEVELS/<DOMAIN>/` - ALL work must target `TFA/<GROUP>/<LLC>/`.


# Rebuild portfolio from scratch with STRICT TFA-ONLY policy (no flat LLC folders), then package a ZIP and tree listings.

```python
import os, zipfile
from pathlib import Path
from datetime import datetime

ROOT = Path("/mnt/data/Amedeo-Pelliccia-Portfolio")
if ROOT.exists():
    import shutil
    shutil.rmtree(ROOT)

def write(path: Path, content: str=""):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def gitkeep(dir_path: Path):
    dir_path.mkdir(parents=True, exist_ok=True)
    (dir_path/".gitkeep").write_text("", encoding="utf-8")

# Root
write(ROOT/"README.md", f"# Amedeo Pelliccia · Portfolio\n\nStrict **TFA-only** domains. Snapshot: {datetime.utcnow().isoformat()}Z\n")
for f in ["CHANGELOG.md","CONTRIBUTING.md","ROADMAP.md","SECURITY.md"]:
    write(ROOT/f, f"# {f[:-3]}\n")

# .github
gitkeep(ROOT/".github")
write(ROOT/".github/copilot-instructions.md", """# Copilot & Agents — Working Rules
- STRICT TFA-ONLY: never create flat LLC folders under `2-DOMAINS-LEVELS/<DOMAIN>/`.
- Use `2-DOMAINS-LEVELS/<DOMAIN>/TFA/<GROUP>/<LLC>/`:
  - SYSTEMS: SI, SE, DI
  - COMPONENTS: CE, CC, CI, CP, CV
  - ELEMENTS: FE
  - STATES: QS
""")

# CI workflows
wf = ROOT/".github/workflows/dir-policy.yml"
wf.parent.mkdir(parents=True, exist_ok=True)
wf.write_text("""name: dir-policy
on: [pull_request]
jobs:
  enforce:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Fail on flat LLC paths
        run: |
          set -e
          bad=$(git ls-files --others --cached --exclude-standard | grep -E '^2-DOMAINS-LEVELS/[^/]+/(SI|SE|DI|CE|CC|CI|CP|CV|FE|QS)(/|$)' || true)
          if [ -n "$bad" ]; then
            echo "::error::Found disallowed flat LLC paths:"
            echo "$bad"
            exit 1
          fi
""", encoding="utf-8")

# Strategy
for name in ["GOVERNANCE.md","MISSION.md","ROADMAP.md","VISION.md"]:
    write(ROOT/"0-STRATEGY"/name, f"# {name[:-3]}\n")

# 1-CAX-METHODOLOGY
sections = {
    "CAB-BRAINSTORMING": ["concept-generation.md", "innovation-framework.md"],
    "CAC-COMPLIANCE-SAFETY-CODE": ["safety-automation.md"],
    "CAD-DESIGN": ["mbse-approach.md", "parametric-modeling.md"],
    "CAE-ENGINEERING": ["simulation-framework.md"],
    "CAEPOST-ENDOFLIFE": ["decommissioning.md"],
    "CAF-FINANCE": ["budgeting-forecasting.md", "resource-planning.yaml"],
    "CAI-AI-INTEGRATION": ["ai-orchestration.md"],
    "CAM-MANUFACTURING": ["bom-bop-management.md"],
    "CAO-ORGANIZATION": ["governance-framework.md", "resource-allocation.yaml", "risk-management.md"],
    "CAP-PRODUCTION": ["mps-mrp-planning.md"],
    "CAS-SUSTAINMENT": ["in-service-support.md"],
    "CAT-TESTING": ["test-planning.md"],
    "CAV-VERIFICATION": ["v-and-v-framework.md"],
}
for sec, files in sections.items():
    for file in files:
        write(ROOT/"1-CAX-METHODOLOGY"/sec/file, f"# {file}\n")
    gitkeep(ROOT/"1-CAX-METHODOLOGY"/sec/"placeholder")
gitkeep(ROOT/"1-CAX-METHODOLOGY"/"CAB-BRAINSTORMING"/"trade-studies")

# CAF deep trees
write(ROOT/"1-CAX-METHODOLOGY"/"CAF-FINANCE"/"FINANCIAL-LEDGER"/"live-valuation-dashboard.md", "# live-valuation-dashboard\n")
write(ROOT/"1-CAX-METHODOLOGY"/"CAF-FINANCE"/"FINANCIAL-LEDGER"/"portfolio-cotization.md", "# portfolio-cotization\n")
gitkeep(ROOT/"1-CAX-METHODOLOGY"/"CAF-FINANCE"/"FINANCIAL-LEDGER"/"audit-trails")
gitkeep(ROOT/"1-CAX-METHODOLOGY"/"CAF-FINANCE"/"FINANCIAL-LEDGER"/"transaction-history")
for f in ["innovation-debt-metrics.md","ip-valuation-framework.md","royalty-streams.md","value-capture-models.md"]:
    write(ROOT/"1-CAX-METHODOLOGY"/"CAF-FINANCE"/"INNOVATION-VALUATION"/f, f"# {f}\n")
for f in ["innovation-metrics.yaml","token-distribution-policy.md","token-economics.md","valuation-framework.md"]:
    write(ROOT/"1-CAX-METHODOLOGY"/"CAF-FINANCE"/"TEKNIA-TOKENS"/f, f"# {f}\n")
gitkeep(ROOT/"1-CAX-METHODOLOGY"/"CAF-FINANCE"/"TEKNIA-TOKENS"/"smart-contracts")

# CAI blockchain integration
write(ROOT/"1-CAX-METHODOLOGY"/"CAI-AI-INTEGRATION"/"blockchain-integration"/"overview.md", "# Blockchain Integration Overview\n")
for sub in ["distributed-ledger/data-immutability","lib-logistics/maintenance-records","lib-logistics/parts-tracking","lib-logistics/service-history",
            "qal-bus-integration/det-anchoring","qal-bus-integration/event-schemas","qal-bus-integration/qaudit-tracking",
            "smart-contracts/contract-templates","smart-contracts/oracle-integration",
            "supply-chain-tracking/material-traceability","supply-chain-tracking/vendor-management",
            "utcs-blockchain/registry-contracts","utcs-blockchain/validation-nodes"]:
    gitkeep(ROOT/"1-CAX-METHODOLOGY"/"CAI-AI-INTEGRATION"/"blockchain-integration"/sub)
write(ROOT/"1-CAX-METHODOLOGY"/"CAI-AI-INTEGRATION"/"blockchain-integration"/"distributed-ledger"/"consensus-mechanisms.md", "# consensus-mechanisms\n")
write(ROOT/"1-CAX-METHODOLOGY"/"CAI-AI-INTEGRATION"/"blockchain-integration"/"distributed-ledger"/"node-architecture.md", "# node-architecture\n")
write(ROOT/"1-CAX-METHODOLOGY"/"CAI-AI-INTEGRATION"/"blockchain-integration"/"smart-contracts"/"automated-execution.md", "# automated-execution\n")
write(ROOT/"1-CAX-METHODOLOGY"/"CAI-AI-INTEGRATION"/"blockchain-integration"/"supply-chain-tracking"/"part-provenance.md", "# part-provenance\n")

# CAS/S1000D tools
tools = ROOT/"1-CAX-METHODOLOGY"/"CAS-SUSTAINMENT"/"S1000D-FRAMEWORK"/"tools"
for f in ["README.md","Top_Level_DMs_AAA_normalized.csv","Top_Level_DMs_AAA_normalized.json","UTCS_S1000D_ID.regex.txt",
          "brex_validator.py","csdb_manager.py","dmc_generator.py","ietp_builder.py","s1000d_lint.py"]:
    write(tools/f, f"# {f}\n")

# 2-DOMAINS-LEVELS — STRICT TFA ONLY
domains = [
    "AAA-STRUCTURES-AERO","AAP-GROUND-SUPPORT","CCC-CABIN-COCKPIT","CQH-CRYO-H2","DDD-SAFETY-CYBER",
    "EDI-ELECTRONICS","EEE-ENVIRONMENTAL","EER-ENERGY-BATTERY","IIF-INFRASTRUCTURE","IIS-AI-SYSTEMS",
    "LCC-CONTROLS-COMMS","LIB-LOGISTICS-CHAIN","MMM-MECHANICAL","OOO-OS-NAVIGATION","PPP-PROPULSION-FUEL"
]
for dom in domains:
    base = ROOT/"2-DOMAINS-LEVELS"/dom/"TFA"
    # SYSTEMS
    for code in ["SI","SE","DI"]:
        gitkeep(base/"SYSTEMS"/code)
    # COMPONENTS (include CV)
    for code in ["CE","CC","CI","CP","CV"]:
        gitkeep(base/"COMPONENTS"/code)
    # ELEMENTS / STATES
    gitkeep(base/"ELEMENTS"/"FE")
    gitkeep(base/"STATES"/"QS")
    write(base/"META"/"README.md", f"# {dom} · TFA Hierarchy\n\nSTRICT TFA-only. Updated {datetime.utcnow().isoformat()}Z\n")
write(ROOT/"2-DOMAINS-LEVELS"/"_LLC-HIERARCHY.md", f"# LLC Hierarchy (STRICT)\nUpdated {datetime.utcnow().isoformat()}Z\n")

# 3..8 stubs
for group in ["3-PROJECTS-USE-CASES","4-RESEARCH-DEVELOPMENT","5-ARTIFACTS-IMPLEMENTATION","6-UTCS-BLOCKCHAIN","7-GOVERNANCE","8-RESOURCES"]:
    gitkeep(ROOT/group)

# Code areas
for lang in ["python","c","rust","typescript","julia","xslt","solidity"]:
    gitkeep(ROOT/"5-ARTIFACTS-IMPLEMENTATION"/"CODE"/lang)
# Infranet minimal
write(ROOT/"5-ARTIFACTS-IMPLEMENTATION"/"CODE"/"infranet"/"README.md", "# INFRANET\n")
write(ROOT/"5-ARTIFACTS-IMPLEMENTATION"/"CODE"/"infranet"/"Makefile", "all:\n\t@echo ok\n")

# UTCS docs
write(ROOT/"6-UTCS-BLOCKCHAIN"/"utcs-blockchain-framework.md", "# UTCS Blockchain Framework\n")
write(ROOT/"6-UTCS-BLOCKCHAIN"/"validate_utcs_mi.py", "print('ok')\n")

# Governance & resources
for sub in ["OPEN-CALL","POLICIES","LICENSING","COMMUNITY","TOKEN-GOVERNANCE/community-proposals"]:
    gitkeep(ROOT/"7-GOVERNANCE"/sub)
for sub in ["ASSETS","TEMPLATES","REFERENCES","TEKNIA-TOKENS/integration-examples"]:
    gitkeep(ROOT/"8-RESOURCES"/sub)

# Package ZIP and trees
def build_tree(path: Path) -> str:
    out = []
    for root, dirs, files in os.walk(path):
        dirs.sort(); files.sort()
        rel = Path(root).relative_to(path)
        indent = "  " * len(rel.parts)
        label = path.name if str(rel)=="." else str(rel)
        out.append(f"{indent}{label}/")
        for f in files:
            out.append(f"{indent}  {f}")
    return "\n".join(out)

zip_path = Path("/mnt/data/Amedeo-Pelliccia-Portfolio_TFA_STRICT.zip")
if zip_path.exists():
    zip_path.unlink()
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
    for p in ROOT.rglob("*"):
        z.write(p, arcname=str(p.relative_to("/mnt/data")))

tree_domains = build_tree(ROOT/"2-DOMAINS-LEVELS")
tree_all = build_tree(ROOT)

Path("/mnt/data/TFA_STRICT_domains_tree.txt").write_text(tree_domains, encoding="utf-8")
Path("/mnt/data/TFA_STRICT_domains_tree.md").write_text(f"# Domains Tree (STRICT TFA) — {datetime.utcnow().isoformat()}Z\n\n```\n{tree_domains}\n```\n", encoding="utf-8")
Path("/mnt/data/Portfolio_TFA_STRICT_tree.txt").write_text(tree_all, encoding="utf-8")
Path("/mnt/data/Portfolio_TFA_STRICT_tree.md").write_text(f"# Portfolio Tree (STRICT TFA) — {datetime.utcnow().isoformat()}Z\n\n```\n{tree_all}\n```\n", encoding="utf-8")

{
 "zip": zip_path.as_posix(),
 "domains_tree_md": "/mnt/data/TFA_STRICT_domains_tree.md",
 "portfolio_tree_md": "/mnt/data/Portfolio_TFA_STRICT_tree.md"
}
```
```Trainer Final Algorithm (Top Final AI) as Amedeo-Pelliccia's portfolio tree

portfolio/
  CHANGELOG.md
  CONTRIBUTING.md
  README.md
  ROADMAP.md
  SECURITY.md
  .github/
    .gitkeep
    copilot-instructions.md
    .github/workflows/
      dir-policy.yml
  0-STRATEGY/
    GOVERNANCE.md
    MISSION.md
    ROADMAP.md
    VISION.md
  1-CAX-METHODOLOGY/
    1-CAX-METHODOLOGY/CAB-BRAINSTORMING/
      concept-generation.md
      innovation-framework.md
      1-CAX-METHODOLOGY/CAB-BRAINSTORMING/placeholder/
        .gitkeep
      1-CAX-METHODOLOGY/CAB-BRAINSTORMING/trade-studies/
        .gitkeep
    1-CAX-METHODOLOGY/CAC-COMPLIANCE-SAFETY-CODE/
      safety-automation.md
      1-CAX-METHODOLOGY/CAC-COMPLIANCE-SAFETY-CODE/placeholder/
        .gitkeep
    1-CAX-METHODOLOGY/CAD-DESIGN/
      mbse-approach.md
      parametric-modeling.md
      1-CAX-METHODOLOGY/CAD-DESIGN/placeholder/
        .gitkeep
    1-CAX-METHODOLOGY/CAE-ENGINEERING/
      simulation-framework.md
      1-CAX-METHODOLOGY/CAE-ENGINEERING/placeholder/
        .gitkeep
    1-CAX-METHODOLOGY/CAEPOST-ENDOFLIFE/
      decommissioning.md
      1-CAX-METHODOLOGY/CAEPOST-ENDOFLIFE/placeholder/
        .gitkeep
    1-CAX-METHODOLOGY/CAF-FINANCE/
      budgeting-forecasting.md
      resource-planning.yaml
      1-CAX-METHODOLOGY/CAF-FINANCE/FINANCIAL-LEDGER/
        live-valuation-dashboard.md
        portfolio-cotization.md
        1-CAX-METHODOLOGY/CAF-FINANCE/FINANCIAL-LEDGER/audit-trails/
          .gitkeep
        1-CAX-METHODOLOGY/CAF-FINANCE/FINANCIAL-LEDGER/transaction-history/
          .gitkeep
      1-CAX-METHODOLOGY/CAF-FINANCE/INNOVATION-VALUATION/
        innovation-debt-metrics.md
        ip-valuation-framework.md
        royalty-streams.md
        value-capture-models.md
      1-CAX-METHODOLOGY/CAF-FINANCE/TEKNIA-TOKENS/
        innovation-metrics.yaml
        token-distribution-policy.md
        token-economics.md
        valuation-framework.md
        1-CAX-METHODOLOGY/CAF-FINANCE/TEKNIA-TOKENS/smart-contracts/
          .gitkeep
      1-CAX-METHODOLOGY/CAF-FINANCE/placeholder/
        .gitkeep
    1-CAX-METHODOLOGY/CAI-AI-INTEGRATION/
      ai-orchestration.md
      1-CAX-METHODOLOGY/CAI-AI-INTEGRATION/blockchain-integration/
        overview.md
        1-CAX-METHODOLOGY/CAI-AI-INTEGRATION/blockchain-integration/distributed-ledger/
          consensus-mechanisms.md
          node-architecture.md
          1-CAX-METHODOLOGY/CAI-AI-INTEGRATION/blockchain-integration/distributed-ledger/data-immutability/
            .gitkeep
        1-CAX-METHODOLOGY/CAI-AI-INTEGRATION/blockchain-integration/lib-logistics/
          1-CAX-METHODOLOGY/CAI-AI-INTEGRATION/blockchain-integration/lib-logistics/maintenance-records/
            .gitkeep
          1-CAX-METHODOLOGY/CAI-AI-INTEGRATION/blockchain-integration/lib-logistics/parts-tracking/
            .gitkeep
          1-CAX-METHODOLOGY/CAI-AI-INTEGRATION/blockchain-integration/lib-logistics/service-history/
            .gitkeep
        1-CAX-METHODOLOGY/CAI-AI-INTEGRATION/blockchain-integration/qal-bus-integration/
          1-CAX-METHODOLOGY/CAI-AI-INTEGRATION/blockchain-integration/qal-bus-integration/det-anchoring/
            .gitkeep
          1-CAX-METHODOLOGY/CAI-AI-INTEGRATION/blockchain-integration/qal-bus-integration/event-schemas/
            .gitkeep
          1-CAX-METHODOLOGY/CAI-AI-INTEGRATION/blockchain-integration/qal-bus-integration/qaudit-tracking/
            .gitkeep
        1-CAX-METHODOLOGY/CAI-AI-INTEGRATION/blockchain-integration/smart-contracts/
          automated-execution.md
          1-CAX-METHODOLOGY/CAI-AI-INTEGRATION/blockchain-integration/smart-contracts/contract-templates/
            .gitkeep
          1-CAX-METHODOLOGY/CAI-AI-INTEGRATION/blockchain-integration/smart-contracts/oracle-integration/
            .gitkeep
        1-CAX-METHODOLOGY/CAI-AI-INTEGRATION/blockchain-integration/supply-chain-tracking/
          part-provenance.md
          1-CAX-METHODOLOGY/CAI-AI-INTEGRATION/blockchain-integration/supply-chain-tracking/material-traceability/
            .gitkeep
          1-CAX-METHODOLOGY/CAI-AI-INTEGRATION/blockchain-integration/supply-chain-tracking/vendor-management/
            .gitkeep
        1-CAX-METHODOLOGY/CAI-AI-INTEGRATION/blockchain-integration/utcs-blockchain/
          1-CAX-METHODOLOGY/CAI-AI-INTEGRATION/blockchain-integration/utcs-blockchain/registry-contracts/
            .gitkeep
          1-CAX-METHODOLOGY/CAI-AI-INTEGRATION/blockchain-integration/utcs-blockchain/validation-nodes/
            .gitkeep
      1-CAX-METHODOLOGY/CAI-AI-INTEGRATION/placeholder/
        .gitkeep
    1-CAX-METHODOLOGY/CAM-MANUFACTURING/
      bom-bop-management.md
      1-CAX-METHODOLOGY/CAM-MANUFACTURING/placeholder/
        .gitkeep
    1-CAX-METHODOLOGY/CAO-ORGANIZATION/
      governance-framework.md
      resource-allocation.yaml
      risk-management.md
      1-CAX-METHODOLOGY/CAO-ORGANIZATION/placeholder/
        .gitkeep
    1-CAX-METHODOLOGY/CAP-PRODUCTION/
      mps-mrp-planning.md
      1-CAX-METHODOLOGY/CAP-PRODUCTION/placeholder/
        .gitkeep
    1-CAX-METHODOLOGY/CAS-SUSTAINMENT/
      in-service-support.md
      1-CAX-METHODOLOGY/CAS-SUSTAINMENT/S1000D-FRAMEWORK/
        1-CAX-METHODOLOGY/CAS-SUSTAINMENT/S1000D-FRAMEWORK/tools/
          README.md
          Top_Level_DMs_AAA_normalized.csv
          Top_Level_DMs_AAA_normalized.json
          UTCS_S1000D_ID.regex.txt
          brex_validator.py
          csdb_manager.py
          dmc_generator.py
          ietp_builder.py
          s1000d_lint.py
      1-CAX-METHODOLOGY/CAS-SUSTAINMENT/placeholder/
        .gitkeep
    1-CAX-METHODOLOGY/CAT-TESTING/
      test-planning.md
      1-CAX-METHODOLOGY/CAT-TESTING/placeholder/
        .gitkeep
    1-CAX-METHODOLOGY/CAV-VERIFICATION/
      v-and-v-framework.md
      1-CAX-METHODOLOGY/CAV-VERIFICATION/placeholder/
        .gitkeep
  2-DOMAINS-LEVELS/
    _LLC-HIERARCHY.md
    2-DOMAINS-LEVELS/AAA-STRUCTURES-AERO/
      2-DOMAINS-LEVELS/AAA-STRUCTURES-AERO/TFA/
        2-DOMAINS-LEVELS/AAA-STRUCTURES-AERO/TFA/COMPONENTS/
          2-DOMAINS-LEVELS/AAA-STRUCTURES-AERO/TFA/COMPONENTS/CC/
            .gitkeep
          2-DOMAINS-LEVELS/AAA-STRUCTURES-AERO/TFA/COMPONENTS/CE/
            .gitkeep
          2-DOMAINS-LEVELS/AAA-STRUCTURES-AERO/TFA/COMPONENTS/CI/
            .gitkeep
          2-DOMAINS-LEVELS/AAA-STRUCTURES-AERO/TFA/COMPONENTS/CP/
            .gitkeep
          2-DOMAINS-LEVELS/AAA-STRUCTURES-AERO/TFA/COMPONENTS/CV/
            .gitkeep
        2-DOMAINS-LEVELS/AAA-STRUCTURES-AERO/TFA/ELEMENTS/
          2-DOMAINS-LEVELS/AAA-STRUCTURES-AERO/TFA/ELEMENTS/FE/
            .gitkeep
        2-DOMAINS-LEVELS/AAA-STRUCTURES-AERO/TFA/META/
          README.md
        2-DOMAINS-LEVELS/AAA-STRUCTURES-AERO/TFA/STATES/
          2-DOMAINS-LEVELS/AAA-STRUCTURES-AERO/TFA/STATES/QS/
            .gitkeep
        2-DOMAINS-LEVELS/AAA-STRUCTURES-AERO/TFA/SYSTEMS/
          2-DOMAINS-LEVELS/AAA-STRUCTURES-AERO/TFA/SYSTEMS/DI/
            .gitkeep
          2-DOMAINS-LEVELS/AAA-STRUCTURES-AERO/TFA/SYSTEMS/SE/
            .gitkeep
          2-DOMAINS-LEVELS/AAA-STRUCTURES-AERO/TFA/SYSTEMS/SI/
            .gitkeep
    2-DOMAINS-LEVELS/AAP-GROUND-SUPPORT/
      2-DOMAINS-LEVELS/AAP-GROUND-SUPPORT/TFA/
        2-DOMAINS-LEVELS/AAP-GROUND-SUPPORT/TFA/COMPONENTS/
          2-DOMAINS-LEVELS/AAP-GROUND-SUPPORT/TFA/COMPONENTS/CC/
            .gitkeep
          2-DOMAINS-LEVELS/AAP-GROUND-SUPPORT/TFA/COMPONENTS/CE/
            .gitkeep
          2-DOMAINS-LEVELS/AAP-GROUND-SUPPORT/TFA/COMPONENTS/CI/
            .gitkeep
          2-DOMAINS-LEVELS/AAP-GROUND-SUPPORT/TFA/COMPONENTS/CP/
            .gitkeep
          2-DOMAINS-LEVELS/AAP-GROUND-SUPPORT/TFA/COMPONENTS/CV/
            .gitkeep
        2-DOMAINS-LEVELS/AAP-GROUND-SUPPORT/TFA/ELEMENTS/
          2-DOMAINS-LEVELS/AAP-GROUND-SUPPORT/TFA/ELEMENTS/FE/
            .gitkeep
        2-DOMAINS-LEVELS/AAP-GROUND-SUPPORT/TFA/META/
          README.md
        2-DOMAINS-LEVELS/AAP-GROUND-SUPPORT/TFA/STATES/
          2-DOMAINS-LEVELS/AAP-GROUND-SUPPORT/TFA/STATES/QS/
            .gitkeep
        2-DOMAINS-LEVELS/AAP-GROUND-SUPPORT/TFA/SYSTEMS/
          2-DOMAINS-LEVELS/AAP-GROUND-SUPPORT/TFA/SYSTEMS/DI/
            .gitkeep
          2-DOMAINS-LEVELS/AAP-GROUND-SUPPORT/TFA/SYSTEMS/SE/
            .gitkeep
          2-DOMAINS-LEVELS/AAP-GROUND-SUPPORT/TFA/SYSTEMS/SI/
            .gitkeep
    2-DOMAINS-LEVELS/CCC-CABIN-COCKPIT/
      2-DOMAINS-LEVELS/CCC-CABIN-COCKPIT/TFA/
        2-DOMAINS-LEVELS/CCC-CABIN-COCKPIT/TFA/COMPONENTS/
          2-DOMAINS-LEVELS/CCC-CABIN-COCKPIT/TFA/COMPONENTS/CC/
            .gitkeep
          2-DOMAINS-LEVELS/CCC-CABIN-COCKPIT/TFA/COMPONENTS/CE/
            .gitkeep
          2-DOMAINS-LEVELS/CCC-CABIN-COCKPIT/TFA/COMPONENTS/CI/
            .gitkeep
          2-DOMAINS-LEVELS/CCC-CABIN-COCKPIT/TFA/COMPONENTS/CP/
            .gitkeep
          2-DOMAINS-LEVELS/CCC-CABIN-COCKPIT/TFA/COMPONENTS/CV/
            .gitkeep
        2-DOMAINS-LEVELS/CCC-CABIN-COCKPIT/TFA/ELEMENTS/
          2-DOMAINS-LEVELS/CCC-CABIN-COCKPIT/TFA/ELEMENTS/FE/
            .gitkeep
        2-DOMAINS-LEVELS/CCC-CABIN-COCKPIT/TFA/META/
          README.md
        2-DOMAINS-LEVELS/CCC-CABIN-COCKPIT/TFA/STATES/
          2-DOMAINS-LEVELS/CCC-CABIN-COCKPIT/TFA/STATES/QS/
            .gitkeep
        2-DOMAINS-LEVELS/CCC-CABIN-COCKPIT/TFA/SYSTEMS/
          2-DOMAINS-LEVELS/CCC-CABIN-COCKPIT/TFA/SYSTEMS/DI/
            .gitkeep
          2-DOMAINS-LEVELS/CCC-CABIN-COCKPIT/TFA/SYSTEMS/SE/
            .gitkeep
          2-DOMAINS-LEVELS/CCC-CABIN-COCKPIT/TFA/SYSTEMS/SI/
            .gitkeep
    2-DOMAINS-LEVELS/CQH-CRYO-H2/
      2-DOMAINS-LEVELS/CQH-CRYO-H2/TFA/
        2-DOMAINS-LEVELS/CQH-CRYO-H2/TFA/COMPONENTS/
          2-DOMAINS-LEVELS/CQH-CRYO-H2/TFA/COMPONENTS/CC/
            .gitkeep
          2-DOMAINS-LEVELS/CQH-CRYO-H2/TFA/COMPONENTS/CE/
            .gitkeep
          2-DOMAINS-LEVELS/CQH-CRYO-H2/TFA/COMPONENTS/CI/
            .gitkeep
          2-DOMAINS-LEVELS/CQH-CRYO-H2/TFA/COMPONENTS/CP/
            .gitkeep
          2-DOMAINS-LEVELS/CQH-CRYO-H2/TFA/COMPONENTS/CV/
            .gitkeep
        2-DOMAINS-LEVELS/CQH-CRYO-H2/TFA/ELEMENTS/
          2-DOMAINS-LEVELS/CQH-CRYO-H2/TFA/ELEMENTS/FE/
            .gitkeep
        2-DOMAINS-LEVELS/CQH-CRYO-H2/TFA/META/
          README.md
        2-DOMAINS-LEVELS/CQH-CRYO-H2/TFA/STATES/
          2-DOMAINS-LEVELS/CQH-CRYO-H2/TFA/STATES/QS/
            .gitkeep
        2-DOMAINS-LEVELS/CQH-CRYO-H2/TFA/SYSTEMS/
          2-DOMAINS-LEVELS/CQH-CRYO-H2/TFA/SYSTEMS/DI/
            .gitkeep
          2-DOMAINS-LEVELS/CQH-CRYO-H2/TFA/SYSTEMS/SE/
            .gitkeep
          2-DOMAINS-LEVELS/CQH-CRYO-H2/TFA/SYSTEMS/SI/
            .gitkeep
    2-DOMAINS-LEVELS/DDD-SAFETY-CYBER/
      2-DOMAINS-LEVELS/DDD-SAFETY-CYBER/TFA/
        2-DOMAINS-LEVELS/DDD-SAFETY-CYBER/TFA/COMPONENTS/
          2-DOMAINS-LEVELS/DDD-SAFETY-CYBER/TFA/COMPONENTS/CC/
            .gitkeep
          2-DOMAINS-LEVELS/DDD-SAFETY-CYBER/TFA/COMPONENTS/CE/
            .gitkeep
          2-DOMAINS-LEVELS/DDD-SAFETY-CYBER/TFA/COMPONENTS/CI/
            .gitkeep
          2-DOMAINS-LEVELS/DDD-SAFETY-CYBER/TFA/COMPONENTS/CP/
            .gitkeep
          2-DOMAINS-LEVELS/DDD-SAFETY-CYBER/TFA/COMPONENTS/CV/
            .gitkeep
        2-DOMAINS-LEVELS/DDD-SAFETY-CYBER/TFA/ELEMENTS/
          2-DOMAINS-LEVELS/DDD-SAFETY-CYBER/TFA/ELEMENTS/FE/
            .gitkeep
        2-DOMAINS-LEVELS/DDD-SAFETY-CYBER/TFA/META/
          README.md
        2-DOMAINS-LEVELS/DDD-SAFETY-CYBER/TFA/STATES/
          2-DOMAINS-LEVELS/DDD-SAFETY-CYBER/TFA/STATES/QS/
            .gitkeep
        2-DOMAINS-LEVELS/DDD-SAFETY-CYBER/TFA/SYSTEMS/
          2-DOMAINS-LEVELS/DDD-SAFETY-CYBER/TFA/SYSTEMS/DI/
            .gitkeep
          2-DOMAINS-LEVELS/DDD-SAFETY-CYBER/TFA/SYSTEMS/SE/
            .gitkeep
          2-DOMAINS-LEVELS/DDD-SAFETY-CYBER/TFA/SYSTEMS/SI/
            .gitkeep
    2-DOMAINS-LEVELS/EDI-ELECTRONICS/
      2-DOMAINS-LEVELS/EDI-ELECTRONICS/TFA/
        2-DOMAINS-LEVELS/EDI-ELECTRONICS/TFA/COMPONENTS/
          2-DOMAINS-LEVELS/EDI-ELECTRONICS/TFA/COMPONENTS/CC/
            .gitkeep
          2-DOMAINS-LEVELS/EDI-ELECTRONICS/TFA/COMPONENTS/CE/
            .gitkeep
          2-DOMAINS-LEVELS/EDI-ELECTRONICS/TFA/COMPONENTS/CI/
            .gitkeep
          2-DOMAINS-LEVELS/EDI-ELECTRONICS/TFA/COMPONENTS/CP/
            .gitkeep
          2-DOMAINS-LEVELS/EDI-ELECTRONICS/TFA/COMPONENTS/CV/
            .gitkeep
        2-DOMAINS-LEVELS/EDI-ELECTRONICS/TFA/ELEMENTS/
          2-DOMAINS-LEVELS/EDI-ELECTRONICS/TFA/ELEMENTS/FE/
            .gitkeep
        2-DOMAINS-LEVELS/EDI-ELECTRONICS/TFA/META/
          README.md
        2-DOMAINS-LEVELS/EDI-ELECTRONICS/TFA/STATES/
          2-DOMAINS-LEVELS/EDI-ELECTRONICS/TFA/STATES/QS/
            .gitkeep
        2-DOMAINS-LEVELS/EDI-ELECTRONICS/TFA/SYSTEMS/
          2-DOMAINS-LEVELS/EDI-ELECTRONICS/TFA/SYSTEMS/DI/
            .gitkeep
          2-DOMAINS-LEVELS/EDI-ELECTRONICS/TFA/SYSTEMS/SE/
            .gitkeep
          2-DOMAINS-LEVELS/EDI-ELECTRONICS/TFA/SYSTEMS/SI/
            .gitkeep
    2-DOMAINS-LEVELS/EEE-ENVIRONMENTAL/
      2-DOMAINS-LEVELS/EEE-ENVIRONMENTAL/TFA/
        2-DOMAINS-LEVELS/EEE-ENVIRONMENTAL/TFA/COMPONENTS/
          2-DOMAINS-LEVELS/EEE-ENVIRONMENTAL/TFA/COMPONENTS/CC/
            .gitkeep
          2-DOMAINS-LEVELS/EEE-ENVIRONMENTAL/TFA/COMPONENTS/CE/
            .gitkeep
          2-DOMAINS-LEVELS/EEE-ENVIRONMENTAL/TFA/COMPONENTS/CI/
            .gitkeep
          2-DOMAINS-LEVELS/EEE-ENVIRONMENTAL/TFA/COMPONENTS/CP/
            .gitkeep
          2-DOMAINS-LEVELS/EEE-ENVIRONMENTAL/TFA/COMPONENTS/CV/
            .gitkeep
        2-DOMAINS-LEVELS/EEE-ENVIRONMENTAL/TFA/ELEMENTS/
          2-DOMAINS-LEVELS/EEE-ENVIRONMENTAL/TFA/ELEMENTS/FE/
            .gitkeep
        2-DOMAINS-LEVELS/EEE-ENVIRONMENTAL/TFA/META/
          README.md
        2-DOMAINS-LEVELS/EEE-ENVIRONMENTAL/TFA/STATES/
          2-DOMAINS-LEVELS/EEE-ENVIRONMENTAL/TFA/STATES/QS/
            .gitkeep
        2-DOMAINS-LEVELS/EEE-ENVIRONMENTAL/TFA/SYSTEMS/
          2-DOMAINS-LEVELS/EEE-ENVIRONMENTAL/TFA/SYSTEMS/DI/
            .gitkeep
          2-DOMAINS-LEVELS/EEE-ENVIRONMENTAL/TFA/SYSTEMS/SE/
            .gitkeep
          2-DOMAINS-LEVELS/EEE-ENVIRONMENTAL/TFA/SYSTEMS/SI/
            .gitkeep
    2-DOMAINS-LEVELS/EER-ENERGY-BATTERY/
      2-DOMAINS-LEVELS/EER-ENERGY-BATTERY/TFA/
        2-DOMAINS-LEVELS/EER-ENERGY-BATTERY/TFA/COMPONENTS/
          2-DOMAINS-LEVELS/EER-ENERGY-BATTERY/TFA/COMPONENTS/CC/
            .gitkeep
          2-DOMAINS-LEVELS/EER-ENERGY-BATTERY/TFA/COMPONENTS/CE/
            .gitkeep
          2-DOMAINS-LEVELS/EER-ENERGY-BATTERY/TFA/COMPONENTS/CI/
            .gitkeep
          2-DOMAINS-LEVELS/EER-ENERGY-BATTERY/TFA/COMPONENTS/CP/
            .gitkeep
          2-DOMAINS-LEVELS/EER-ENERGY-BATTERY/TFA/COMPONENTS/CV/
            .gitkeep
        2-DOMAINS-LEVELS/EER-ENERGY-BATTERY/TFA/ELEMENTS/
          2-DOMAINS-LEVELS/EER-ENERGY-BATTERY/TFA/ELEMENTS/FE/
            .gitkeep
        2-DOMAINS-LEVELS/EER-ENERGY-BATTERY/TFA/META/
          README.md
        2-DOMAINS-LEVELS/EER-ENERGY-BATTERY/TFA/STATES/
          2-DOMAINS-LEVELS/EER-ENERGY-BATTERY/TFA/STATES/QS/
            .gitkeep
        2-DOMAINS-LEVELS/EER-ENERGY-BATTERY/TFA/SYSTEMS/
          2-DOMAINS-LEVELS/EER-ENERGY-BATTERY/TFA/SYSTEMS/DI/
            .gitkeep
          2-DOMAINS-LEVELS/EER-ENERGY-BATTERY/TFA/SYSTEMS/SE/
            .gitkeep
          2-DOMAINS-LEVELS/EER-ENERGY-BATTERY/TFA/SYSTEMS/SI/
            .gitkeep
    2-DOMAINS-LEVELS/IIF-INFRASTRUCTURE/
      2-DOMAINS-LEVELS/IIF-INFRASTRUCTURE/TFA/
        2-DOMAINS-LEVELS/IIF-INFRASTRUCTURE/TFA/COMPONENTS/
          2-DOMAINS-LEVELS/IIF-INFRASTRUCTURE/TFA/COMPONENTS/CC/
            .gitkeep
          2-DOMAINS-LEVELS/IIF-INFRASTRUCTURE/TFA/COMPONENTS/CE/
            .gitkeep
          2-DOMAINS-LEVELS/IIF-INFRASTRUCTURE/TFA/COMPONENTS/CI/
            .gitkeep
          2-DOMAINS-LEVELS/IIF-INFRASTRUCTURE/TFA/COMPONENTS/CP/
            .gitkeep
          2-DOMAINS-LEVELS/IIF-INFRASTRUCTURE/TFA/COMPONENTS/CV/
            .gitkeep
        2-DOMAINS-LEVELS/IIF-INFRASTRUCTURE/TFA/ELEMENTS/
          2-DOMAINS-LEVELS/IIF-INFRASTRUCTURE/TFA/ELEMENTS/FE/
            .gitkeep
        2-DOMAINS-LEVELS/IIF-INFRASTRUCTURE/TFA/META/
          README.md
        2-DOMAINS-LEVELS/IIF-INFRASTRUCTURE/TFA/STATES/
          2-DOMAINS-LEVELS/IIF-INFRASTRUCTURE/TFA/STATES/QS/
            .gitkeep
        2-DOMAINS-LEVELS/IIF-INFRASTRUCTURE/TFA/SYSTEMS/
          2-DOMAINS-LEVELS/IIF-INFRASTRUCTURE/TFA/SYSTEMS/DI/
            .gitkeep
          2-DOMAINS-LEVELS/IIF-INFRASTRUCTURE/TFA/SYSTEMS/SE/
            .gitkeep
          2-DOMAINS-LEVELS/IIF-INFRASTRUCTURE/TFA/SYSTEMS/SI/
            .gitkeep
    2-DOMAINS-LEVELS/IIS-AI-SYSTEMS/
      2-DOMAINS-LEVELS/IIS-AI-SYSTEMS/TFA/
        2-DOMAINS-LEVELS/IIS-AI-SYSTEMS/TFA/COMPONENTS/
          2-DOMAINS-LEVELS/IIS-AI-SYSTEMS/TFA/COMPONENTS/CC/
            .gitkeep
          2-DOMAINS-LEVELS/IIS-AI-SYSTEMS/TFA/COMPONENTS/CE/
            .gitkeep
          2-DOMAINS-LEVELS/IIS-AI-SYSTEMS/TFA/COMPONENTS/CI/
            .gitkeep
          2-DOMAINS-LEVELS/IIS-AI-SYSTEMS/TFA/COMPONENTS/CP/
            .gitkeep
          2-DOMAINS-LEVELS/IIS-AI-SYSTEMS/TFA/COMPONENTS/CV/
            .gitkeep
        2-DOMAINS-LEVELS/IIS-AI-SYSTEMS/TFA/ELEMENTS/
          2-DOMAINS-LEVELS/IIS-AI-SYSTEMS/TFA/ELEMENTS/FE/
            .gitkeep
        2-DOMAINS-LEVELS/IIS-AI-SYSTEMS/TFA/META/
          README.md
        2-DOMAINS-LEVELS/IIS-AI-SYSTEMS/TFA/STATES/
          2-DOMAINS-LEVELS/IIS-AI-SYSTEMS/TFA/STATES/QS/
            .gitkeep
        2-DOMAINS-LEVELS/IIS-AI-SYSTEMS/TFA/SYSTEMS/
          2-DOMAINS-LEVELS/IIS-AI-SYSTEMS/TFA/SYSTEMS/DI/
            .gitkeep
          2-DOMAINS-LEVELS/IIS-AI-SYSTEMS/TFA/SYSTEMS/SE/
            .gitkeep
          2-DOMAINS-LEVELS/IIS-AI-SYSTEMS/TFA/SYSTEMS/SI/
            .gitkeep
    2-DOMAINS-LEVELS/LCC-CONTROLS-COMMS/
      2-DOMAINS-LEVELS/LCC-CONTROLS-COMMS/TFA/
        2-DOMAINS-LEVELS/LCC-CONTROLS-COMMS/TFA/COMPONENTS/
          2-DOMAINS-LEVELS/LCC-CONTROLS-COMMS/TFA/COMPONENTS/CC/
            .gitkeep
          2-DOMAINS-LEVELS/LCC-CONTROLS-COMMS/TFA/COMPONENTS/CE/
            .gitkeep
          2-DOMAINS-LEVELS/LCC-CONTROLS-COMMS/TFA/COMPONENTS/CI/
            .gitkeep
          2-DOMAINS-LEVELS/LCC-CONTROLS-COMMS/TFA/COMPONENTS/CP/
            .gitkeep
          2-DOMAINS-LEVELS/LCC-CONTROLS-COMMS/TFA/COMPONENTS/CV/
            .gitkeep
        2-DOMAINS-LEVELS/LCC-CONTROLS-COMMS/TFA/ELEMENTS/
          2-DOMAINS-LEVELS/LCC-CONTROLS-COMMS/TFA/ELEMENTS/FE/
            .gitkeep
        2-DOMAINS-LEVELS/LCC-CONTROLS-COMMS/TFA/META/
          README.md
        2-DOMAINS-LEVELS/LCC-CONTROLS-COMMS/TFA/STATES/
          2-DOMAINS-LEVELS/LCC-CONTROLS-COMMS/TFA/STATES/QS/
            .gitkeep
        2-DOMAINS-LEVELS/LCC-CONTROLS-COMMS/TFA/SYSTEMS/
          2-DOMAINS-LEVELS/LCC-CONTROLS-COMMS/TFA/SYSTEMS/DI/
            .gitkeep
          2-DOMAINS-LEVELS/LCC-CONTROLS-COMMS/TFA/SYSTEMS/SE/
            .gitkeep
          2-DOMAINS-LEVELS/LCC-CONTROLS-COMMS/TFA/SYSTEMS/SI/
            .gitkeep
    2-DOMAINS-LEVELS/LIB-LOGISTICS-CHAIN/
      2-DOMAINS-LEVELS/LIB-LOGISTICS-CHAIN/TFA/
        2-DOMAINS-LEVELS/LIB-LOGISTICS-CHAIN/TFA/COMPONENTS/
          2-DOMAINS-LEVELS/LIB-LOGISTICS-CHAIN/TFA/COMPONENTS/CC/
            .gitkeep
          2-DOMAINS-LEVELS/LIB-LOGISTICS-CHAIN/TFA/COMPONENTS/CE/
            .gitkeep
          2-DOMAINS-LEVELS/LIB-LOGISTICS-CHAIN/TFA/COMPONENTS/CI/
            .gitkeep
          2-DOMAINS-LEVELS/LIB-LOGISTICS-CHAIN/TFA/COMPONENTS/CP/
            .gitkeep
          2-DOMAINS-LEVELS/LIB-LOGISTICS-CHAIN/TFA/COMPONENTS/CV/
            .gitkeep
        2-DOMAINS-LEVELS/LIB-LOGISTICS-CHAIN/TFA/ELEMENTS/
          2-DOMAINS-LEVELS/LIB-LOGISTICS-CHAIN/TFA/ELEMENTS/FE/
            .gitkeep
        2-DOMAINS-LEVELS/LIB-LOGISTICS-CHAIN/TFA/META/
          README.md
        2-DOMAINS-LEVELS/LIB-LOGISTICS-CHAIN/TFA/STATES/
          2-DOMAINS-LEVELS/LIB-LOGISTICS-CHAIN/TFA/STATES/QS/
            .gitkeep
        2-DOMAINS-LEVELS/LIB-LOGISTICS-CHAIN/TFA/SYSTEMS/
          2-DOMAINS-LEVELS/LIB-LOGISTICS-CHAIN/TFA/SYSTEMS/DI/
            .gitkeep
          2-DOMAINS-LEVELS/LIB-LOGISTICS-CHAIN/TFA/SYSTEMS/SE/
            .gitkeep
          2-DOMAINS-LEVELS/LIB-LOGISTICS-CHAIN/TFA/SYSTEMS/SI/
            .gitkeep
    2-DOMAINS-LEVELS/MMM-MECHANICAL/
      2-DOMAINS-LEVELS/MMM-MECHANICAL/TFA/
        2-DOMAINS-LEVELS/MMM-MECHANICAL/TFA/COMPONENTS/
          2-DOMAINS-LEVELS/MMM-MECHANICAL/TFA/COMPONENTS/CC/
            .gitkeep
          2-DOMAINS-LEVELS/MMM-MECHANICAL/TFA/COMPONENTS/CE/
            .gitkeep
          2-DOMAINS-LEVELS/MMM-MECHANICAL/TFA/COMPONENTS/CI/
            .gitkeep
          2-DOMAINS-LEVELS/MMM-MECHANICAL/TFA/COMPONENTS/CP/
            .gitkeep
          2-DOMAINS-LEVELS/MMM-MECHANICAL/TFA/COMPONENTS/CV/
            .gitkeep
        2-DOMAINS-LEVELS/MMM-MECHANICAL/TFA/ELEMENTS/
          2-DOMAINS-LEVELS/MMM-MECHANICAL/TFA/ELEMENTS/FE/
            .gitkeep
        2-DOMAINS-LEVELS/MMM-MECHANICAL/TFA/META/
          README.md
        2-DOMAINS-LEVELS/MMM-MECHANICAL/TFA/STATES/
          2-DOMAINS-LEVELS/MMM-MECHANICAL/TFA/STATES/QS/
            .gitkeep
        2-DOMAINS-LEVELS/MMM-MECHANICAL/TFA/SYSTEMS/
          2-DOMAINS-LEVELS/MMM-MECHANICAL/TFA/SYSTEMS/DI/
            .gitkeep
          2-DOMAINS-LEVELS/MMM-MECHANICAL/TFA/SYSTEMS/SE/
            .gitkeep
          2-DOMAINS-LEVELS/MMM-MECHANICAL/TFA/SYSTEMS/SI/
            .gitkeep
    2-DOMAINS-LEVELS/OOO-OS-NAVIGATION/
      2-DOMAINS-LEVELS/OOO-OS-NAVIGATION/TFA/
        2-DOMAINS-LEVELS/OOO-OS-NAVIGATION/TFA/COMPONENTS/
          2-DOMAINS-LEVELS/OOO-OS-NAVIGATION/TFA/COMPONENTS/CC/
            .gitkeep
          2-DOMAINS-LEVELS/OOO-OS-NAVIGATION/TFA/COMPONENTS/CE/
            .gitkeep
          2-DOMAINS-LEVELS/OOO-OS-NAVIGATION/TFA/COMPONENTS/CI/
            .gitkeep
          2-DOMAINS-LEVELS/OOO-OS-NAVIGATION/TFA/COMPONENTS/CP/
            .gitkeep
          2-DOMAINS-LEVELS/OOO-OS-NAVIGATION/TFA/COMPONENTS/CV/
            .gitkeep
        2-DOMAINS-LEVELS/OOO-OS-NAVIGATION/TFA/ELEMENTS/
          2-DOMAINS-LEVELS/OOO-OS-NAVIGATION/TFA/ELEMENTS/FE/
            .gitkeep
        2-DOMAINS-LEVELS/OOO-OS-NAVIGATION/TFA/META/
          README.md
        2-DOMAINS-LEVELS/OOO-OS-NAVIGATION/TFA/STATES/
          2-DOMAINS-LEVELS/OOO-OS-NAVIGATION/TFA/STATES/QS/
            .gitkeep
        2-DOMAINS-LEVELS/OOO-OS-NAVIGATION/TFA/SYSTEMS/
          2-DOMAINS-LEVELS/OOO-OS-NAVIGATION/TFA/SYSTEMS/DI/
            .gitkeep
          2-DOMAINS-LEVELS/OOO-OS-NAVIGATION/TFA/SYSTEMS/SE/
            .gitkeep
          2-DOMAINS-LEVELS/OOO-OS-NAVIGATION/TFA/SYSTEMS/SI/
            .gitkeep
    2-DOMAINS-LEVELS/PPP-PROPULSION-FUEL/
      2-DOMAINS-LEVELS/PPP-PROPULSION-FUEL/TFA/
        2-DOMAINS-LEVELS/PPP-PROPULSION-FUEL/TFA/COMPONENTS/
          2-DOMAINS-LEVELS/PPP-PROPULSION-FUEL/TFA/COMPONENTS/CC/
            .gitkeep
          2-DOMAINS-LEVELS/PPP-PROPULSION-FUEL/TFA/COMPONENTS/CE/
            .gitkeep
          2-DOMAINS-LEVELS/PPP-PROPULSION-FUEL/TFA/COMPONENTS/CI/
            .gitkeep
          2-DOMAINS-LEVELS/PPP-PROPULSION-FUEL/TFA/COMPONENTS/CP/
            .gitkeep
          2-DOMAINS-LEVELS/PPP-PROPULSION-FUEL/TFA/COMPONENTS/CV/
            .gitkeep
        2-DOMAINS-LEVELS/PPP-PROPULSION-FUEL/TFA/ELEMENTS/
          2-DOMAINS-LEVELS/PPP-PROPULSION-FUEL/TFA/ELEMENTS/FE/
            .gitkeep
        2-DOMAINS-LEVELS/PPP-PROPULSION-FUEL/TFA/META/
          README.md
        2-DOMAINS-LEVELS/PPP-PROPULSION-FUEL/TFA/STATES/
          2-DOMAINS-LEVELS/PPP-PROPULSION-FUEL/TFA/STATES/QS/
            .gitkeep
        2-DOMAINS-LEVELS/PPP-PROPULSION-FUEL/TFA/SYSTEMS/
          2-DOMAINS-LEVELS/PPP-PROPULSION-FUEL/TFA/SYSTEMS/DI/
            .gitkeep
          2-DOMAINS-LEVELS/PPP-PROPULSION-FUEL/TFA/SYSTEMS/SE/
            .gitkeep
          2-DOMAINS-LEVELS/PPP-PROPULSION-FUEL/TFA/SYSTEMS/SI/
            .gitkeep
  3-PROJECTS-USE-CASES/
    .gitkeep
  4-RESEARCH-DEVELOPMENT/
    .gitkeep
  5-ARTIFACTS-IMPLEMENTATION/
    .gitkeep
    5-ARTIFACTS-IMPLEMENTATION/CODE/
      5-ARTIFACTS-IMPLEMENTATION/CODE/c/
        .gitkeep
      5-ARTIFACTS-IMPLEMENTATION/CODE/infranet/
        Makefile
        README.md
      5-ARTIFACTS-IMPLEMENTATION/CODE/julia/
        .gitkeep
      5-ARTIFACTS-IMPLEMENTATION/CODE/python/
        .gitkeep
      5-ARTIFACTS-IMPLEMENTATION/CODE/rust/
        .gitkeep
      5-ARTIFACTS-IMPLEMENTATION/CODE/solidity/
        .gitkeep
      5-ARTIFACTS-IMPLEMENTATION/CODE/typescript/
        .gitkeep
      5-ARTIFACTS-IMPLEMENTATION/CODE/xslt/
        .gitkeep
  6-UTCS-BLOCKCHAIN/
    .gitkeep
    utcs-blockchain-framework.md
    validate_utcs_mi.py
  7-GOVERNANCE/
    .gitkeep
    7-GOVERNANCE/COMMUNITY/
      .gitkeep
    7-GOVERNANCE/LICENSING/
      .gitkeep
    7-GOVERNANCE/OPEN-CALL/
      .gitkeep
    7-GOVERNANCE/POLICIES/
      .gitkeep
    7-GOVERNANCE/TOKEN-GOVERNANCE/
      7-GOVERNANCE/TOKEN-GOVERNANCE/community-proposals/
        .gitkeep
  8-RESOURCES/
    .gitkeep
    8-RESOURCES/ASSETS/
      .gitkeep
    8-RESOURCES/REFERENCES/
      .gitkeep
    8-RESOURCES/TEKNIA-TOKENS/
      8-RESOURCES/TEKNIA-TOKENS/integration-examples/
        .gitkeep
    8-RESOURCES/TEMPLATES/
      .gitkeep
```
