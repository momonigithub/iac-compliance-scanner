# Makefile for IaC Compliance Scanner

PYTHON = python3
SCANNER_DIR = scanner
TERRAFORM_DIR = terraform

.PHONY: all scan report clean install help seed

all: install scan report

install:
	pip install -r requirements.txt

scan:
	$(PYTHON) $(SCANNER_DIR)/scan.py

report:
	$(PYTHON) $(SCANNER_DIR)/report.py

seed:
	$(PYTHON) scripts/seed_history.py

clean:
	rm -rf reports/*.json reports/*.html db/scan_history.db

help:
	@echo "Available commands:"
	@echo "  make install - Install dependencies"
	@echo "  make scan    - Run compliance scan"
	@echo "  make report  - Generate HTML report"
	@echo "  make seed    - Seed database with demo data"
	@echo "  make clean   - Remove reports and database"
	@echo "  make all     - Install, scan, and report"
