.PHONY: run test check db-init db-check db-backup

PYTHON ?= python3

run:
	$(PYTHON) app.py

test:
	$(PYTHON) -m unittest discover -v

check:
	$(PYTHON) -m compileall -q app.py kanban scripts tests
	$(PYTHON) -m unittest discover

db-init:
	$(PYTHON) scripts/db_admin.py init

db-check:
	$(PYTHON) scripts/db_admin.py check

db-backup:
	$(PYTHON) scripts/db_admin.py backup
