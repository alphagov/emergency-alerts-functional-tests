import os
import re
import sys
from xml.dom.minidom import Node, parse

# import requests


def main():
    if len(sys.argv) < 3:
        print("Usage: python report-test-failures.py filename zendesk_url zendesk_key")
        sys.exit(0)

    if os.path.exists(sys.argv[1]):
        filename = sys.argv[1]
    else:
        sys.exit(0)

    # zendesk_url = sys.argv[2]
    # zendesk_key = sys.argv[3]

    test_failures = extract_failures_summary(parse(filename))

    body = ""
    for t in test_failures:
        body += f"Test Name: {t[0]}\nLocation: {t[1]}\nError: {t[2]}\n\n"

    dispatch_zendesk_notification({"comment": body})


def dispatch_zendesk_notification():
    pass


def extract_failures_summary(document):
    test_failures = document.getElementsByTagName("failure")

    failures = []
    for test_failure in test_failures:
        if test_failure.hasAttribute("message"):
            message = test_failure.getAttribute("message")

        if test_failure.hasChildNodes:
            node = test_failure.firstChild
            if node.nodeType == Node.TEXT_NODE:
                text = node.nodeValue
                test_name = extract_test_method_name(text)
                location = extract_last_line(text)

        if message is not None or location is not None:
            failures.append((test_name, location, message))

    return failures


def extract_test_method_name(s):
    match = re.search(r"def\s(.*?)\(", s)
    if match:
        return match.group(1)
    else:
        return None


def extract_last_line(s):
    if not s:
        return None

    lines = s.split("\n")
    return lines[-1].strip()


if __name__ == "__main__":
    main()
