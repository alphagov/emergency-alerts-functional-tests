.DEFAULT_GOAL := help
SHELL := /bin/bash

.PHONY: help
help:
	@cat $(MAKEFILE_LIST) | grep -E '^[a-zA-Z_-]+:.*?## .*$$' | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: bootstrap
bootstrap:
	mkdir -p logs screenshots functional-test-reports
	pip install -r requirements.txt
	playwright install chromium

.PHONY: lint
lint:
	isort --check-only tests
	flake8 .
	black --check .

.PHONY: uninstall-packages
uninstall-packages:
	python -m pip freeze | xargs python -m pip uninstall -y

.PHONY: test
test:
	pytest -v --junitxml=functional-test-reports/report.xml tests/
