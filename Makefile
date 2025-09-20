# TFA V2 Portfolio Management Makefile
# Scaffolding, validation, and maintenance commands

.PHONY: help scaffold check validate domains quantum-bridge master-progress clean \
bootstrap pre-commit-install lint test canonical-plan canonical-apply canonical-verify ci

PY := python

# Default target
help:
	@echo "🚀 TFA V2 Portfolio Management"
	@echo ""
	@echo "Available targets:"
	@echo "  bootstrap        - Install/upgrade core Python tooling"
	@echo "  pre-commit-install - Install pre-commit hooks"
	@echo "  lint             - Run canonical extension lint checks"
	@echo "  test             - Execute pytest suite"
	@echo "  canonical-plan   - Preview canonical extension migration"
	@echo "  canonical-apply  - Apply canonical extension migration"
	@echo "  canonical-verify - Ensure no pending canonical renames"
	@echo "  ci               - Run lint, tests, and canonical verification"
	@echo "  scaffold         - Create missing TFA structure and implementation buckets"
	@echo "  check            - Run all validations"
	@echo "  validate         - Run TFA structure validator"
	@echo "  domains          - Show domain status"
	@echo "  quantum-bridge   - Create quantum-classical bridge code buckets"
	@echo "  master-progress  - Generate Master's Project progress report"
	@echo "  clean            - Remove temporary files"
	@echo "  help             - Show this help"

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
	@find 2-DOMAINS-LEVELS -maxdepth 1 -type d -name "*-*" | sort | while read -r domain; do \
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

# Idempotent scaffolding for CQH domain
.PHONY: scaffold-cqh
scaffold-cqh:
	@echo "Scaffolding CQH-CRYOGENICS-QUANTUM-AND-H2 domain..."
	# Create TFA layer directories (if they don't exist)
	mkdir -p 2-DOMAINS-LEVELS/CQH-CRYOGENICS-QUANTUM-AND-H2/TFA/ \
	         2-DOMAINS-LEVELS/CQH-CRYOGENICS-QUANTUM-AND-H2/TFA/SYSTEMS/DI \
	         2-DOMAINS-LEVELS/CQH-CRYOGENICS-QUANTUM-AND-H2/TFA/SYSTEMS/SI \
	         2-DOMAINS-LEVELS/CQH-CRYOGENICS-QUANTUM-AND-H2/TFA/STATIONS/SE \
	         2-DOMAINS-LEVELS/CQH-CRYOGENICS-QUANTUM-AND-H2/TFA/COMPONENTS/CV \
	         2-DOMAINS-LEVELS/CQH-CRYOGENICS-QUANTUM-AND-H2/TFA/COMPONENTS/CE \
	         2-DOMAINS-LEVELS/CQH-CRYOGENICS-QUANTUM-AND-H2/TFA/COMPONENTS/CC \
	         2-DOMAINS-LEVELS/CQH-CRYOGENICS-QUANTUM-AND-H2/TFA/COMPONENTS/CI \
	         2-DOMAINS-LEVELS/CQH-CRYOGENICS-QUANTUM-AND-H2/TFA/COMPONENTS/CP \
	         2-DOMAINS-LEVELS/CQH-CRYOGENICS-QUANTUM-AND-H2/TFA/BITS/CB \
	         2-DOMAINS-LEVELS/CQH-CRYOGENICS-QUANTUM-AND-H2/TFA/QUBITS/QB \
	         2-DOMAINS-LEVELS/CQH-CRYOGENICS-QUANTUM-AND-H2/TFA/ELEMENTS/UE \
	         2-DOMAINS-LEVELS/CQH-CRYOGENICS-QUANTUM-AND-H2/TFA/ELEMENTS/FE \
	         2-DOMAINS-LEVELS/CQH-CRYOGENICS-QUANTUM-AND-H2/TFA/WAVES/FWD \
	         2-DOMAINS-LEVELS/CQH-CRYOGENICS-QUANTUM-AND-H2/TFA/STATES/QS \
	         2-DOMAINS-LEVELS/CQH-CRYOGENICS-QUANTUM-AND-H2/TFA/META
	# Add META/README.md if not present
	@if [ ! -f "2-DOMAINS-LEVELS/CQH-CRYOGENICS-QUANTUM-AND-H2/TFA/META/README.md" ]; then \
	    echo "# CQH Domain TFA Structure" > 2-DOMAINS-LEVELS/CQH-CRYOGENICS-QUANTUM-AND-H2/TFA/META/README.md; \
	    echo "(Placeholder README for CQH domain)" >> 2-DOMAINS-LEVELS/CQH-CRYOGENICS-QUANTUM-AND-H2/TFA/META/README.md; \
	    echo "Added META/README.md placeholder."; \
	fi
	@echo "CQH domain scaffolding complete."

# Include shared TFA scaffolding/validation targets
include 8-RESOURCES/TEMPLATES/makefile.snippets.mk
