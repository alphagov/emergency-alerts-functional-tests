import os
import sys
from xml.dom.minidom import Node, parse


def main():
    if len(sys.argv) < 2:
        print("Usage: python report-test-failures.py input output")
        sys.exit(0)

    input = sys.argv[1]
    output = sys.argv[2]

    if not os.path.exists(input) or not os.path.exists(output):
        print("Please provide both an input and output file")
        sys.exit(0)

    test_failures = extract_failures_summary(parse(input))

    with open(output, "a") as output_file:
        for t in test_failures:
            output_file.write(f"{t[0]} | NAME: {t[1]} | FILE: {t[2]} | ERROR: {t[3]}\n")


def extract_failures_summary(document):
    test_failures = document.getElementsByTagName("failure")

    failures = []
    for test_failure in test_failures:
        parent = test_failure.parentNode
        test_identifier = parent.getAttribute("name")
        (test_name, test_group) = test_identifier.split("@")

        if test_failure.hasAttribute("message"):
            message = test_failure.getAttribute("message")

        if test_failure.hasChildNodes:
            node = test_failure.firstChild
            if node.nodeType == Node.TEXT_NODE:
                text = node.nodeValue
                location = extract_last_line(text)

        if message is not None or location is not None:
            failures.append((test_group, test_name, location, message))

    return failures


def extract_last_line(s):
    if not s:
        return None

    lines = s.split("\n")
    return lines[-1].strip()


if __name__ == "__main__":
    main()
