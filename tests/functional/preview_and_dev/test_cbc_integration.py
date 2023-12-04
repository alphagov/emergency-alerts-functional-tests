import time
import uuid

import boto3
import pytest

from config import config
from tests.pages.rollups import broadcast_alert, cancel_alert
from tests.test_utils import recordtime


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


# @recordtime
# @pytest.mark.xdist_group(name="cbc-integration")
# def test_get_loopback_request_with_bad_id_returns_no_items():
#     ddbc = create_ddb_client()
#     response = ddbc.query(
#         TableName="LoopbackRequests",
#         KeyConditionExpression="RequestId = :RequestId",
#         ExpressionAttributeValues={
#             ":RequestId": {"S": "1234"},
#         },
#     )

#     assert len(response["Items"]) == 0


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
# def test_get_loopback_responses_returns_codes_for_eight_endpoints():
#     ddbc = create_ddb_client()
#     db_response = ddbc.scan(
#         TableName="LoopbackResponses",
#     )

#     print(db_response)

#     assert db_response["Count"] == 8

#     response_mnos = set()
#     response_codes = set()
#     for item in db_response["Items"]:
#         response_mnos.add(item["Name"]["S"])
#         response_codes.add(item["ResponseCode"]["N"])
#     expected_mnos = {
#         "ee-az1",
#         "ee-az2",
#         "o2-az1",
#         "o2-az2",
#         "vodafone-az1",
#         "vodafone-az2",
#         "three-az1",
#         "three-az2",
#     }
#     assert response_mnos == expected_mnos
#     assert len(response_codes) == 1
#     assert response_codes.pop() == "200"


# @recordtime
# @pytest.mark.xdist_group(name="cbc-integration")
# def test_set_loopback_response_codes():
#     test_cbc = "ee-az1"
#     test_code = "500"
#     test_ip = config["cbcs"][test_cbc]

#     try:
#         ddbc = create_ddb_client()
#         _set_response_codes(ddbc, test_cbc, test_code)

#         db_response = ddbc.query(
#             TableName="LoopbackResponses",
#             KeyConditionExpression="IpAddress = :IpAddress",
#             ExpressionAttributeValues={
#                 ":IpAddress": {"S": test_ip},
#             },
#         )

#         assert db_response["Count"] == 1
#         assert db_response["Items"][0]["ResponseCode"]["N"] == test_code

#     finally:
#         _set_response_codes(ddbc, test_cbc, "200")


@recordtime
@pytest.mark.xdist_group(name="cbc-integration")
def test_broadcast_with_az1_failure_tries_az2(driver, api_client):
    broadcast_id = str(uuid.uuid4())

    primary_cbc = "o2-az1"
    secondary_cbc = "o2-az2"
    failure_code = "500"
    success_code = "200"

    try:
        ddbc = create_ddb_client()
        _set_response_codes(ddbc, primary_cbc, failure_code)

        broadcast_alert(driver, broadcast_id)
        # alerturl = driver.current_url.split("services/")[1]
        # service_id = alerturl.split("/current-alerts/")[0]
        # broadcast_message_id = alerturl.split("/current-alerts/")[1]
        (service_id, broadcast_message_id) = _get_service_and_broadcast_ids(
            driver.current_url
        )
        time.sleep(10)

        # db_response = ddbc.query(
        #     TableName="LoopbackResponses",
        #     KeyConditionExpression="IpAddress = :IpAddress",
        #     ExpressionAttributeValues={
        #         ":IpAddress": {"S": config["cbcs"][primary_cbc]},
        #     },
        # )
        # assert db_response["Count"] == 1
        # assert db_response["Items"][0]["ResponseCode"]["N"] == failure_code

        # db_response = ddbc.query(
        #     TableName="LoopbackResponses",
        #     KeyConditionExpression="IpAddress = :IpAddress",
        #     ExpressionAttributeValues={
        #         ":IpAddress": {"S": config["cbcs"][secondary_cbc]},
        #     },
        # )
        # assert db_response["Count"] == 1
        # assert db_response["Items"][0]["ResponseCode"]["N"] == success_code

        url = f"/service/{service_id}/broadcast-message/{broadcast_message_id}/provider-messages"
        response = api_client.get(url=url)
        assert response is not None

        provider_messages = response["messages"]
        assert provider_messages is not None
        assert len(provider_messages) == 4

        o2_request_id = _retrieve_item_for_key_value(
            provider_messages, "provider", "o2", "id"
        )

        db_response = ddbc.query(
            TableName="LoopbackRequests",
            KeyConditionExpression="RequestId = :RequestId",
            ExpressionAttributeValues={":RequestId": {"S": o2_request_id}},
        )

        print(provider_messages)
        print(db_response)

        responses = db_response["Items"]

        o2_az1_response_code = _retrieve_item_for_key_value(
            responses, "MnoName", primary_cbc, "ResponseCode"
        )
        assert o2_az1_response_code == failure_code

        o2_az2_response_code = _retrieve_item_for_key_value(
            responses, "MnoName", secondary_cbc, "ResponseCode"
        )
        assert o2_az2_response_code == success_code

        assert db_response is None

    finally:
        _set_response_codes(ddbc, primary_cbc, success_code)
        cancel_alert(driver, broadcast_id)


# @recordtime
# @pytest.mark.xdist_group(name="cbc-integration")
# def test_broadcast_with_both_azs_failing_gets_failure_response_from_both(driver):
#     broadcast_id = str(uuid.uuid4())

#     primary_cbc = "vodafone-az1"
#     secondary_cbc = "vodafone-az2"
#     failure_code = "500"
#     success_code = "200"

#     try:
#         ddbc = create_ddb_client()
#         _set_response_codes(ddbc, [primary_cbc, secondary_cbc], failure_code)

#         broadcast_alert(driver, broadcast_id)
#         time.sleep(120)

#         db_response = ddbc.query(
#             TableName="LoopbackResponses",
#             KeyConditionExpression="IpAddress = :IpAddress",
#             ExpressionAttributeValues={
#                 ":IpAddress": {"S": config["cbcs"][primary_cbc]},
#             },
#         )
#         assert db_response["Count"] == 1
#         assert db_response["Items"][0]["ResponseCode"]["N"] == failure_code

#         db_response = ddbc.query(
#             TableName="LoopbackResponses",
#             KeyConditionExpression="IpAddress = :IpAddress",
#             ExpressionAttributeValues={
#                 ":IpAddress": {"S": config["cbcs"][secondary_cbc]},
#             },
#         )
#         assert db_response["Count"] == 1
#         assert db_response["Items"][0]["ResponseCode"]["N"] == failure_code

#     finally:
#         _set_response_codes(ddbc, [primary_cbc, secondary_cbc], success_code)
#         cancel_alert(driver, broadcast_id)


def _get_service_and_broadcast_ids(url):
    alerturl = url.split("services/")[1]
    service_id = alerturl.split("/current-alerts/")[0]
    broadcast_message_id = alerturl.split("/current-alerts/")[1]
    return (service_id, broadcast_message_id)


def _set_response_codes(ddbc, az_name="all", response_code="200"):
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
                ":code": {"N": response_code},
            },
        )


# def _find_id_by_provider(data, provider):
#     for item in data:
#         if item["provider"] == provider:
#             return item["id"]
#     return None


def _retrieve_item_for_key_value(data, key, value, item):
    for d in data:
        if d[key] == value:
            return d[item]
    return None
