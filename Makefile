.DEFAULT_GOAL := help
SHELL := /bin/bash

NVM_VERSION := 0.39.7
NODE_VERSION := 16.14.0

write-source-file:
	@if [ -f ~/.zshrc ]; then \
		if [[ $$(cat ~/.zshrc | grep "export NVM") ]]; then \
			cat ~/.zshrc | grep "export NVM" | sed "s/export//" > ~/.nvm-source; \
		else \
			cat ~/.bashrc | grep "export NVM" | sed "s/export//" > ~/.nvm-source; \
		fi \
	else \
		cat ~/.bashrc | grep "export NVM" | sed "s/export//" > ~/.nvm-source; \
	fi

read-source-file: write-source-file
	@for line in $$(cat ~/.nvm-source); do \
		export $$line; \
	done

	@echo '. "$$NVM_DIR/nvm.sh"' >> ~/.nvm-source;

	@current_nvm_version=$$(. ~/.nvm-source && nvm --version); \
	echo "NVM Versions (current/expected): $$current_nvm_version/$(NVM_VERSION)"; \
	echo "";

.PHONY: install-nvm
install-nvm:
	@echo ""
	@echo "[Install Node Version Manager]"
	@echo ""

	@if [ ! -f ~/.nvm-source ]; then \
		rm -rf $(NVM_DIR); \
		curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v$(NVM_VERSION)/install.sh | bash; \
		echo ""; \
	fi

	@$(MAKE) read-source-file

	@current_nvm_version=$$(. ~/.nvm-source && nvm --version); \
	if [[ "$(NVM_VERSION)" == "$$current_nvm_version" ]]; then \
		echo "No need up adjust NVM versions."; \
	else \
		rm -rf $(NVM_DIR); \
		curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v$(NVM_VERSION)/install.sh | bash; \
		echo ""; \
	fi

	@$(MAKE) read-source-file

.PHONY: install-node
install-node: install-nvm
	@echo ""
	@echo "[Install Node]"
	@echo ""

	@. ~/.nvm-source && nvm install $(NODE_VERSION) \
		&& nvm use $(NODE_VERSION) \
		&& nvm alias default $(NODE_VERSION);

.PHONY: help
help:
	@cat $(MAKEFILE_LIST) | grep -E '^[a-zA-Z_-]+:.*?## .*$$' | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: bootstrap
bootstrap: install-node ## Install build dependencies
	mkdir -p logs screenshots functional-test-reports
	pip install -r requirements.txt

.PHONY: lint
lint:
	isort --check-only tests
	flake8 .
	black --check .

.PHONY: test-broadcast-flow
test-broadcast-flow:
	pytest -v -n auto --dist=loadgroup \
	tests/functional/preview_and_dev/test_broadcast_flow.py \
	--junitxml=functional-test-reports/broadcast-flow

.PHONY: test-cbc-integration
test-cbc-integration:
	pytest -v -n auto --dist=loadgroup \
	tests/functional/preview_and_dev/test_cbc_integration.py \
	--junitxml=functional-test-reports/cbc-integration

.PHONY: test-platform-admin-flow
test-platform-admin-flow:
	pytest -v -n auto --dist=loadgroup \
	tests/functional/preview_and_dev/test_platform_admin_flow.py \
	--junitxml=functional-test-reports/platform-admin-flow

.PHONY: test-authentication-flow
test-authentication-flow:
	pytest -v -n auto --dist=loadgroup \
	tests/functional/preview_and_dev/test_authentication_flow.py \
	--junitxml=functional-test-reports/authentication-flow

.PHONY: test-top-rail-services
test-top-rail-services:
	pytest -v -n auto --dist=loadgroup \
	tests/functional/preview_and_dev/test_top_rail_services.py \
	--junitxml=functional-test-reports/top-rail-services

.PHONY: test-links-and-cookies
test-links-and-cookies:
	pytest -v -n auto --dist=loadgroup \
	tests/functional/preview_and_dev/test_links_and_cookies.py \
	--junitxml=functional-test-reports/links-and-cookies

.PHONY: test-template-flow
test-template-flow:
	pytest -v -n auto --dist=loadgroup \
	tests/functional/preview_and_dev/test_template_flow.py \
	--junitxml=functional-test-reports/template-flow

.PHONY: test-user-operations
test-user-operations:
	pytest -v -n auto --dist=loadgroup \
	tests/functional/preview_and_dev/test_user_operations.py \
	--junitxml=functional-test-reports/user-operations

.PHONY: test-throttling
test-throttling:
	pytest -v -n auto --dist=loadgroup \
	tests/functional/preview_and_dev/test_throttling.py \
	--junitxml=functional-test-reports/throttling

.PHONY: test-session-timeout
test-session-timeout:
	pytest -v -n auto --dist=loadgroup \
	tests/functional/preview_and_dev/test_session_timeout.py \
	--junitxml=functional-test-reports/session-timeout
