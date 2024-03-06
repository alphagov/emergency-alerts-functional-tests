import re
import sys


def main():
    if len(sys.argv) < 3:
        print("Usage: python signal-build-pass-or-fail.py working-dir testsuite-list")
        sys.exit(0)

    working_dir = sys.argv[1]
    test_report_files = sys.argv[2:]
    test_reports = [
        working_dir + "/functional-test-reports/" + filename
        for filename in test_report_files
    ]

    pattern = r'(errors|failures)="([1-9][0-9]*)"'

    for test_report in test_reports:
        with open(test_report, "r") as file:
            report = file.read()
            if re.search(pattern, report):
                print("Non-passing tests found. Exiting with status 1.")
                sys.exit(1)


if __name__ == "__main__":
    main()
