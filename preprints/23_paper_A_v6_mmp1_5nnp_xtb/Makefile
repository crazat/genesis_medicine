## paper_A v6 pre-publish gate (Zenodo target 2026-05-30)
##
## Required passes:
##   make check          - run tools/check_tables.py against both manuscript versions
##   make check-paper-b  - run check_tables.py against companion paper_B v1
##   make check-all      - both
##
## A non-zero exit from any check blocks publish.

PY ?= python3
TOOL := tools/check_tables.py

.PHONY: check check-paper-b check-all

check:
	$(PY) $(TOOL) manuscript_v0.2.md manuscript_v0.1.md

check-paper-b:
	$(PY) $(TOOL) ../24_paper_B_v1_boltz_xtb_rescue_zn_mmp1/manuscript_skeleton_v0.1.md

check-all: check check-paper-b
