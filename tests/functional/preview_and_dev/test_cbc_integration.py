import time
import uuid

import boto3
import pytest
from boto3.dynamodb.conditions import Key

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


@recordtime
@pytest.mark.xdist_group(name="cbc-integration")
def test_get_loopback_response_with_bad_id_returns_no_items():
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
def test_broadcast_with_new_content(driver, api_client):
    id = str(uuid.uuid4())
    epoch = int(time.time())

    try:
        broadcast_alert(driver, id)

        alerturl = driver.current_url.split("services/")[1]

        service_id = alerturl.split("/current-alerts/")[0]
        broadcast_message_id = alerturl.split("/current-alerts/")[1]

        time.sleep(10)
        url = f"/service/{service_id}/broadcast-message/{broadcast_message_id}/provider-messages"
        response = api_client.get(url=url)
        assert response is not None

        messages = response["messages"]
        assert messages is not None

        print("broadcast_message_id: " + broadcast_message_id)
        print(messages)

        assert len(messages) == 4

        ddbc = create_ddb_client()

        key_condition_expression = Key("MnoName").eq(messages[0]["provider"]) & Key(
            "Timestamp"
        ).gt(epoch)

        db_response = ddbc.query(
            TableName="LoopbackRequests",
            KeyConditionExpression=key_condition_expression,
        )

        # db_response = ddbc.query(
        #     TableName="LoopbackRequests",
        #     KeyConditionExpression="MnoName = :MnoName",
        #     ExpressionAttributeValues={
        #         ":MnoName": {"S": messages[0]["provider"]},
        #     },
        # )

        print(db_response)

        assert len(db_response["Items"]) > 0

        assert messages is None  # force exception to allow capture of stdout

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
