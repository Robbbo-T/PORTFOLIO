# TFA V2 Portfolio Management Makefile
# Scaffolding, validation, and maintenance commands

.PHONY: help scaffold check validate domains quantum-bridge master-progress clean

# Default target
help:
	@echo "🚀 TFA V2 Portfolio Management"
	@echo ""
	@echo "Available targets:"
	@echo "  scaffold         - Create missing TFA structure and implementation buckets"
	@echo "  check            - Run all validations"
	@echo "  validate         - Run TFA structure validator"
	@echo "  domains          - Show domain status"
	@echo "  quantum-bridge   - Create quantum-classical bridge code buckets"
	@echo "  master-progress  - Generate Master's Project progress report"
	@echo "  clean            - Remove temporary files"
	@echo "  help             - Show this help"

# Create complete TFA scaffolding (idempotent) + quantum bridge buckets
scaffold: quantum-bridge
	@echo "🏗️ Scaffolding TFA V2 structure..."
	@python3 scripts/scaffold_tfa.py
	@echo "✅ TFA scaffolding complete"

# Validate TFA structure
validate:
	@echo "🔍 Running TFA structure validation..."
	@python3 scripts/validate_tfa.py

# Aggregate checks
check: validate
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