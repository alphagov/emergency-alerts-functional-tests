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

.PHONY: test-broadcast-flow
test-broadcast-flow:
	pytest -v \
	tests/functional/preview_and_dev/test_broadcast_flow.py::test_prepare_broadcast_with_new_content_for_postcode_area \
	--junitxml=functional-test-reports/broadcast-flow

.PHONY: test-cbc-integration
test-cbc-integration:
	pytest -v \
	tests/functional/preview_and_dev/test_cbc_integration.py \
	--junitxml=functional-test-reports/cbc-integration

.PHONY: test-platform-admin-flow
test-platform-admin-flow:
	pytest -v \
	tests/functional/preview_and_dev/test_platform_admin_flow.py \
	--junitxml=functional-test-reports/platform-admin-flow

.PHONY: test-authentication-flow
test-authentication-flow:
	pytest -v \
	tests/functional/preview_and_dev/test_authentication_flow.py \
	--junitxml=functional-test-reports/authentication-flow

.PHONY: test-top-rail-services
test-top-rail-services:
	pytest -v \
	tests/functional/preview_and_dev/test_top_rail_services.py \
	--junitxml=functional-test-reports/top-rail-services

.PHONY: test-links-and-cookies
test-links-and-cookies:
	pytest -v \
	tests/functional/preview_and_dev/test_links_and_cookies.py \
	--junitxml=functional-test-reports/links-and-cookies

.PHONY: test-template-flow
test-template-flow:
	pytest -v \
	tests/functional/preview_and_dev/test_template_flow.py \
	--junitxml=functional-test-reports/template-flow

.PHONY: test-user-operations
test-user-operations:
	pytest -v \
	tests/functional/preview_and_dev/test_user_operations.py \
	--junitxml=functional-test-reports/user-operations

.PHONY: test-throttling
test-throttling:
	pytest -v \
	tests/functional/preview_and_dev/test_throttling.py \
	--junitxml=functional-test-reports/throttling

.PHONY: test-session-timeout
test-session-timeout:
	pytest -v \
	tests/functional/preview_and_dev/test_session_timeout.py \
	--junitxml=functional-test-reports/session-timeout
