import uuid

import pytest

from config import config
from tests.pages.rollups import approve_alert, cancel_alert, create_alert
from tests.test_utils import recordtime


def test_cbc_config():
    assert "ee" in config["cbcs"]
    assert "vodafone" in config["cbcs"]
    assert "o2" in config["cbcs"]
    assert "three" in config["cbcs"]


@recordtime
@pytest.mark.xdist_group(name="cbc-integration")
def test_prepare_broadcast_with_new_content(driver):
    id = str(uuid.uuid4())
    create_alert(driver, id)
    approve_alert(driver, id)

    # do some stuff here

    cancel_alert(driver, id)
