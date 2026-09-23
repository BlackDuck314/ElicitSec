.PHONY: validate test run-scan report

validate:
	elicitsec validate --all

test:
	pytest -q

run-scan:
	elicitsec run --suites suites --adapter mock --out results/local

report:
	elicitsec report --from results/local --out results/local/report.md
