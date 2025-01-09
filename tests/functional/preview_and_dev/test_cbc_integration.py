import time
import uuid
from random import choice

import pytest
from retry import retry

from config import config
from tests.pages import RetryException
from tests.pages.rollups import broadcast_alert, cancel_alert
from tests.test_utils import PROVIDERS, create_ddb_client, set_response_codes

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
    responses = get_loopback_request_items(ddbc=ddbc, request_id="1234")
    assert len(responses) == 0


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

    provider_messages = response["messages"]
    assert provider_messages is not None
    assert len(provider_messages) == 4

    distinct_request_ids = 0

    for provider_id in PROVIDERS:
        request_id = dict_item_for_key_value(
            provider_messages, "provider", provider_id, "id"
        )
        responses = get_loopback_request_items(ddbc=ddbc, request_id=request_id)
        if len(responses):
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
def test_set_loopback_response_codes(cbc_blackout):
    ddbc = create_ddb_client()

    test_code = 403
    set_loopback_response_codes(ddbc, response_code=test_code)
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

    set_loopback_response_codes(ddbc=ddbc, response_code=200)
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
def test_broadcast_with_az1_failure_tries_az2(driver, api_client, cbc_blackout):
    broadcast_id = str(uuid.uuid4())

    mno = choice(PROVIDERS)
    primary_cbc = f"{mno}-az1"
    secondary_cbc = f"{mno}-az2"
    failure_code = 500

    ddbc = create_ddb_client()
    set_loopback_response_codes(
        ddbc, response_code=failure_code, cbc_list=[primary_cbc]
    )

    broadcast_alert(driver, broadcast_id)
    (service_id, broadcast_message_id) = get_service_and_broadcast_id(
        driver.current_url
    )
    time.sleep(60)

    url = f"/service/{service_id}/broadcast-message/{broadcast_message_id}/provider-messages"
    response = api_client.get(url=url)
    assert response is not None

    provider_messages = response["messages"]
    assert provider_messages is not None
    assert len(provider_messages) == 4

    request_id = dict_item_for_key_value(provider_messages, "provider", mno, "id")
    responses = get_loopback_request_items(
        ddbc=ddbc, request_id=request_id, retry_if=lambda resp: len(resp["Items"]) < 5
    )

    set_loopback_response_codes(ddbc=ddbc, response_code=200)

    az1_response_code = dynamo_item_for_key_value(
        responses, "MnoName", primary_cbc, "ResponseCode"
    )
    assert az1_response_code == str(failure_code)

    az2_response_code = dynamo_item_for_key_value(
        responses, "MnoName", secondary_cbc, "ResponseCode"
    )
    assert az2_response_code == "200"

    cancel_alert(driver, broadcast_id)


@pytest.mark.xdist_group(name=test_group_name)
def test_broadcast_with_both_azs_failing_retries_requests(
    driver, api_client, cbc_blackout
):
    broadcast_id = str(uuid.uuid4())

    mno = choice(PROVIDERS)
    primary_cbc = f"{mno}-az1"
    secondary_cbc = f"{mno}-az2"
    failure_code = 500

    ddbc = create_ddb_client()
    set_loopback_response_codes(
        ddbc, response_code=failure_code, cbc_list=[primary_cbc, secondary_cbc]
    )

    broadcast_alert(driver, broadcast_id)
    time.sleep(10)  # wait for send_broadcast_message to be invoked

    (service_id, broadcast_message_id) = get_service_and_broadcast_id(
        driver.current_url
    )

    url = f"/service/{service_id}/broadcast-message/{broadcast_message_id}/provider-messages"
    response = api_client.get(url=url)
    assert response is not None

    provider_messages = response["messages"]
    assert provider_messages is not None
    assert len(provider_messages) == 4

    request_id = dict_item_for_key_value(provider_messages, "provider", mno, "id")
    responses = get_loopback_request_items(
        ddbc=ddbc,
        request_id=request_id,
        retry_if=lambda resp: len(resp["Items"]) < 4,
    )

    set_loopback_response_codes(ddbc=ddbc, response_code=200)

    az1_response_codes = dynamo_items_for_key_value(
        responses, "MnoName", primary_cbc, "ResponseCode"
    )
    az1_codes_set = set(az1_response_codes)
    assert len(az1_codes_set) == 1  # assert that all codes are the same
    assert az1_codes_set.pop() == str(failure_code)

    az2_response_codes = dynamo_items_for_key_value(
        responses, "MnoName", secondary_cbc, "ResponseCode"
    )
    az2_codes_set = set(az2_response_codes)
    assert len(az2_codes_set) == 1  # assert that all codes are the same
    assert az2_codes_set.pop() == str(failure_code)

    cancel_alert(driver, broadcast_id)


@pytest.mark.xdist_group(name=test_group_name)
def test_broadcast_with_both_azs_failing_eventually_succeeds_if_azs_are_restored(
    driver, api_client, cbc_blackout
):
    broadcast_id = str(uuid.uuid4())

    mno = choice(PROVIDERS)
    primary_cbc = f"{mno}-az1"
    secondary_cbc = f"{mno}-az2"
    failure_code = 500

    ddbc = create_ddb_client()
    set_loopback_response_codes(
        ddbc, response_code=failure_code, cbc_list=[primary_cbc, secondary_cbc]
    )

    broadcast_alert(driver, broadcast_id)
    time.sleep(10)  # wait for send_broadcast_message to be invoked

    (service_id, broadcast_message_id) = get_service_and_broadcast_id(
        driver.current_url
    )

    url = f"/service/{service_id}/broadcast-message/{broadcast_message_id}/provider-messages"
    response = api_client.get(url=url)
    assert response is not None

    provider_messages = response["messages"]
    assert provider_messages is not None
    assert len(provider_messages) == 4

    request_id = dict_item_for_key_value(provider_messages, "provider", mno, "id")

    # wait for at least one response (which should be a '500' at this stage)
    _ = get_loopback_request_items(
        ddbc=ddbc, request_id=request_id, retry_if=lambda resp: len(resp["Items"]) < 1
    )

    set_loopback_response_codes(ddbc=ddbc, response_code=200)
    time.sleep(120)

    responses = get_loopback_request_items(
        ddbc=ddbc,
        request_id=request_id,
    )

    az1_response_codes = dynamo_items_for_key_value(
        responses, "MnoName", primary_cbc, "ResponseCode"
    )

    az2_response_codes = dynamo_items_for_key_value(
        responses, "MnoName", secondary_cbc, "ResponseCode"
    )

    response_codes = set(az1_response_codes + az2_response_codes)
    assert len(response_codes) == 2  # we should have a 200 along with the 500s
    assert str(failure_code) in response_codes
    assert "200" in response_codes

    cancel_alert(driver, broadcast_id)


@retry(
    RetryException,
    tries=config["dynamo_query_retry_times"],
    delay=config["dynamo_query_retry_interval"],
)
def get_loopback_request_items(ddbc, request_id, retry_if=None):
    db_response = ddbc.query(
        TableName="LoopbackRequests",
        KeyConditionExpression="RequestId = :RequestId",
        ExpressionAttributeValues={":RequestId": {"S": request_id}},
    )
    if retry_if is not None and retry_if(db_response):
        raise RetryException(
            f'Found {len(db_response["Items"])} requests for RequestId:{request_id}. Retrying...)'
        )

    return db_response["Items"]


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


def set_loopback_response_codes(ddbc, response_code=200, cbc_list=None):
    set_response_codes(ddbc=ddbc, response_code=response_code, cbc_list=cbc_list)
    time.sleep(10)
