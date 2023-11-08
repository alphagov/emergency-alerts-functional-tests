import uuid

import boto3
import pytest

from config import config
from tests.pages.rollups import broadcast_alert, cancel_alert
from tests.test_utils import get_broadcast_provider_messages, recordtime

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

        # https://admin.preview.emergency-alerts.service.gov.uk/services/de53ec2b-4324-4a63-a8a2-ef582fd538d8/current-alerts/42cc9c35-7f9b-43d1-989c-dd995f31766c

        url = driver.current_url.split("services/")[1]
        print("url: " + url)
        print(url.split("/current-alerts/"))
        service_id = url.split("/current-alerts/")[0]
        broadcast_message_id = url.split("/current-alerts/")[1]
        assert broadcast_message_id is not None
        print("service_id: " + service_id)
        print("broadcast_message_id: " + broadcast_message_id)

        print(
            "url: "
            + f'{config["notify_api_url"]}/service/{service_id}/'
            + f"broadcast-message/{broadcast_message_id}/provider-messages"
        )
        provider_messages = get_broadcast_provider_messages(
            service_id, broadcast_message_id
        )
        print("*******************************")
        print(provider_messages)
        # assert provider_messages is not None
        assert provider_messages is None

        # ddbc = create_ddb_client()
        # response = ddbc.query(
        #     TableName="LoopbackRequests",
        #     KeyConditionExpression="RequestId = :RequestId",
        #     ExpressionAttributeValues={
        #         ":RequestId": {"S": provider_messages[0].id},
        #     },
        # )

        # assert len(response["Items"]) > 0
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
