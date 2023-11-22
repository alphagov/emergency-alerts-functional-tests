import os
import uuid

import pytest


def generate_unique_email(email, uuid):
    parts = email.split("@")
    return "{}+{}@{}".format(parts[0], uuid, parts[1])


# global variable
config = {
    # static
    "notification_retry_times": 15,
    "notification_retry_interval": 5,
    "letter_retry_times": 48,
    "provider_retry_times": 12,
    "provider_retry_interval": 22,
    "verify_code_retry_times": 8,
    "verify_code_retry_interval": 9,
    "govuk_alerts_wait_retry_times": 24,
    "govuk_alerts_wait_retry_interval": 10,
    "functional_test_service_name": "Functional Test Service_",
    "letter_contact_data": {
        "address_line_1": "test",
        "address_line_2": "London",
        "postcode": "N1 7RA",
    },
    "notify_templates": {
        "email_auth_template_id": "299726d2-dba6-42b8-8209-30e1d66ea164",
        "invitation_template_id": "4f46df42-f795-4cc4-83bb-65ca312f49cc",
        "org_invitation_template_id": "203566f0-d835-47c5-aa06-932439c86573",
        "password_reset_template_id": "474e9242-823b-4f99-813d-ed392e7f1201",
        "registration_template_id": "ece42649-22a8-4d06-b87f-d52d5d3f0a27",
        "verify_code_template_id": "36fb0730-6259-4da1-8a80-c8de22ad4246",
    },
}


urls = {
    "development": {
        "api": "http://localhost:6011",
        "admin": "http://localhost:6012",
        "govuk_alerts": "http://localhost:6017/alerts",
    },
    "preview": {
        "api": "https://api.preview.emergency-alerts.service.gov.uk",
        "admin": "https://admin.preview.emergency-alerts.service.gov.uk",
        "govuk_alerts": "https://d70jn492f2qbx.cloudfront.net",
    },
}


def setup_shared_config():
    """
    Used by all tests
    """
    env = os.environ["ENVIRONMENT"].lower()

    # if env not in {"dev", "preview", "ecs-preview", "staging", "live"}:
    #     pytest.fail('env "{}" not one of dev, preview, staging, live'.format(env))
    if env not in {"development", "preview"}:
        pytest.fail('env "{}" not development or preview'.format(env))

    config.update(
        {
            "env": env,
            "notify_api_url": urls[env]["api"],
            "notify_admin_url": urls[env]["admin"],
            "govuk_alerts_url": urls[env]["govuk_alerts"],
        }
    )


def setup_preview_dev_config():
    uuid_for_test_run = str(uuid.uuid4())

    config.update(
        {
            "service_name": "Functional Test_{}".format(uuid_for_test_run),
            "user": {
                "name": "{}_Functional Test_{}".format(
                    config["env"], uuid_for_test_run
                ),
                "email": generate_unique_email(
                    os.environ["FUNCTIONAL_TEST_EMAIL"], uuid_for_test_run
                ),
                "password": os.environ["FUNCTIONAL_TEST_PASSWORD"],
                "mobile": os.environ["TEST_NUMBER"],
            },
            "notify_service_api_key": os.environ["NOTIFY_SERVICE_API_KEY"],
            "broadcast_service": {
                "id": os.environ["BROADCAST_SERVICE_ID"],
                "broadcast_user_1": {
                    "id": os.environ["BROADCAST_USER_1_ID"],
                    "email": os.environ["BROADCAST_USER_1_EMAIL"],
                    # we are re-using seeded user's password
                    "password": os.environ["FUNCTIONAL_TESTS_SERVICE_EMAIL_PASSWORD"],
                    "mobile": os.environ["BROADCAST_USER_1_NUMBER"],
                },
                "broadcast_user_2": {
                    "id": os.environ["BROADCAST_USER_2_ID"],
                    "email": os.environ["BROADCAST_USER_2_EMAIL"],
                    # we are re-using seeded user's password
                    "password": os.environ["FUNCTIONAL_TESTS_SERVICE_EMAIL_PASSWORD"],
                    "mobile": os.environ["BROADCAST_USER_2_NUMBER"],
                },
                "api_key_live": os.environ["BROADCAST_SERVICE_API_KEY"],
            },
            "service": {
                "id": os.environ["FUNCTIONAL_TESTS_SERVICE_ID"],
                "name": os.environ["FUNCTIONAL_TESTS_SERVICE_NAME"],
                "seeded_user": {
                    "email": os.environ["FUNCTIONAL_TESTS_SERVICE_EMAIL"],
                    "password": os.environ["FUNCTIONAL_TESTS_SERVICE_EMAIL_PASSWORD"],
                    "mobile": os.environ["FUNCTIONAL_TESTS_SERVICE_NUMBER"],
                },
                "api_live_key": os.environ["FUNCTIONAL_TESTS_SERVICE_API_KEY"],
                "api_test_key": os.environ["BROADCAST_SERVICE_API_KEY"],
                # email address of seeded email auth user
                "email_auth_account": os.environ[
                    "FUNCTIONAL_TESTS_SERVICE_EMAIL_AUTH_ACCOUNT"
                ],
                "organisation_id": os.environ["FUNCTIONAL_TESTS_ORGANISATION_ID"],
                "email_reply_to": os.environ["FUNCTIONAL_TESTS_SERVICE_EMAIL_REPLY_TO"],
                "email_reply_to_2": os.environ.get(
                    "FUNCTIONAL_TESTS_SERVICE_EMAIL_REPLY_TO_2"
                ),
                "email_reply_to_3": os.environ.get(
                    "FUNCTIONAL_TESTS_SERVICE_EMAIL_REPLY_TO_3"
                ),
                "sms_sender_text": "func tests",
                "templates": {
                    "email": os.environ["JENKINS_BUILD_EMAIL_TEMPLATE_ID"],
                    "sms": os.environ["JENKINS_BUILD_SMS_TEMPLATE_ID"],
                    "letter": os.environ["JENKINS_BUILD_LETTER_TEMPLATE_ID"],
                },
                "inbound_number": os.environ["FUNCTIONAL_TESTS_SERVICE_INBOUND_NUMBER"],
            },
            "mmg_inbound_sms": {
                "username": os.environ["MMG_INBOUND_SMS_USERNAME"],
                "password": os.environ["MMG_INBOUND_SMS_AUTH"],
            },
            "cbcs": ["ee", "vodafone", "o2", "three"],
        }
    )


def setup_staging_prod_config():
    # staging and prod run the same simple smoke tests
    config.update(
        {
            "name": "{} Functional Tests".format(config["env"]),
            "user": {
                "email": os.environ["FUNCTIONAL_TEST_EMAIL"],
                "password": os.environ["FUNCTIONAL_TEST_PASSWORD"],
                "mobile": os.environ["TEST_NUMBER"],
            },
            "notify_service_api_key": os.environ["NOTIFY_SERVICE_API_KEY"],
            "service": {
                "id": os.environ["SERVICE_ID"],
                "api_live_key": os.environ["API_KEY"],
                "api_test_key": os.environ["API_TEST_KEY"],
                "email_auth_account": os.environ["FUNCTIONAL_TEST_EMAIL_AUTH"],
                "seeded_user": {"password": os.environ["FUNCTIONAL_TEST_PASSWORD"]},
                "templates": {
                    "email": os.environ["JENKINS_BUILD_EMAIL_TEMPLATE_ID"],
                    "sms": os.environ["JENKINS_BUILD_SMS_TEMPLATE_ID"],
                    # letter template not set up on staging and prod
                },
                "inbound_number": os.environ["PROVIDER_TEST_INBOUND_NUMBER"],
            },
        }
    )
