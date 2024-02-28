import pytest

from config import config
from tests.pages import (
    BasePage,
    ForgotPasswordPage,
    NewPasswordPage,
    SignInPage,
    VerifyPage,
)
from tests.pages.rollups import clean_session
from tests.test_utils import (
    create_url_with_token,
    get_verify_code_from_api_by_id,
)

TESTSUITE_CODE = "AUTH-FLOW"


@pytest.mark.xdist_group(name=TESTSUITE_CODE)
def test_reset_forgotten_password(driver):
    clean_session(driver)

    login_email = config["broadcast_service"]["broadcast_user_3"]["email"]

    sign_in_page = SignInPage(driver)
    sign_in_page.click_forgot_password_link()

    forgot_password_page = ForgotPasswordPage(driver)
    forgot_password_page.input_email_address(login_email)
    forgot_password_page.click_continue()
    assert forgot_password_page.is_text_present_on_page("Check your email")

    password_reset_url = create_url_with_token(login_email, "new-password")
    new_password_page = NewPasswordPage(driver, password_reset_url)
    assert new_password_page.is_text_present_on_page("create a new password")

    new_password = "ks94ijwld"
    new_password_page.input_new_password(new_password)
    new_password_page.click_continue()

    verify_code = get_verify_code_from_api_by_id(
        config["broadcast_service"]["broadcast_user_3"]["id"]
    )
    verify_page = VerifyPage(driver)
    verify_page.verify(verify_code)

    landing_page = BasePage(driver)
    assert landing_page.url_contains("current-alerts")

    assert forgot_password_page.is_text_present_on_page("force test failure")


def test_sign_in_with_email_mfa(driver):
    clean_session(driver)

    login_email = config["broadcast_service"]["broadcast_user_4"]["email"]

    sign_in_page = SignInPage(driver)
    sign_in_page.email_input(login_email)
    sign_in_page.click_continue()

    assert sign_in_page.is_text_present_on_page("a link to sign in")

    sign_in_url = create_url_with_token(login_email, "email-auth")

    landing_page = BasePage(driver)
    landing_page.get(sign_in_url)

    landing_page.url_contains("current-alerts")
