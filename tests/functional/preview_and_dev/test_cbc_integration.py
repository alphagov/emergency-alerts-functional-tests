# import time
# import uuid

import boto3
import pytest

from config import config

# from tests.pages.rollups import broadcast_alert, cancel_alert
from tests.test_utils import recordtime

# from boto3.dynamodb.conditions import Key, Attr


def test_cbc_config():
    assert "ee-az1" in config["cbcs"]
    assert "ee-az2" in config["cbcs"]
    assert "vodafone-az1" in config["cbcs"]
    assert "vodafone-az2" in config["cbcs"]
    assert "o2-az1" in config["cbcs"]
    assert "o2-az2" in config["cbcs"]
    assert "three-az1" in config["cbcs"]
    assert "three-az2" in config["cbcs"]


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
def test_get_loopback_request_with_bad_id_returns_no_items():
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
def test_get_loopback_responses_returns_codes_for_eight_endpoints():
    ddbc = create_ddb_client()
    db_response = ddbc.scan(
        TableName="LoopbackResponses",
    )

    print(db_response)

    assert db_response["Count"] == 8

    response_mnos = set()
    response_codes = set()
    for item in db_response["Items"]:
        response_mnos.add(item["Name"]["S"])
        response_codes.add(item["ResponseCode"]["N"])
    expected_mnos = {
        "ee-az1",
        "ee-az2",
        "o2-az1",
        "o2-az2",
        "vodafone-az1",
        "vodafone-az2",
        "three-az1",
        "three-az2",
    }
    assert response_mnos == expected_mnos
    assert len(response_codes) == 1
    assert response_codes.pop() == "200"


def test_set_loopback_response_codes():
    ddbc = create_ddb_client()

    test_cbc = "ee-az2"
    test_code = 500
    ip = config["cbcs"][test_cbc]

    try:
        _set_response_codes(ddbc, test_cbc, test_code)

        db_response = ddbc.scan(
            TableName="LoopbackResponses",
            KeyConditionExpression="IpAddress = :IpAddress",
            ExpressionAttributeValues={
                ":IpAddress": {"S": ip},
            },
        )

        assert db_response["Count"] == 1
        assert db_response["Items"][0]["ResponseCode"]["N"] == test_code

    finally:
        _set_response_codes(ddbc, test_cbc, 200)


def _set_response_codes(ddbc, az_name=None, response_code=200):
    if ddbc is None:
        print("Please provide a dynamoDB client")

    if isinstance(az_name, str) and az_name.lower() != "all":
        ips = [config["cbcs"][az_name]]
    else:
        ips = config["cbcs"].values()

    for ip in ips:
        ddbc.update_item(
            TableName="LoopbackResponses",
            Key={
                "IpAddress": {"S": ip},
            },
            UpdateExpression="SET ResponseCode = :code",
            ExpressionAttributeValues={
                ":code": {"N": str(response_code)},
            },
        )


# @recordtime
# @pytest.mark.xdist_group(name="cbc-integration")
# def test_broadcast_with_new_content(driver, api_client):
#     broadcast_id = str(uuid.uuid4())

#     try:
#         start = int(time.time())
#         broadcast_alert(driver, broadcast_id)

#         alerturl = driver.current_url.split("services/")[1]
#         service_id = alerturl.split("/current-alerts/")[0]
#         broadcast_message_id = alerturl.split("/current-alerts/")[1]

#         time.sleep(10)
#         end = int(time.time())
#         url = f"/service/{service_id}/broadcast-message/{broadcast_message_id}/provider-messages"
#         response = api_client.get(url=url)
#         assert response is not None

#         messages = response["messages"]
#         assert messages is not None
#         assert len(messages) == 4

#         ddbc = create_ddb_client()
#         db_response = ddbc.scan(
#             TableName="LoopbackRequests",
#             FilterExpression="#timestamp BETWEEN :start_time AND :end_time",
#             ExpressionAttributeNames={"#timestamp": "Timestamp"},
#             ExpressionAttributeValues={
#                 ":start_time": {"N": str(start)},
#                 ":end_time": {"N": str(end)},
#             },
#         )

#         assert db_response["Count"] == 4

#         response_items = db_response["Items"]

#         response_mnos = set()
#         for item in response_items:
#             response_mnos.add(item["MnoName"]["S"])
#         expected_mnos = {"ee-az1", "o2-az1", "vodafone-az1", "three-az1"}
#         assert response_mnos == expected_mnos

#     finally:
#         cancel_alert(driver, broadcast_id)


# @recordtime
# @pytest.mark.xdist_group(name="cbc-integration")
# def test_broadcast_with_new_content_with_site_a_failure(driver):
#     broadcast_id = str(uuid.uuid4())
#     test_mno = "o2"

#     try:
#         start = int(time.time())
#         broadcast_alert(driver, broadcast_id)

#         print("set loopback resposne to 500 for one mno")

#         ddbc = create_ddb_client()

#         print("create broadcast and check for responses")

#     finally:
#         cancel_alert(driver, broadcast_id)
#         print("restore responses to 200s")


# @recordtime
# @pytest.mark.xdist_group(name="cbc-integration")
# def test_broadcast_with_new_content_with_primary_lambda_failure(driver):
#     pass


# @recordtime
# @pytest.mark.xdist_group(name="cbc-integration")
# def test_broadcast_with_new_content_with_primary_lambda_and_site_a_failure(driver):
#     pass
