import os
import sys


def main():
    if len(sys.argv) < 1:
        print("Usage: python report-test-failures.py filename")
        sys.exit(0)

    input = sys.argv[1]

    if not os.path.exists(input):
        print("Please provide both an input and output file")
        sys.exit(0)

    with open(input, "r") as input_file:
        failures = input_file.readlines()

    for failure in failures:
        print("PRV-FT-", failure.replace("\n", " "), sep="")


if __name__ == "__main__":
    main()
