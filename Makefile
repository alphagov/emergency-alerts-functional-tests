.DEFAULT_GOAL := help
SHELL := /bin/bash

.PHONY: help
help:
	@cat $(MAKEFILE_LIST) | grep -E '^[a-zA-Z_-]+:.*?## .*$$' | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: bootstrap
bootstrap: ## Install build dependencies
	mkdir -p logs screenshots
	pip install -r requirements.txt

.PHONY: clean
clean: ## Remove temporary files
	rm -rf screenshots/*
	rm -rf logs/*

.PHONY: lint
lint: clean
	isort --check-only tests
	flake8 .
	black --check .

.PHONY: test
test: clean ## Run functional tests against local environment
	pytest -v tests/functional/preview_and_dev/test_broadcast_flow.py -n auto --dist loadgroup
