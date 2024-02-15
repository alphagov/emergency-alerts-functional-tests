#! /bin/bash

text=$(cat)

# Look for non-zero errors or failures
pattern='(errors|failures)="([1-9][0-9]*)"'

# Check if the string matches the pattern
if [[ $text =~ $pattern ]]; then
    echo "Non-passing tests found. Exiting with status 1."
    exit 1
else
    echo "All tests green."
fi
