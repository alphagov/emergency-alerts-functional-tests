# notifications-functional-tests

The tests are:

- `functional/`: tests of the Notify user interface and API (notifications.service.gov.uk)
- `document_download/`: tests of the Documents user interface and API (documents.service.gov.uk)
- `provider_delivery/`: tests for delivery of notifications (Staging and Production only)

These tests are run against preview, staging and production using Concourse. We run a full set of tests on preview but only a smaller set of tests, also known as smoke tests, on staging and production.

The Concourse jobs are defined in our [infrastructure repo](https://github.com/alphagov/notifications-aws/blob/master/concourse/templates/functional-tests.yml.j2).

## Uses

These tests are not intended to be used for load testing.

## Installation

```shell
brew install --cask chromedriver # needs to be >= v2.32

make bootstrap # install dependencies, etc.
```

Note: when you run the tests for the first time on a Mac, **you may need to authorise `chromedriver` in your security settings** ("System Preferences > Security & Privacy > General").

## Running tests

Note, there is an order dependency in the main tests. The registration test must run before any of the other tests as a new user account created for each test run. That user account is used for all later browser based tests. Each test run will first register a user account using the configured FUNCTIONAL_TEST_EMAIL. The email account will have random characters added so that we do not have uniqueness issues with the email address of registered user.

### Running the tests against your local development environment

**Note: this is currently only supported for `functional/` and `document_download/` tests.** See the next section if you want to run the `provider_delivery/` tests locally.

Populate the local database with fixture data:

```shell
psql notification_api -f db_setup_fixtures.sql
```

Note: If you see any errors (for example a `duplicate key value violates unique constraint` line or similar), that table will not be saved but other following table inserts will still attempt. You'll need to fix the errors for that table (either in your local database or in the fixture script) and run the script again, or open `psql` and just copy-paste the lines from the script that you need.

Now run the following in other tabs / windows:

- If you're testing the Notify user interface:

  - [notifications-api](https://github.com/alphagov/notifications-api):
    - Flask app (run `export ANTIVIRUS_ENABLED=1 first`)
    - Celery
  - [notifications-template-preview](https://github.com/alphagov/notifications-template-preview):
    - Flask app
    - Celery
  - [notifications-admin](https://github.com/alphagov/notifications-admin)
    - Flask app
  - [notifications-antivirus](https://github.com/alphagov/notifications-antivirus)
    - Celery

- If you're testing the Documents user interface:

  - [notifications-api](https://github.com/alphagov/notifications-api) (Flask app only)
  - [notifications-admin](https://github.com/alphagov/notifications-admin)
  - [document-download-api](https://github.com/alphagov/document-download-api)
  - [document-download-frontend](https://github.com/alphagov/document-download-frontend)

Then source the environment and run the tests:

```
source environment_local.sh

# run all the tests
make test

# run a specific test
pytest tests/functional/preview_and_dev/test_seeded_user.py
```

### Running the tests against preview, staging or production

Users with the required services and templates have already been set up for each of these environments. The details for these are found in our credentials repo, under `credentials/functional-tests`. There are different sets of credentials depending on the tests you want to run e.g. `staging-provider`, `staging-functional` . Decrypt the credentials you need and paste them locally in a separate file e.g. `environment_staging.sh`. Then:

```
source environment_{env_name}.sh

# run specific tests, for example:
pytest tests/document_download/preview_and_dev
```

### Running tests in parallel

We can reduce the duration of the test suite by running some tests in parallel.

We use the pytest [x-dist plugin](https://pypi.org/project/pytest-xdist/) to support running tests in parallel automatically. The number of test runners is determined automatically using the `pytest -n auto` option. This will be set to the number of CPUs available on the test machine.

Each test runner launches a separate selenium/chromedriver instance so browser state is isolated between runners.

#### Defining parallel groups

We execute tests in parallel groups using the `pytest --dist loadgroup` option. This allows us to group tests by the authenticated user type or other logical domain - this is useful for functional tests that rely on a particular state of a real user environment during execution.

Parallel tests executed using the same user type can cause race conditions and interfere with other tests. Tests belonging to different groups are executed in parallel. Each test within the same group is executed sequentially by the same test runner.

We use the following annotations on test methods to define the groups:

```python
@pytest.mark.xdist_group(name="seeded-user")
@pytest.mark.xdist_group(name="registration-flow")
@pytest.mark.xdist_group(name="api-client")
@pytest.mark.xdist_group(name="seeded-email")
@pytest.mark.xdist_group(name="broadcasts")
@pytest.mark.xdist_group(name="api-letters")
@pytest.mark.xdist_group(name="platform-admin")
```

More groups generally equals better parallelisation (limited by test runner count). However, in the case of functional tests, increased parallelisation increases the risk of side effects and race conditions in the shared environment unless grouped carefully.


## Pre-commit

We use [pre-commit](https://pre-commit.com/) to ensure that committed code meets basic standards for formatting, and will make basic fixes for you to save time and aggravation.

Install pre-commit system-wide with, eg `brew install pre-commit`. Then, install the hooks in this repository with `pre-commit install --install-hooks`.


## Further documentation

- [Updating db_setup_fixtures](docs/update-db_setup_fixtures.md)
- [Style guide](docs/style-guide.md)
