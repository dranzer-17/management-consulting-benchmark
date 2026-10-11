# Reproduce the study. `make reproduce` uses the committed raw extracts (no network). `make ingest` re-downloads them.
PY ?= python

.PHONY: reproduce ingest check test web-data all
reproduce: ; $(PY) -m src.clean && $(PY) -m src.metrics && $(PY) -m src.figures && $(PY) -m src.render_sources && $(PY) -m src.export_web && $(PY) -m src.validate
check:     ; $(PY) -m src.validate
test:      ; $(PY) -m pytest -q
ingest:
	$(PY) -m src.ingest.h1b_lca
	$(PY) -m src.ingest.perm
	$(PY) -m src.ingest.usaspending_awards
	$(PY) -m src.ingest.usaspending_subawards
	$(PY) -m src.ingest.sec_edgar
	$(PY) -m src.ingest.uk_contracts
	$(PY) -m src.ingest.canada_contracts
	$(PY) -m src.ingest.austender
	$(PY) -m src.ingest.openalex
	$(PY) -m src.ingest.wikidata
	$(PY) -m src.ingest.site_inventory
	$(PY) -m src.ingest.attention
all: ingest reproduce test
