import random
import string
from urllib.parse import urlparse

import pytest

from config import config
from tests.pages import (
    BasePage,
    ForgotPasswordPage,
    NewPasswordPage,
    SignInPage,
    VerifyPage,
    action_group,
)
from tests.test_utils import (
    SuiteNames,
    create_email_mfa_sign_in_url,
    create_sign_in_url,
    get_verification_code_by_id,
    skip_test_suite_if_disabled,
)

test_group_name = "auth-flow"


@pytest.mark.xdist_group(name=test_group_name)
@skip_test_suite_if_disabled(test_suite_name=SuiteNames.AUTH_FLOW)
def test_reset_forgotten_password(driver, purge_failed_logins):
    user3 = config["broadcast_service"]["broadcast_user_3"]["id"]
    login_email = config["broadcast_service"]["broadcast_user_3"]["email"]

    sign_in_page = SignInPage(driver)
    sign_in_page.get()
    sign_in_page.click_forgot_password_link()

    forgot_password_page = ForgotPasswordPage(driver)
    forgot_password_page.input_email_address(login_email)
    forgot_password_page.click_submit()
    assert forgot_password_page.text_is_on_page("Check your email")

    password_reset_url = create_sign_in_url(login_email, "new-password")
    new_password_page = NewPasswordPage(driver, password_reset_url)
    assert new_password_page.text_is_on_page("create a new password")

    new_password = "".join(
        [
            random.choice(string.ascii_letters + string.digits + string.punctuation)
            for _ in range(15)
        ]
    )
    new_password_page.input_new_password(new_password)
    purge_failed_logins()
    new_password_page.click_continue_to_signin()

    verify_page = VerifyPage(driver)
    verify_page.get(relative_url="two-factor-sms")
    verify_code = get_verification_code_by_id(user3)
    verify_page.verify(verify_code)

    sign_in_page.get()
    sign_in_page.login(login_email, new_password)

    verify_page.get(relative_url="two-factor-sms")
    verify_code = get_verification_code_by_id(user3)
    verify_page.verify(verify_code)

    landing_page = BasePage(driver)
    assert landing_page.url_contains("current-alerts")


@pytest.mark.xdist_group(name=test_group_name)
@skip_test_suite_if_disabled(test_suite_name=SuiteNames.AUTH_FLOW)
def test_sign_in_with_email_mfa(driver, purge_failed_logins):
    login_id = config["broadcast_service"]["broadcast_user_4"]["id"]
    login_email = config["broadcast_service"]["broadcast_user_4"]["email"]
    login_pw = config["broadcast_service"]["broadcast_user_4"]["password"]

    purge_failed_logins()
    sign_in_page = SignInPage(driver)
    sign_in_page.get()
    assert sign_in_page.is_current()
    sign_in_page.login(login_email, login_pw)

    sign_in_page.wait_until_url_ends_with("/two-factor-email-sent")
    assert sign_in_page.text_is_on_page("a link to sign in")

    purge_failed_logins()

    verify_code = get_verification_code_by_id(login_id)
    sign_in_url = create_email_mfa_sign_in_url(login_id, verify_code, "email-auth")

    landing_page = BasePage(driver)
    landing_page.get(sign_in_url)
    assert landing_page.text_is_on_page("Switch service")


@pytest.mark.xdist_group(name=test_group_name)
@skip_test_suite_if_disabled(test_suite_name=SuiteNames.AUTH_FLOW)
def test_sign_in_with_webauthn_mfa(driver, purge_failed_logins):
    login_email = config["broadcast_service"]["webauthn"]["email"]
    login_pw = config["broadcast_service"]["webauthn"]["password"]

    with action_group(driver, "Setup virtual WebAuthn"):
        # Install the fake hardware MFA via Chrome devtools protocol
        client = driver.page.context.new_cdp_session(driver.page)
        client.send("WebAuthn.enable")
        result = client.send(
            "WebAuthn.addVirtualAuthenticator",
            {
                "options": {
                    # U2F-style security key - not a Passkey (no residency)
                    "protocol": "u2f",
                    "transport": "usb",
                    "hasResidentKey": False,
                }
            },
        )

        authenticator_id = result["authenticatorId"]
        relying_party_id = urlparse(config["eas_admin_url"]).hostname
        client.send(
            "WebAuthn.addCredential",
            {
                "authenticatorId": authenticator_id,
                "credential": {
                    # These values must *exactly* correlate with credential_data encoded as CBOR in
                    # the webauthn_credential table ...or put simply, there's no point paramterising
                    # it as they're long and complicated.
                    "credentialId": "9s2l4k0SR/U/jR48as69U/aOZXI9OHg1MG1r2lQ5qJg=",
                    "isResidentCredential": False,
                    "rpId": relying_party_id,
                    "privateKey": "MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQg/"
                    + "tRNVidBeIGCML1qlhQXEsaRy98uNW1N5OchhpXfCq6hRANCAATDZPqXSkAfNhqXOXwk9KqFphlYXVu"
                    + "VU5FzF2IJX8HqQih9rcQlYLeTFxfuU+X44rBFQJ+Vdj2zoflLAdf5+AAt",
                    "signCount": 1,
                },
            },
        )

    purge_failed_logins()
    sign_in_page = SignInPage(driver)
    assert sign_in_page.is_current()
    sign_in_page.login(login_email, login_pw)

    sign_in_page.wait_until_url_ends_with("/two-factor-webauthn")
    sign_in_page.click_element_by_link_text("Check security key")

    sign_in_page.wait_until_url_ends_with("current-alerts")
