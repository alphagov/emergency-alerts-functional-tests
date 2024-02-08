#! /bin/bash

# Look for non-zero errors or failures
# pattern='\b(?:errors|failures)="([1-9][0-9]*)"\b'

# Specify the file to scan
# if [ -e "$1" ]; then
#     echo "Test output file found: $1"
# else
#     echo "Test output file $1 does not exist"
#     exit 1
# fi

# # Use grep to search for matches in the file
# if grep -q -E "$pattern" "$1"; then
#     echo "Non-passing tests found. Exiting with status 1."
#     exit 1
# else
#     echo "All tests green."
# fi

# exit 0

text=$(cat)

echo "$text"

# Look for non-zero errors or failures
pattern='\b(?:errors|failures)="([1-9][0-9]*)"\b'

# Check if the string matches the pattern
if [[ $text =~ $pattern ]]; then
    echo "Non-passing tests found. Exiting with status 1."
    exit 1
else
    echo "All tests green."
fi
