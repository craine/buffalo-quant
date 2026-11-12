PY ?= python3
.PHONY: ingest clean test report site all
ingest:
	$(PY) -m src.ingest.nflverse
clean:
	$(PY) -m src.clean.build
test: site
	$(PY) -m pytest -q tests
report:
	$(PY) -m src.reports.defense_baseline
site:
	$(PY) -m src.site.build
all: ingest clean test report site
