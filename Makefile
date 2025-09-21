# TFA V2 Portfolio Management Makefile
# Scaffolding, validation, and maintenance commands

# Canonical Project Slug
PROJECT_SLUG ?= robbbo-t-asi-t-transition
PYTHON_PKG = robbbot_asi_t_transition
K8S_NAMESPACE = robbbot-asi-t-tr

# Docker Configuration
GITHUB_OWNER ?= Robbbo-T
GIT_REF ?= $(shell git rev-parse --short HEAD 2>/dev/null || echo dev)
IMAGE_NAME ?= $(PROJECT_SLUG)
IMAGE_TAG ?= $(GIT_REF)
IMAGE ?= ghcr.io/$(GITHUB_OWNER)/$(IMAGE_NAME):$(IMAGE_TAG)

.PHONY: help print-vars scaffold check validate domains quantum-bridge master-progress clean \
bootstrap pre-commit-install lint test canonical-plan canonical-apply canonical-verify ci \
docker-build docker-push scaffold-llc-readmes mod-base mod-stack \
genesis.check genesis.ci lint-names

PY := python

# Default target
help:
	@echo "🚀 TFA V2 Portfolio Management"
	@echo ""
	@echo "Available targets:"
	@echo "  print-vars       - Show canonical project variables"
	@echo "  bootstrap        - Install/upgrade core Python tooling"
	@echo "  pre-commit-install - Install pre-commit hooks"
	@echo "  lint             - Run canonical extension lint checks"
	@echo "  test             - Execute pytest suite"
	@echo "  canonical-plan   - Preview canonical extension migration"
	@echo "  canonical-apply  - Apply canonical extension migration"
	@echo "  canonical-verify - Ensure no pending canonical renames"
	@echo "  ci               - Run lint, tests, and canonical verification"
	@echo "  scaffold         - Create missing TFA structure and implementation buckets"
	@echo "  scaffold-llc-readmes - Generate or update all canonical READMEs within TFA/LLC layers"
	@echo "  check            - Run all validations"
	@echo "  validate         - Run TFA structure validator"
	@echo "  domains          - Show domain status"
	@echo "  quantum-bridge   - Create quantum-classical bridge code buckets"
	@echo "  mod-base         - Run MOD-BASE baseline model"
	@echo "  mod-stack        - Run MOD-STACK composition and execution"
	@echo "  docker-build     - Build Docker image with canonical naming"
	@echo "  docker-push      - Push Docker image to registry"
	@echo "  master-progress  - Generate Master's Project progress report"
	@echo "  clean            - Remove temporary files"
	@echo "  genesis.check    - Run Genesis validation checks (path grammar, UTCS headers, FCR, evidence)"
	@echo "  genesis.ci       - Run full Genesis CI suite locally"
	@echo "  lint-names       - Validate file naming conventions"
	@echo "  help             - Show this help"

print-vars:
	@echo "Project Slug: $(PROJECT_SLUG)"
	@echo "Python Package: $(PYTHON_PKG)"
	@echo "K8s Namespace: $(K8S_NAMESPACE)"
	@echo "Docker Image: $(IMAGE)"

bootstrap:
	$(PY) -m pip install --upgrade pip -q
	$(PY) -m pip install -q pyyaml pre-commit pytest hypothesis

pre-commit-install: bootstrap
	pre-commit install -t pre-commit -t pre-push

lint:
	$(PY) tools/lint_extensions.py

test:
	pytest -q

canonical-plan: bootstrap
	@$(PY) tools/migrate_extensions.py || true

canonical-apply: bootstrap
	@$(PY) tools/check_git_clean.py
	@git switch -c chore/canonical-extensions 2>/dev/null || git switch chore/canonical-extensions
	$(PY) tools/migrate_extensions.py --apply
	pre-commit run -a || true
	git add -A
	git commit -m "chore: normalize extensions per policy" || true
	@echo "✔ canonical-apply done. Revisa el diff y sube PR."

canonical-verify: bootstrap
	@$(PY) tools/migrate_extensions.py && echo "OK: no pending canonical renames"

ci: bootstrap lint test canonical-verify
	@echo "CI pack OK"

# Create complete TFA scaffolding (idempotent) + quantum bridge buckets
scaffold:: quantum-bridge
	@echo "🏗️ Scaffolding TFA V2 structure..."
	@python3 scripts/scaffold_tfa.py
	@echo "✅ TFA scaffolding complete"

# Validate TFA structure
validate:
	@echo "🔍 Running TFA structure validation..."
	@python3 scripts/validate_tfa.py

# Alias for GitHub Actions workflow
validate-tfa: validate

# Run quantum layers consistency check
check-quantum-layers:
	@echo "🔬 Running quantum layers consistency check..."
	@python3 scripts/validate_tfa.py

# Aggregate checks
check:: validate
	@echo "🎯 All checks passed!"

# Show domain status
domains:
	@echo "📊 Domain Status Report:"
	@echo ""
	@find portfolio/2-DOMAINS-LEVELS -maxdepth 1 -type d -name "*-*" | sort | while read -r domain; do \
		domain_name=$$(basename "$$domain"); \
		if [ -d "$$domain/TFA" ]; then \
			layers=$$(find "$$domain/TFA" -maxdepth 1 -type d | wc -l); \
			layers=$$((layers - 1)); \
			echo "✅ $$domain_name ($$layers layers)"; \
		else \
			echo "❌ $$domain_name (no TFA)"; \
		fi; \
	done

# Create quantum-classical bridge implementation buckets
quantum-bridge:
	@echo "⚛️ Creating quantum-classical bridge code buckets..."
	@mkdir -p 5-ARTIFACTS-IMPLEMENTATION/CODE/python/classical-bits
	@mkdir -p 5-ARTIFACTS-IMPLEMENTATION/CODE/python/quantum-qubits
	@mkdir -p 5-ARTIFACTS-IMPLEMENTATION/CODE/python/unit-elements
	@mkdir -p 5-ARTIFACTS-IMPLEMENTATION/CODE/python/federation-elements
	@mkdir -p 5-ARTIFACTS-IMPLEMENTATION/CODE/python/wave-dynamics
	@[ -f 5-ARTIFACTS-IMPLEMENTATION/CODE/python/classical-bits/README.md ] || echo "# Classical Bit Implementations" > 5-ARTIFACTS-IMPLEMENTATION/CODE/python/classical-bits/README.md
	@[ -f 5-ARTIFACTS-IMPLEMENTATION/CODE/python/quantum-qubits/README.md ] || echo "# Quantum Qubit Implementations" > 5-ARTIFACTS-IMPLEMENTATION/CODE/python/quantum-qubits/README.md
	@[ -f 5-ARTIFACTS-IMPLEMENTATION/CODE/python/unit-elements/README.md ] || echo "# Unit Element Implementations" > 5-ARTIFACTS-IMPLEMENTATION/CODE/python/unit-elements/README.md
	@[ -f 5-ARTIFACTS-IMPLEMENTATION/CODE/python/federation-elements/README.md ] || echo "# Federation Entanglement Implementations" > 5-ARTIFACTS-IMPLEMENTATION/CODE/python/federation-elements/README.md
	@[ -f 5-ARTIFACTS-IMPLEMENTATION/CODE/python/wave-dynamics/README.md ] || echo "# Wave Dynamics Implementations" > 5-ARTIFACTS-IMPLEMENTATION/CODE/python/wave-dynamics/README.md
	@echo "✅ Quantum-classical bridge buckets ready"

# Master's Project Progress Report
master-progress:
	@echo "📊 Generating Master's Project Progress Report..."
	@python3 scripts/generate_master_progress_report.py
	@echo "✅ Progress report generated: 0-STRATEGY/MASTER-PROJECT-FRAMEWORK/PROGRESS-REPORT.md"

# Clean temporary files
clean:
	@echo "🧹 Cleaning temporary files..."
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@find . -name ".DS_Store" -delete 2>/dev/null || true
	@echo "✅ Cleanup complete"

# Docker build and push targets
docker-build:
	@echo "Building Docker image: $(IMAGE)..."
	@docker build -t $(IMAGE) . || true

docker-push:
	@echo "Pushing Docker image: $(IMAGE)..."
	@docker push $(IMAGE) || true

# Idempotent scaffolding for CQH domain
.PHONY: scaffold-cqh
scaffold-cqh:
	@echo "Scaffolding CQH-CRYOGENICS-QUANTUM-AND-H2 domain..."
	# Create TFA layer directories (if they don't exist)
	mkdir -p portfolio/2-DOMAINS-LEVELS/CQH-CRYOGENICS-QUANTUM-AND-H2/TFA/ \
	         portfolio/2-DOMAINS-LEVELS/CQH-CRYOGENICS-QUANTUM-AND-H2/TFA/SYSTEMS/DI \
	         portfolio/2-DOMAINS-LEVELS/CQH-CRYOGENICS-QUANTUM-AND-H2/TFA/SYSTEMS/SI \
	         portfolio/2-DOMAINS-LEVELS/CQH-CRYOGENICS-QUANTUM-AND-H2/TFA/STATIONS/SE \
	         portfolio/2-DOMAINS-LEVELS/CQH-CRYOGENICS-QUANTUM-AND-H2/TFA/COMPONENTS/CV \
	         portfolio/2-DOMAINS-LEVELS/CQH-CRYOGENICS-QUANTUM-AND-H2/TFA/COMPONENTS/CE \
	         portfolio/2-DOMAINS-LEVELS/CQH-CRYOGENICS-QUANTUM-AND-H2/TFA/COMPONENTS/CC \
	         portfolio/2-DOMAINS-LEVELS/CQH-CRYOGENICS-QUANTUM-AND-H2/TFA/COMPONENTS/CI \
	         portfolio/2-DOMAINS-LEVELS/CQH-CRYOGENICS-QUANTUM-AND-H2/TFA/COMPONENTS/CP \
	         portfolio/2-DOMAINS-LEVELS/CQH-CRYOGENICS-QUANTUM-AND-H2/TFA/BITS/CB \
	         portfolio/2-DOMAINS-LEVELS/CQH-CRYOGENICS-QUANTUM-AND-H2/TFA/QUBITS/QB \
	         portfolio/2-DOMAINS-LEVELS/CQH-CRYOGENICS-QUANTUM-AND-H2/TFA/ELEMENTS/UE \
	         portfolio/2-DOMAINS-LEVELS/CQH-CRYOGENICS-QUANTUM-AND-H2/TFA/ELEMENTS/FE \
	         portfolio/2-DOMAINS-LEVELS/CQH-CRYOGENICS-QUANTUM-AND-H2/TFA/WAVES/FWD \
	         portfolio/2-DOMAINS-LEVELS/CQH-CRYOGENICS-QUANTUM-AND-H2/TFA/STATES/QS \
	         portfolio/2-DOMAINS-LEVELS/CQH-CRYOGENICS-QUANTUM-AND-H2/TFA/META
	# Add META/README.md if not present
	@if [ ! -f "portfolio/2-DOMAINS-LEVELS/CQH-CRYOGENICS-QUANTUM-AND-H2/TFA/META/README.md" ]; then \
	    echo "# CQH Domain TFA Structure" > portfolio/2-DOMAINS-LEVELS/CQH-CRYOGENICS-QUANTUM-AND-H2/TFA/META/README.md; \
	    echo "(Placeholder README for CQH domain)" >> portfolio/2-DOMAINS-LEVELS/CQH-CRYOGENICS-QUANTUM-AND-H2/TFA/META/README.md; \
	    echo "Added META/README.md placeholder."; \
	fi
	@echo "CQH domain scaffolding complete."

# Include shared TFA scaffolding/validation targets
include 8-RESOURCES/TEMPLATES/makefile.snippets.mk

## Generates or updates all canonical READMEs within the TFA/LLC layers
scaffold-llc-readmes:
	@echo "🏛️ Scaffolding canonical LLC READMEs across all domains and CAx tracks..."
	@python tools/generate_llc_readmes.py
	@echo "✅ Canonical READMEs are up to date."

# MOD-BASE: Run baseline model
mod-base:
	@echo "🚀 Running MOD-BASE baseline model..."
	@$(PY) services/mod-base/run_mod_base.py \
		--spec services/mod-base/model_spec.yaml \
		--data services/mod-base/data/sample_flight_plan.csv \
		--out services/mod-base/eval/metrics.json
	@echo "✅ MOD-BASE execution completed"

# MOD-STACK: Apply stack and run composed model
mod-stack: mod-base
	@echo "🔄 Applying MOD-STACK composition..."
	@mkdir -p services/mod-base/stack/evidence
	@$(PY) services/mod-base/stack/apply_stack.py --stack services/mod-base/stack/stack.yaml
	@echo "✅ MOD-STACK composition completed"

# Genesis validation targets
genesis.check: bootstrap
	@echo "🔍 Genesis Validation Checks"
	@echo "========================================="
	@echo "📋 Path grammar & UTCS headers..."
	@$(PY) ASI-T/GENESIS/SCRIPTS/check_paths.py
	@echo "📋 Schema validation..."
	@$(PY) ASI-T/GENESIS/SCRIPTS/validate_schemas.py
	@echo "📋 Evidence linting..."
	@$(PY) ASI-T/GENESIS/SCRIPTS/evidence_lint.py
	@echo "📋 FCR enforcement..."
	@$(PY) ASI-T/GENESIS/SCRIPTS/fcr_enforcer.py
	@echo "✅ All Genesis checks passed"

genesis.ci: genesis.check
	@echo "🔄 Genesis CI Suite Complete"
	@echo "✅ Repository ready for Genesis compliance"

lint-names:
	@echo "🔍 Validating file naming conventions..."
	@$(PY) tools/validate_paths.py
	@echo "✅ File naming validation complete"
