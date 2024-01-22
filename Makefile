.DEFAULT_GOAL := help
SHELL := /bin/bash

.PHONY: help
help:
	@cat $(MAKEFILE_LIST) | grep -E '^[a-zA-Z_-]+:.*?## .*$$' | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: bootstrap
bootstrap: ## Install build dependencies
	mkdir -p logs screenshots functional-test-reports
	pip install -r requirements.txt

# .PHONY: clean
# clean: ## Remove temporary files
# 	rm -rf screenshots/*
# 	rm -rf logs/*
# 	rm -rf functional-test-reports/*

.PHONY: lint
lint:
	isort --check-only tests
	flake8 .
	black --check .

.PHONY: test-broadcast-flow
test-broadcast-flow:
	pytest -v -n auto --dist loadgroup \
	tests/functional/preview_and_dev/test_broadcast_flow.py \
	--junitxml=functional-test-reports/broadcast-flow.xml

.PHONY: test-platform-admin-flow
test-platform-admin-flow:
	pytest -v -n auto --dist loadgroup \
	tests/functional/preview_and_dev/test_platform_admin_flow.py \
	--junitxml=functional-test-reports/platform-admin-flow.xml

.PHONY: test-cbc-integration
test-cbc-integration:
	pytest -v -n auto --dist loadgroup \
	tests/functional/preview_and_dev/test_cbc_integration.py \
	--junitxml=functional-test-reports/cbc-integration.xml
