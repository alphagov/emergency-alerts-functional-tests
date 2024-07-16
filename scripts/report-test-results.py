import json
import os
import sys
from xml.dom.minidom import Node, parse


def main():
    if len(sys.argv) < 3:
        print("Usage: python report-test-results.py working-dir testsuite-list")
        sys.exit(1)

    working_dir = sys.argv[1]
    test_file_names = sys.argv[2:]
    test_files = [
        working_dir + "/functional-test-reports/" + filename
        for filename in test_file_names
    ]

    if not len(test_files):
        print("Please provide a list of test files")
        sys.exit(1)

    artefact_bucket = get_smoke_test_bucket_name()

    failed_tests = []

    for test_file in test_files:
        test_results = extract_test_result(parse(test_file))
        for r in test_results:
            success = "PASS" if len(r) < 4 else "FAIL"

            result = f"PRV-FT-{r[0].upper()} | {success} | NAME: {r[1]} | TIME: {r[2]}"

            if len(r) > 3:
                result = result + f" | ERROR: {r[3]} | FILE: {r[4]}"
                if artefact_bucket is not None:
                    result = result + f" | Test output bucket: {artefact_bucket}"

            if success == "FAIL":
                failed_tests.append(f"- {r[1]}: {r[3]}\n")

            print(result.replace("\n", " "), sep="")

    print(failed_tests)
    log_final_results(failed_tests=failed_tests)


def log_final_results(failed_tests):
    if len(failed_tests) > 3:
        failed_tests_count = len(failed_tests)
        failed_tests = failed_tests[:3]
        failed_tests = failed_tests.append(f"- ...{failed_tests_count} more failed.")

    print(
        json.dumps(
            {
                "status": "FAILED" if failed_tests else "PASSED",
                "failures": failed_tests,
            },
            indent=4,
        )
    )


def extract_test_result(document):
    test_results = document.getElementsByTagName("testcase")

    results = []

    for result in test_results:
        test_identifier = result.getAttribute("name")
        (test_name, test_group) = test_identifier.split("@")
        test_time = result.getAttribute("time")

        failure = result.getElementsByTagName("failure")
        error = result.getElementsByTagName("error")

        test_failure = None
        if len(failure) > 0:
            test_failure = failure[0]
        elif len(error) > 0:
            test_failure = error[0]

        failure_message, failure_summary = extract_failure_detail(test_failure)

        if failure_message is not None or failure_summary is not None:
            results.append(
                (test_group, test_name, test_time, failure_summary, failure_message)
            )
        else:
            results.append((test_group, test_name, test_time))

    return results


def extract_failure_detail(failure):
    if failure is None:
        return (None, None)

    if failure.hasAttribute("message"):
        failure_message = failure.getAttribute("message").replace("\n", " ")

    if failure.hasChildNodes:
        node = failure.firstChild
        if node.nodeType == Node.TEXT_NODE:
            text = node.nodeValue
            last_line = extract_last_line(text)
            failure_summary = extract_failure_summary(last_line)

    return (failure_summary, failure_message)


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


def get_smoke_test_bucket_name():
    return os.environ.get("FUNCTIONAL_TEST_ARTEFACT_BUCKET_NAME")


if __name__ == "__main__":
    main()
