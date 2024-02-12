import os
import re
import sys
from xml.dom.minidom import Node, parse


def main():
    if len(sys.argv) < 2:
        print("Usage: python report-test-failures.py input output")
        sys.exit(0)

    if os.path.exists(sys.argv[1]):
        input = sys.argv[1]
    else:
        sys.exit(0)

    # create file

    test_failures = extract_failures_summary(parse(input))

    body = ""
    for t in test_failures:
        body += f"Test Name: {t[0]}\nLocation: {t[1]}\nError: {t[2]}\n\n"

    # write failure info to file


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
