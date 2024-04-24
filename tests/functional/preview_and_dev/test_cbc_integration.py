import time
import uuid

import pytest

from config import config
from tests.pages.rollups import broadcast_alert, cancel_alert
from tests.test_utils import (
    PROVIDERS,
    create_ddb_client,
    put_functional_test_blackout_metric,
    set_response_codes,
)

test_group_name = "cbc-integration"


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

    broadcast_id = str(uuid.uuid4())
    broadcast_alert(driver, broadcast_id)

    alerturl = driver.current_url.split("services/")[1]
    service_id = alerturl.split("/current-alerts/")[0]
    broadcast_message_id = alerturl.split("/current-alerts/")[1]

    time.sleep(60)
    url = f"/service/{service_id}/broadcast-message/{broadcast_message_id}/provider-messages"
    response = api_client.get(url=url)
    assert response is not None

    print(f">>> provider messages for broadcast message ID {broadcast_message_id}")
    print(response)

    provider_messages = response["messages"]
    assert provider_messages is not None
    assert len(provider_messages) == 4

    distinct_request_ids = 0

    for provider_id in PROVIDERS:
        request_id = dict_item_for_key_value(
            provider_messages, "provider", provider_id, "id"
        )
        db_response = ddbc.query(
            TableName="LoopbackRequests",
            KeyConditionExpression="RequestId = :RequestId",
            ExpressionAttributeValues={":RequestId": {"S": request_id}},
            ConsistentRead=True,
        )
        print(f">>> loopback requests for request ID {request_id}")
        print(db_response)
        if len(db_response["Items"]):
            distinct_request_ids += 1

    assert distinct_request_ids == 4

    cancel_alert(driver, broadcast_id)


@pytest.mark.xdist_group(name=test_group_name)
def test_get_loopback_responses_returns_codes_for_eight_endpoints():
    ddbc = create_ddb_client()
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
    ddbc = create_ddb_client()

    test_code = 403
    set_error_response_codes(ddbc, response_code=test_code)
    for mno in PROVIDERS:
        for az in ["az1", "az2"]:
            test_cbc = f"{mno}-{az}"
            test_ip = config["cbcs"][test_cbc]
            db_response = ddbc.query(
                TableName="LoopbackResponses",
                KeyConditionExpression="IpAddress = :IpAddress",
                ExpressionAttributeValues={
                    ":IpAddress": {"S": test_ip},
                },
                ConsistentRead=True,
            )
            assert db_response["Count"] == 1
            assert db_response["Items"][0]["ResponseCode"]["N"] == str(test_code)

    reset_response_codes(ddbc)
    for mno in PROVIDERS:
        for az in ["az1", "az2"]:
            test_cbc = f"{mno}-{az}"
            test_ip = config["cbcs"][test_cbc]
            db_response = ddbc.query(
                TableName="LoopbackResponses",
                KeyConditionExpression="IpAddress = :IpAddress",
                ExpressionAttributeValues={
                    ":IpAddress": {"S": test_ip},
                },
                ConsistentRead=True,
            )
            assert db_response["Count"] == 1
            assert db_response["Items"][0]["ResponseCode"]["N"] == "200"


@pytest.mark.xdist_group(name=test_group_name)
def test_broadcast_with_az1_failure_tries_az2(driver, api_client):
    broadcast_id = str(uuid.uuid4())

    mno = "ee"
    primary_cbc = f"{mno}-az1"
    secondary_cbc = f"{mno}-az2"
    failure_code = 500

    ddbc = create_ddb_client()
    set_error_response_codes(ddbc, response_code=failure_code, cbc_list=[primary_cbc])

    broadcast_alert(driver, broadcast_id)
    (service_id, broadcast_message_id) = get_service_and_broadcast_id(
        driver.current_url
    )
    time.sleep(60)

    url = f"/service/{service_id}/broadcast-message/{broadcast_message_id}/provider-messages"
    response = api_client.get(url=url)
    assert response is not None

    print(f">>> provider messages for broadcast message ID {broadcast_message_id}")
    print(response)

    provider_messages = response["messages"]
    assert provider_messages is not None
    assert len(provider_messages) == 4

    request_id = dict_item_for_key_value(provider_messages, "provider", mno, "id")

    db_response = ddbc.query(
        TableName="LoopbackRequests",
        KeyConditionExpression="RequestId = :RequestId",
        ExpressionAttributeValues={":RequestId": {"S": request_id}},
        ConsistentRead=True,
    )

    reset_response_codes(ddbc)

    print(f">>> loopback requests for request ID {request_id}")
    print(db_response)

    responses = db_response["Items"]

    az1_response_code = dynamo_item_for_key_value(
        responses, "MnoName", primary_cbc, "ResponseCode"
    )
    assert az1_response_code == failure_code

    az2_response_code = dynamo_item_for_key_value(
        responses, "MnoName", secondary_cbc, "ResponseCode"
    )
    assert az2_response_code == "200"

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
    set_response_codes(
        ddbc, response_code=failure_code, cbc_list=[primary_cbc, secondary_cbc]
    )

    broadcast_alert(driver, broadcast_id)
    time.sleep(300)  # wait for exponential backoff of retries

    (service_id, broadcast_message_id) = get_service_and_broadcast_id(
        driver.current_url
    )

    url = f"/service/{service_id}/broadcast-message/{broadcast_message_id}/provider-messages"
    response = api_client.get(url=url)
    assert response is not None

    print(f">>> provider messages for broadcast message ID {broadcast_message_id}")
    print(response)

    provider_messages = response["messages"]
    assert provider_messages is not None
    assert len(provider_messages) == 4

    request_id = dict_item_for_key_value(provider_messages, "provider", mno, "id")

    db_response = ddbc.query(
        TableName="LoopbackRequests",
        KeyConditionExpression="RequestId = :RequestId",
        ExpressionAttributeValues={":RequestId": {"S": request_id}},
        ConsistentRead=True,
    )

    reset_response_codes(ddbc)

    print(f">>> loopback requests for request ID {request_id}")
    print(db_response)

    responses = db_response["Items"]

    az1_response_codes = dynamo_items_for_key_value(
        responses, "MnoName", primary_cbc, "ResponseCode"
    )

    az1_codes_set = set(az1_response_codes)
    assert len(az1_codes_set) == 1  # assert that all codes are the same
    assert az1_codes_set.pop() == failure_code

    az2_response_codes = dynamo_items_for_key_value(
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

    ddbc = create_ddb_client()
    set_response_codes(
        ddbc, response_code=failure_code, cbc_list=[primary_cbc, secondary_cbc]
    )

    broadcast_alert(driver, broadcast_id)
    (service_id, broadcast_message_id) = get_service_and_broadcast_id(
        driver.current_url
    )
    time.sleep(10)  # wait for some retries
    reset_response_codes(ddbc)
    time.sleep(60)  # wait for more retries

    url = f"/service/{service_id}/broadcast-message/{broadcast_message_id}/provider-messages"
    response = api_client.get(url=url)
    assert response is not None

    print(f">>> provider messages for broadcast message ID {broadcast_message_id}")
    print(response)

    provider_messages = response["messages"]
    assert provider_messages is not None
    assert len(provider_messages) == 4

    request_id = dict_item_for_key_value(provider_messages, "provider", mno, "id")

    db_response = ddbc.query(
        TableName="LoopbackRequests",
        KeyConditionExpression="RequestId = :RequestId",
        ExpressionAttributeValues={":RequestId": {"S": request_id}},
        ConsistentRead=True,
    )

    print(f">>> loopback requests for request ID {request_id}")
    print(db_response)

    responses = db_response["Items"]

    az1_response_codes = dynamo_items_for_key_value(
        responses, "MnoName", primary_cbc, "ResponseCode"
    )

    az2_response_codes = dynamo_items_for_key_value(
        responses, "MnoName", secondary_cbc, "ResponseCode"
    )

    response_codes = set(az1_response_codes + az2_response_codes)
    assert len(response_codes) == 2  # we should have a 200 along with the 500s
    assert failure_code in response_codes
    assert "200" in response_codes

    cancel_alert(driver, broadcast_id)


def get_service_and_broadcast_id(url):
    alerturl = url.split("services/")[1]
    service_id = alerturl.split("/current-alerts/")[0]
    broadcast_message_id = alerturl.split("/current-alerts/")[1]
    return (service_id, broadcast_message_id)


def dict_item_for_key_value(data, key, value, item):
    for d in data:
        if d[key] == value:
            return d[item]
    return None


def dynamo_item_for_key_value(data, key, value, item):
    for d in data:
        if list(d[key].values())[0] == value:
            return list(d[item].values())[0]
    return None


def dynamo_items_for_key_value(data, key, value, item):
    items = list()
    for d in data:
        if list(d[key].values())[0] == value:
            items.append(list(d[item].values())[0])
    return items


def set_error_response_codes(ddbc, response_code=200, cbc_list=None):
    put_functional_test_blackout_metric(status=response_code)
    set_response_codes(ddbc=ddbc, response_code=response_code, cbc_list=cbc_list)


def reset_response_codes(ddbc):
    set_response_codes(ddbc=ddbc)
    put_functional_test_blackout_metric(status=200)
