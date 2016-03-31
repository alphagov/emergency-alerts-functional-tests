#!/bin/bash
#
# Run project tests
#
# NOTE: This script expects to be run from the project root with
# ./scripts/run_tests.sh

# Use default environment vars for localhost if not already set

set -o pipefail
source environment.sh

function display_result {
  RESULT=$1
  EXIT_STATUS=$2
  TEST=$3

  if [ $RESULT -ne 0 ]; then
    echo -e "\033[31m$TEST failed\033[0m"
    exit $EXIT_STATUS
  else
    echo -e "\033[32m$TEST passed\033[0m"
  fi
}

pep8 .
display_result $? 1 "Code style check"

## Code coverage
#py.test --cov=app tests/
#display_result $? 2 "Code coverage"
if [ "$#" -eq 1 ]; then
	export ENVIRONMENT=$1
	if [ $1 = "live" ]; then
		py.test -v tests/test_signin_flow.py tests/test_csv_upload_flow.py
	elif [ $1 = "preview" ]; then
		py.test -v
	else
		echo -e "Invalid environment '$1' argument."
		exit 3
	fi
else
	py.test -v
fi
#
display_result $? 3 "Unit tests"

