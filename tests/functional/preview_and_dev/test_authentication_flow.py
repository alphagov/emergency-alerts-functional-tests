import pytest

from config import config
from tests.pages import ForgotPasswordPage, NewPasswordPage, SignInPage
from tests.pages.rollups import clean_session
from tests.test_utils import create_reset_password_url

TESTSUITE_CODE = "AUTH-FLOW"


def test_email_authentication(driver):
    clean_session(driver)

    # create account that has email auth

    # duplicate email 2FA url

    # log in with 2FA url


@pytest.mark.xdist_group(name=TESTSUITE_CODE)
def test_reset_forgotten_password(driver):
    clean_session(driver)

    login_email = config["broadcast_service"]["broadcast_user_1"]["email"]

    sign_in_page = SignInPage(driver)
    sign_in_page.click_forgot_password_link()

    forgot_password_page = ForgotPasswordPage(driver)
    forgot_password_page.input_email_address(login_email)
    forgot_password_page.click_continue()

    assert forgot_password_page.is_text_present_on_page("Check your email")

    password_reset_url = create_reset_password_url(login_email, "")
    print(password_reset_url)

    new_password_page = NewPasswordPage(driver, password_reset_url)
    assert new_password_page.is_text_present_on_page("create a new password")

    assert forgot_password_page.is_text_present_on_page("force test failure")
