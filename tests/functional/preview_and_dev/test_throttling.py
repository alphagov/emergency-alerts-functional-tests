import time

import pytest

from config import config
from tests.pages import BasePage, HomePage, SignInPage, ThrottledPage
from tests.pages.pages import VerifyPage
from tests.pages.rollups import clean_session
from tests.test_utils import get_verification_code_by_id, recordtime

test_group_name = "throttling"


@recordtime
@pytest.mark.xdist_group(name=test_group_name)
def test_login_attempt_throttled_after_failed_login(driver, purge_failed_logins):
    clean_session(driver)
    purge_failed_logins()

    home_page = HomePage(driver)
    home_page.get()
    home_page.accept_cookie_warning()

    login_email = config["broadcast_service"]["throttled_user"]["email"]
    login_pw = "incorrect password"

    sign_in_page = SignInPage(driver)
    sign_in_page.get()
    assert sign_in_page.is_current()
    sign_in_page.login(login_email, login_pw)

    # Assert here that error text appears
    assert (
        sign_in_page.get_errors().split(".")[0]
        == "The email address or password you entered is incorrect"
    )

    sign_in_page.get()
    assert sign_in_page.is_current()
    sign_in_page.login(login_email, login_pw)

    # Assert here that error text appears for second time
    assert (
        sign_in_page.get_errors().split(".")[0]
        == "The email address or password you entered is incorrect"
    )

    # Wait out the throttle period
    time.sleep(5)

    sign_in_page.get()
    assert sign_in_page.is_current()
    sign_in_page.login(login_email, login_pw)

    # Assert here that error text appears for third time
    assert (
        sign_in_page.get_errors().split(".")[0]
        == "The email address or password you entered is incorrect"
    )

    # Attempts again with correct credentials
    login_email = config["broadcast_service"]["throttled_user"]["email"]
    login_pw = config["broadcast_service"]["throttled_user"]["password"]

    sign_in_page = SignInPage(driver)
    sign_in_page.get()
    assert sign_in_page.is_current()
    sign_in_page.login(login_email, login_pw)

    throttled_page = ThrottledPage(driver)
    assert throttled_page.text_is_on_page("Too many requests")
    assert throttled_page.text_is_on_page(
        "You've been temporarily throttled due to too many login attempts."
    )

    # Waits some time to avoid throttle
    time.sleep(5)

    # Attempts again
    throttled_page.click_element_by_link_text("Sign in")

    login_email = config["broadcast_service"]["throttled_user"]["email"]
    login_pw = config["broadcast_service"]["throttled_user"]["password"]

    sign_in_page = SignInPage(driver)
    sign_in_page.get()
    assert sign_in_page.is_current()
    sign_in_page.login(login_email, login_pw)

    # Successful login renders MFA page

    assert sign_in_page.text_is_on_page("a text message with a security code")
    mfa_code = get_verification_code_by_id(
        config["broadcast_service"]["throttled_user"]["id"]
    )

    verify_page = VerifyPage(driver)
    verify_page.verify(code=mfa_code)

    landing_page = BasePage(driver)
    assert landing_page.url_contains("current-alerts")

    landing_page.sign_out()
