import uuid

import boto3
import pytest

from config import config
from tests.pages.rollups import broadcast_alert, cancel_alert
from tests.test_utils import recordtime

# from boto3.dynamodb.conditions import Key, Attr


def test_cbc_config():
    assert "ee" in config["cbcs"]
    assert "vodafone" in config["cbcs"]
    assert "o2" in config["cbcs"]
    assert "three" in config["cbcs"]


def create_ddb_client():
    try:
        sts_client = boto3.client("sts")

        sts_session = sts_client.assume_role(
            RoleArn="arn:aws:iam::519419547532:role/mno-loopback-database-access",
            RoleSessionName="access-loopback-for-functional-test",
        )

        KEY_ID = sts_session["Credentials"]["AccessKeyId"]
        ACCESS_KEY = sts_session["Credentials"]["SecretAccessKey"]
        TOKEN = sts_session["Credentials"]["SessionToken"]

        try:
            return boto3.client(
                "dynamodb",
                region_name="eu-west-2",
                aws_access_key_id=KEY_ID,
                aws_secret_access_key=ACCESS_KEY,
                aws_session_token=TOKEN,
            )

        except Exception as e:
            raise Exception("Unable to create DB client") from e

    except Exception as e:
        raise Exception("Unable to assume role") from e


def test_get_loopback_response_with_bad_id_fails():
    ddbc = create_ddb_client()
    response = ddbc.query(
        TableName="LoopbackRequests",
        KeyConditionExpression="RequestId = :RequestId",
        ExpressionAttributeValues={
            ":RequestId": {"S": "1234"},
        },
    )

    assert len(response["Items"]) == 0


@recordtime
@pytest.mark.xdist_group(name="cbc-integration")
def test_broadcast_with_new_content(driver):
    id = str(uuid.uuid4())

    try:
        broadcast_alert(driver, id)

        broadcast_message_id = driver.current_url.split("current-alerts/")[1]
        assert broadcast_message_id is not None

        # use broadcast message id to get list of
        # broadcast_provider_message ids

        broadcast_provider_message_id = "0d240e70-922a-4170-b1d4-df64ea8442e6"

        ddbc = create_ddb_client()
        response = ddbc.query(
            TableName="LoopbackRequests",
            KeyConditionExpression="RequestId = :RequestId",
            ExpressionAttributeValues={
                ":RequestId": {"S": broadcast_provider_message_id},
            },
        )

        assert len(response["Items"]) > 0
    finally:
        cancel_alert(driver, id)


@recordtime
@pytest.mark.xdist_group(name="cbc-integration")
def test_broadcast_with_new_content_with_primary_lambda_failure(driver):
    pass


@recordtime
@pytest.mark.xdist_group(name="cbc-integration")
def test_broadcast_with_new_content_with_site_a_failure(driver):
    pass


@recordtime
@pytest.mark.xdist_group(name="cbc-integration")
def test_broadcast_with_new_content_with_primary_lambda_and_site_a_failure(driver):
    pass
