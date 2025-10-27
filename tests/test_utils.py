import functools
import json
import logging
import re
from datetime import datetime, timezone
from urllib.parse import urlencode

import boto3
import requests
from itsdangerous import URLSafeTimedSerializer
from notifications_python_client.notifications import NotificationsAPIClient
from retry import retry

from config import config
from tests.pages import (
    CurrentAlertsPage,
    EditBroadcastTemplatePage,
    GovUkAlertsPage,
    RetryException,
    ShowTemplatesPage,
    VerifyPage,
    wait_for_page_load_completion,
)
from tests.pages.pages import ChooseTemplateFieldsPage
from tests.playwright_adapter import (
    By,
    NoSuchElementException,
    PlaywrightDriver,
    TimeoutException,
)

logging.basicConfig(
    filename="./logs/test_run_{}.log".format(datetime.now(timezone.utc)),
    level=logging.INFO,
)

ACCOUNTS_REQUIRING_SMS_2FA = [
    "broadcast_create_user",
    "broadcast_approve_user",
    "platform_admin",
    "platform_admin_2",
    "broadcast_auth_test_user",
]

PROVIDERS = ["ee", "o2", "three", "vodafone"]


def convert_naive_utc_datetime_to_cap_standard_string(dt):
    """
    As defined in section 3.3.2 of
    http://docs.oasis-open.org/emergency/cap/v1.2/CAP-v1.2-os.html
    They define the standard "YYYY-MM-DDThh:mm:ssXzh:zm", where X is
    `+` if the timezone is > UTC, otherwise `-`
    """
    return f"{dt.strftime('%Y-%m-%dT%H:%M:%S')}-00:00"


def get_link(template_id, email):
    email_body = get_notification_by_to_field(
        template_id, config["notify_service_api_key"], email
    )
    m = re.search(r"http[s]?://\S+", email_body, re.MULTILINE)
    if not m:
        raise RetryException(
            "Could not find a verify email code for template {} sent to {}".format(
                template_id, email
            )
        )
    return m.group(0)


@retry(
    RetryException,
    tries=config["verify_code_retry_times"],
    delay=config["verify_code_retry_interval"],
)
def do_verify(driver: PlaywrightDriver, mobile_number):
    try:
        verify_code = get_verify_code_from_api(mobile_number)
        verify_page = VerifyPage(driver)
        verify_page.verify(verify_code)
        driver.find_element((By.CLASS_NAME, "error-message"), timeout=100)
    except (NoSuchElementException, TimeoutException):
        #  In some cases a TimeoutException is raised even if we have managed to verify.
        #  For now, check explicitly if we 'have verified' and if so move on.
        return True
    else:
        #  There was an error message so let's retry
        raise RetryException


@retry(
    RetryException,
    tries=config["verify_code_retry_times"],
    delay=config["verify_code_retry_interval"],
)
def do_verify_by_id(driver: PlaywrightDriver, user_id):
    try:
        verify_code = get_verification_code_by_id(user_id)
        verify_page = VerifyPage(driver)
        with wait_for_page_load_completion(driver):
            verify_page.verify(verify_code)
        driver.find_element((By.CLASS_NAME, "error-message"), timeout=10)
    except (NoSuchElementException, TimeoutException):
        #  In some cases a TimeoutException is raised even if we have managed to verify.
        #  For now, check explicitly if we 'have verified' and if so move on.
        return True
    else:
        #  There was an error message so let's retry
        raise RetryException


def do_email_auth_verify(driver):
    do_email_verification(
        driver,
        config["notify_templates"]["email_auth_template_id"],
        config["service"]["email_auth_account"],
    )


@retry(
    RetryException,
    tries=config["verify_code_retry_times"],
    delay=config["verify_code_retry_interval"],
)
def do_email_verification(driver, template_id, email_address):
    try:
        email_link = get_link(template_id, email_address)
        driver.get(email_link)

        if (
            driver.find_element((By.CLASS_NAME, "heading-large")).text
            == "The link has expired"
        ):
            #  There was an error message (presumably we tried to use an email token that was already used/expired)
            raise RetryException

    except (NoSuchElementException, TimeoutException):
        # no error - that means we're logged in! hurray.
        return True


def create_broadcast_template(driver, reference="test template", content=None):
    show_templates_page = ShowTemplatesPage(driver)
    show_templates_page.click_add_new_template()

    choose_template_fields_page = ChooseTemplateFieldsPage(driver)
    # Selects checkbox for creating template with only content
    choose_template_fields_page.select_checkbox_or_radio(value="content_only")
    choose_template_fields_page.click_continue()

    template_page = EditBroadcastTemplatePage(driver)
    template_page.create_template(reference=reference, content=content)
    return template_page.get_template_id()


def go_to_service_dashboard(driver, service="service"):
    page = CurrentAlertsPage(driver)
    page.go_to_service_landing_page(config[service]["id"])


def go_to_templates_page(driver, service="service"):
    page = CurrentAlertsPage(driver)
    page.go_to_service_landing_page(config[service]["id"])
    page.click_templates()


def delete_template(driver, template_name, service="service"):
    show_templates_page = ShowTemplatesPage(driver)
    try:
        show_templates_page.click_template_by_link_text(template_name)
    except TimeoutException:
        page = CurrentAlertsPage(driver)
        page.go_to_service_landing_page(config[service]["id"])
        page.click_templates()
        show_templates_page.click_template_by_link_text(template_name)
    template_page = EditBroadcastTemplatePage(driver)
    template_page.click_delete()


def get_verify_code_from_api(mobile_number):
    verify_code_message = get_notification_by_to_field(
        config["notify_templates"]["verify_code_template_id"],
        config["notify_service_api_key"],
        mobile_number,
    )
    m = re.search(r"\d{5}", verify_code_message)
    if not m:
        raise RetryException(
            "Could not find a verify code for template {} sent to {}".format(
                config["notify_templates"]["verify_code_template_id"], mobile_number
            )
        )
    return m.group(0)


def get_notification_by_to_field(template_id, api_key, sent_to, statuses=None):
    client = NotificationsAPIClient(base_url=config["eas_api_url"], api_key=api_key)
    resp = client.get("v2/notifications")
    for notification in resp["notifications"]:
        t_id = notification["template"]["id"]
        to = notification["email_address"] or notification["phone_number"]
        if (
            t_id == template_id
            and to == sent_to
            and (not statuses or notification["status"] in statuses)
        ):
            return notification["body"]
    return ""


def get_verification_code_by_id(user_id):
    url = f'{config["eas_api_url"]}/verify-code/{user_id}'
    response = requests.get(url)
    return response.text


def recordtime(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            logging.info("Starting Test: {}".format(func.__name__))
            logging.info("Start Time: {}".format(str(datetime.now(timezone.utc))))
            result = func(*args, **kwargs)
            return result
        finally:
            logging.info("End Time: {}".format(str(datetime.now(timezone.utc))))

    return wrapper


def check_alert_is_published_on_govuk_alerts(
    driver, page_title, broadcast_content, extra_content=None
):
    gov_uk_alerts_page = GovUkAlertsPage(driver)
    gov_uk_alerts_page.get()
    gov_uk_alerts_page.click_element_by_link_text(page_title)
    gov_uk_alerts_page.check_alert_is_published(broadcast_content)
    if extra_content:
        gov_uk_alerts_page.get_alert_url(driver, broadcast_content)
        gov_uk_alerts_page.check_extra_content_appears(extra_content)


def create_sign_in_url(email, url, next_redirect=None):
    data = json.dumps({"email": email, "created_at": str(datetime.now(timezone.utc))})
    full_url = _url_with_token(data, f"/{url}/", config)
    if next_redirect:
        full_url += "?{}".format(urlencode({"next": next_redirect}))
    return full_url


def create_invitation_url(user_id):
    return _url_with_token(user_id, "/invitation/", config)


def _url_with_token(data, url, config):
    token = (
        URLSafeTimedSerializer(config["broadcast_service"]["secret_key"])
        .dumps(data, config["broadcast_service"]["dangerous_salt"])
        .replace(".", "%2E")
    )
    base_url = config["eas_admin_url"] + url
    return base_url + token


def create_ddb_client():
    try:
        sts_client = boto3.client("sts")

        logging.info(f"Creating DDB client for account {config['cbc_account_number']}")

        sts_session = sts_client.assume_role(
            RoleArn=f"arn:aws:iam::{config['cbc_account_number']}:role/mno-loopback-access-role",
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


def create_cloudwatch_client():
    try:
        sts_client = boto3.client("sts")

        sts_session = sts_client.assume_role(
            RoleArn=f"arn:aws:iam::{config['cbc_account_number']}:role/mno-loopback-access-role",
            RoleSessionName="access-cloudwatch-for-functional-test",
        )

        KEY_ID = sts_session["Credentials"]["AccessKeyId"]
        ACCESS_KEY = sts_session["Credentials"]["SecretAccessKey"]
        TOKEN = sts_session["Credentials"]["SessionToken"]

        try:
            return boto3.client(
                "cloudwatch",
                region_name="eu-west-2",
                aws_access_key_id=KEY_ID,
                aws_secret_access_key=ACCESS_KEY,
                aws_session_token=TOKEN,
            )

        except Exception as e:
            raise Exception("Unable to create CloudWatch client") from e

    except Exception as e:
        raise Exception("Unable to assume role") from e


def is_list_of_strings(arg):
    if isinstance(arg, list):
        return all(isinstance(item, str) for item in arg)
    return False


def set_response_codes(ddbc=None, response_code: int = 200, cbc_list=None):
    if ddbc is None:
        ddbc = create_ddb_client()

    if cbc_list is None:
        cbc_list = list(config["cbcs"].keys())

    if not is_list_of_strings(cbc_list):
        print("Please provide a list of cbc identifiers")
        return

    for cbc in cbc_list:
        ip = config["cbcs"][cbc]
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


def put_functional_test_blackout_metric(status: int):
    try:
        cwc = create_cloudwatch_client()
        cwc.put_metric_data(
            MetricData=[
                {
                    "MetricName": "FunctionalTestBlackout",
                    "Unit": "Count",
                    "Value": 1 if status > 299 else 0,
                },
            ],
            Namespace="FunctionalTests",
        )
    except BaseException as e:
        raise Exception("Error sending response code metric to CW") from e


def clear_proxy_error_alarm():
    try:
        cwc = create_cloudwatch_client()
        for mno in PROVIDERS:
            for az in ["1", "2"]:
                cwc.set_alarm_state(
                    AlarmName=f"{mno}-az{az}-proxy-error",
                    StateValue="OK",
                    StateReason="Functional test alarm reset",
                )
    except BaseException as e:
        raise Exception("Error writing proxy count metric to CW") from e
