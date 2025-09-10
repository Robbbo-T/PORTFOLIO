# Amedeo Pelliccia Portfolio - TFA V2 Makefile

.PHONY: scaffold check help

help:
	@echo "Available targets:"
	@echo "  scaffold  - Create any missing TFA folders (idempotent)"
	@echo "  check     - Validate full TFA structure + quantum layers"
	@echo "  help      - Show this help message"

scaffold:
	@python scripts/scaffold.py

check:
	@python scripts/validate_tfa.py