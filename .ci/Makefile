.PHONY: test schema brex invariants trips qs arp extensions

test: schema brex invariants trips qs arp extensions

schema:
	pytest -q tests/test_schema_spec.py

brex:
	pytest -q tests/test_brex_and_contracts.py

invariants:
	pytest -q tests/test_invariants.py -k "surgesafe or vbus or fc_ramp"

trips:
	pytest -q tests/test_safety_cage.py

qs:
	pytest -q tests/test_qs_anchor.py

arp:
	pytest -q tests/test_hazard_linkage.py

extensions:
	pytest -q tests/test_arp4761x_propagation.py tests/test_qb_result_contract.py tests/test_fe_contracts.py