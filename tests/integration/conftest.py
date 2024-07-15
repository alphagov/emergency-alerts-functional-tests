import time

import pytest

from config import setup_test_config
from tests.test_utils import (
    clear_proxy_error_alarm,
    put_functional_test_blackout_metric,
    set_response_codes,
)


@pytest.fixture(scope="session", autouse=True)
def integration_test_config():
    setup_test_config()


@pytest.fixture(scope="module")
def cbc_blackout():
    put_functional_test_blackout_metric(500)
    time.sleep(10)
    set_response_codes()
    yield
    set_response_codes()
    clear_proxy_error_alarm()
    time.sleep(90)
    put_functional_test_blackout_metric(200)
