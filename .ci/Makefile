.PHONY: bootstrap test schema brex invariants trips qs arp extensions

bootstrap:
	python3 -m pip install -r requirements-dev.txt -q

test: bootstrap schema brex invariants trips qs arp extensions

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
	pytest -q tests/test_arp4761x_propagation.py
	pytest -q tests/test_arp4761x_stl_sanity.py
	pytest -q tests/test_qb_result_contract.py
	pytest -q tests/test_qb_result_contract_negative.py
	pytest -q tests/test_qb_orchestration.py
	pytest -q tests/test_fe_contracts.py
	pytest -q tests/test_fe_security_policy.py
