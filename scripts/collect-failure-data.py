import os
import sys
from xml.dom.minidom import Node, parse


def main():
    if len(sys.argv) < 3:
        print("Usage: python report-test-failures.py working-dir testsuite-list")
        sys.exit(0)

    working_dir = sys.argv[1]
    failure_file = working_dir + "/test-failures"
    test_file_names = sys.argv[2:]
    test_files = [
        working_dir + "/functional-test-reports/" + filename
        for filename in test_file_names
    ]

    if not os.path.exists(failure_file) or not len(test_files):
        print("Please provide both an output file and a list of test files")
        sys.exit(0)

    for test_file in test_files:
        test_failures = extract_failure_descriptions(parse(test_file))

        with open(failure_file, "a") as output_file:
            for t in test_failures:
                output_file.write(
                    f"{t[0]} | NAME: {t[1]} | FILE: {t[2]} | ERROR: {t[3]}\n"
                )


def extract_failure_descriptions(document):
    test_failures = document.getElementsByTagName("failure")

    failures = []
    for test_failure in test_failures:
        parent = test_failure.parentNode
        test_identifier = parent.getAttribute("name")
        (test_name, test_group) = test_identifier.split("@")

        if test_failure.hasAttribute("message"):
            message = test_failure.getAttribute("message").replace("\n", " ")

        if test_failure.hasChildNodes:
            node = test_failure.firstChild
            if node.nodeType == Node.TEXT_NODE:
                text = node.nodeValue
                last_line = extract_last_line(text)
                summary = extract_failure_summary(last_line)

        if message is not None or summary is not None:
            failures.append((test_group, test_name, summary, message))

    return failures


def extract_last_line(s):
    if not s:
        return None

    lines = s.split("\n")
    return lines[-1].strip()


def extract_failure_summary(s):
    if not s:
        return None

    parts = s.split(":")
    return f"{parts[0]}, line {parts[1]}"


if __name__ == "__main__":
    main()
