import time
import uuid

import boto3
import pytest

from config import config
from tests.pages.rollups import broadcast_alert, cancel_alert
from tests.test_utils import PROVIDERS

test_group_name = "cbc-integration"


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


@pytest.mark.xdist_group(name=test_group_name)
def test_cbc_config():
    assert "ee-az1" in config["cbcs"]
    assert "ee-az2" in config["cbcs"]
    assert "vodafone-az1" in config["cbcs"]
    assert "vodafone-az2" in config["cbcs"]
    assert "o2-az1" in config["cbcs"]
    assert "o2-az2" in config["cbcs"]
    assert "three-az1" in config["cbcs"]
    assert "three-az2" in config["cbcs"]


@pytest.mark.xdist_group(name=test_group_name)
def test_get_loopback_request_with_bad_id_returns_no_items():
    ddbc = create_ddb_client()
    response = ddbc.query(
        TableName="LoopbackRequests",
        KeyConditionExpression="RequestId = :RequestId",
        ExpressionAttributeValues={
            ":RequestId": {"S": "1234"},
        },
        ConsistentRead=True,
    )

    assert len(response["Items"]) == 0


# @pytest.mark.skip("Skip while vodafone loopback architecture issue is investigated")
@pytest.mark.xdist_group(name=test_group_name)
def test_broadcast_generates_four_provider_messages(driver, api_client):
    ddbc = create_ddb_client()
    _set_response_codes(ddbc, "all", "200")

    broadcast_id = str(uuid.uuid4())
    broadcast_alert(driver, broadcast_id)

    alerturl = driver.current_url.split("services/")[1]
    service_id = alerturl.split("/current-alerts/")[0]
    broadcast_message_id = alerturl.split("/current-alerts/")[1]

    time.sleep(60)
    url = f"/service/{service_id}/broadcast-message/{broadcast_message_id}/provider-messages"
    response = api_client.get(url=url)
    assert response is not None

    provider_messages = response["messages"]
    assert provider_messages is not None
    assert len(provider_messages) == 4

    distinct_request_ids = 0

    for provider_id in PROVIDERS:
        request_id = _dict_item_for_key_value(
            provider_messages, "provider", provider_id, "id"
        )
        db_response = ddbc.query(
            TableName="LoopbackRequests",
            KeyConditionExpression="RequestId = :RequestId",
            ExpressionAttributeValues={":RequestId": {"S": request_id}},
            ConsistentRead=True,
        )
        print(db_response)
        if len(db_response["Items"]):
            distinct_request_ids += 1

    assert distinct_request_ids == 4

    cancel_alert(driver, broadcast_id)


@pytest.mark.xdist_group(name=test_group_name)
def test_get_loopback_responses_returns_codes_for_eight_endpoints():
    ddbc = create_ddb_client()
    _set_response_codes(ddbc, "all", "200")
    db_response = ddbc.scan(
        TableName="LoopbackResponses",
    )

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


@pytest.mark.xdist_group(name=test_group_name)
def test_set_loopback_response_codes():
    test_cbc = "ee-az1"
    test_code = "500"
    test_ip = config["cbcs"][test_cbc]

    ddbc = create_ddb_client()
    _set_response_codes(ddbc, "all", "200")
    _set_response_codes(ddbc, test_cbc, test_code)

    db_response = ddbc.query(
        TableName="LoopbackResponses",
        KeyConditionExpression="IpAddress = :IpAddress",
        ExpressionAttributeValues={
            ":IpAddress": {"S": test_ip},
        },
        ConsistentRead=True,
    )

    assert db_response["Count"] == 1
    assert db_response["Items"][0]["ResponseCode"]["N"] == test_code


@pytest.mark.xdist_group(name=test_group_name)
def test_broadcast_with_az1_failure_tries_az2(driver, api_client):
    broadcast_id = str(uuid.uuid4())

    mno = "ee"
    primary_cbc = f"{mno}-az1"
    secondary_cbc = f"{mno}-az2"
    failure_code = "500"
    success_code = "200"

    ddbc = create_ddb_client()
    _set_response_codes(ddbc, "all", "200")
    _set_response_codes(ddbc, primary_cbc, failure_code)

    broadcast_alert(driver, broadcast_id)
    (service_id, broadcast_message_id) = _get_service_and_broadcast_id(
        driver.current_url
    )
    time.sleep(60)

    url = f"/service/{service_id}/broadcast-message/{broadcast_message_id}/provider-messages"
    response = api_client.get(url=url)
    assert response is not None

    provider_messages = response["messages"]
    assert provider_messages is not None
    assert len(provider_messages) == 4

    request_id = _dict_item_for_key_value(provider_messages, "provider", mno, "id")

    db_response = ddbc.query(
        TableName="LoopbackRequests",
        KeyConditionExpression="RequestId = :RequestId",
        ExpressionAttributeValues={":RequestId": {"S": request_id}},
        ConsistentRead=True,
    )
    print(db_response)
    responses = db_response["Items"]

    az1_response_code = _dynamo_item_for_key_value(
        responses, "MnoName", primary_cbc, "ResponseCode"
    )
    assert az1_response_code == failure_code

    az2_response_code = _dynamo_item_for_key_value(
        responses, "MnoName", secondary_cbc, "ResponseCode"
    )
    assert az2_response_code == success_code

    cancel_alert(driver, broadcast_id)


# @pytest.mark.skip("Skip while vodafone loopback architecture issue is investigated")
@pytest.mark.xdist_group(name=test_group_name)
def test_broadcast_with_both_azs_failing_retries_requests(driver, api_client):
    broadcast_id = str(uuid.uuid4())

    mno = "vodafone"
    primary_cbc = f"{mno}-az1"
    secondary_cbc = f"{mno}-az2"
    failure_code = "500"

    ddbc = create_ddb_client()
    _set_response_codes(ddbc, "all", "200")
    _set_response_codes(ddbc, [primary_cbc, secondary_cbc], failure_code)

    broadcast_alert(driver, broadcast_id)
    time.sleep(300)  # wait for exponential backoff of retries

    (service_id, broadcast_message_id) = _get_service_and_broadcast_id(
        driver.current_url
    )

    url = f"/service/{service_id}/broadcast-message/{broadcast_message_id}/provider-messages"
    response = api_client.get(url=url)
    assert response is not None

    provider_messages = response["messages"]
    assert provider_messages is not None
    assert len(provider_messages) == 4

    request_id = _dict_item_for_key_value(provider_messages, "provider", mno, "id")

    db_response = ddbc.query(
        TableName="LoopbackRequests",
        KeyConditionExpression="RequestId = :RequestId",
        ExpressionAttributeValues={":RequestId": {"S": request_id}},
        ConsistentRead=True,
    )
    print(db_response)
    responses = db_response["Items"]

    az1_response_codes = _dynamo_items_for_key_value(
        responses, "MnoName", primary_cbc, "ResponseCode"
    )

    az1_codes_set = set(az1_response_codes)
    assert len(az1_codes_set) == 1  # assert that all codes are the same
    assert az1_codes_set.pop() == failure_code

    az2_response_codes = _dynamo_items_for_key_value(
        responses, "MnoName", secondary_cbc, "ResponseCode"
    )

    az2_codes_set = set(az2_response_codes)
    assert len(az2_codes_set) == 1  # assert that all codes are the same
    assert az2_codes_set.pop() == failure_code

    # Assert that the AZs have the retry count we expect:
    # i.e. (initial invocation + 5 retries) * (primary + secondary attempt) = 12
    assert len(az1_response_codes) == 12 or len(az2_response_codes) == 12

    cancel_alert(driver, broadcast_id)


@pytest.mark.xdist_group(name=test_group_name)
def test_broadcast_with_both_azs_failing_eventually_succeeds_if_azs_are_restored(
    driver, api_client
):
    broadcast_id = str(uuid.uuid4())

    mno = "three"
    primary_cbc = f"{mno}-az1"
    secondary_cbc = f"{mno}-az2"
    failure_code = "500"
    success_code = "200"

    ddbc = create_ddb_client()
    _set_response_codes(ddbc, "all", "200")
    _set_response_codes(ddbc, [primary_cbc, secondary_cbc], failure_code)

    broadcast_alert(driver, broadcast_id)
    (service_id, broadcast_message_id) = _get_service_and_broadcast_id(
        driver.current_url
    )
    time.sleep(10)  # wait for some retries
    _set_response_codes(ddbc, [primary_cbc, secondary_cbc], success_code)
    time.sleep(60)  # wait for more retries

    url = f"/service/{service_id}/broadcast-message/{broadcast_message_id}/provider-messages"
    response = api_client.get(url=url)
    assert response is not None

    provider_messages = response["messages"]
    assert provider_messages is not None
    assert len(provider_messages) == 4

    request_id = _dict_item_for_key_value(provider_messages, "provider", mno, "id")

    db_response = ddbc.query(
        TableName="LoopbackRequests",
        KeyConditionExpression="RequestId = :RequestId",
        ExpressionAttributeValues={":RequestId": {"S": request_id}},
        ConsistentRead=True,
    )
    print(db_response)
    responses = db_response["Items"]

    az1_response_codes = _dynamo_items_for_key_value(
        responses, "MnoName", primary_cbc, "ResponseCode"
    )

    az2_response_codes = _dynamo_items_for_key_value(
        responses, "MnoName", secondary_cbc, "ResponseCode"
    )

    response_codes = set(az1_response_codes + az2_response_codes)
    assert len(response_codes) == 2  # we should have a 200 along with the 500s
    assert failure_code in response_codes
    assert success_code in response_codes

    cancel_alert(driver, broadcast_id)


def _get_service_and_broadcast_id(url):
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


def _dict_item_for_key_value(data, key, value, item):
    for d in data:
        if d[key] == value:
            return d[item]
    return None


def _dynamo_item_for_key_value(data, key, value, item):
    for d in data:
        if list(d[key].values())[0] == value:
            return list(d[item].values())[0]
    return None


def _dynamo_items_for_key_value(data, key, value, item):
    items = list()
    for d in data:
        if list(d[key].values())[0] == value:
            items.append(list(d[item].values())[0])
    return items
