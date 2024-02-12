import os
import sys

import requests


def main():
    if len(sys.argv) < 3:
        print("Usage: python report-test-failures.py filename zendesk_url zendesk_key")
        sys.exit(0)

    input = sys.argv[1]

    if not os.path.exists(input):
        print("Please provide both an input and output file")
        sys.exit(0)

    with open(input, "r") as input_file:
        failures = input_file.read()

    if not failures:
        dispatch_zendesk_notification({"comment": failures})


def dispatch_zendesk_notification(body):
    zendesk_url = sys.argv[2]
    zendesk_key = sys.argv[3]

    data = {
        "ticket": {
            "subject": "Functional Test Failures",
            "description": "The following functional tests have reported failures",
            "comment": {"body": f"{body}"},
            "priority": "normal",
        }
    }

    response = requests.post(
        zendesk_url,
        data=data,
        headers={
            "Authorization": f"Token {zendesk_key}",
            "Content-Type": "application/json",
        },
    )
    response.raise_for_status()


if __name__ == "__main__":
    main()
