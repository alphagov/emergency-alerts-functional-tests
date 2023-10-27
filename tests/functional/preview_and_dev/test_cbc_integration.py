import uuid

import boto3
import pytest

from config import config
from tests.pages.rollups import approve_alert, cancel_alert, create_alert
from tests.test_utils import recordtime

# from boto3.dynamodb.conditions import Key, Attr


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

    ddbc = boto3.client("dynamodb", region_name="eu-west-2")
    response = ddbc.query(
        TableName="test",
        KeyConditionExpression="RequestId = :RequestId",
        ExpressionAttributeValues={
            ":RequestId": {"S": "0d240e70-922a-4170-b1d4-df64ea8442e6"},
        },
    )

    assert len(response["Items"]) > 0

    cancel_alert(driver, id)
