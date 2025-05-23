import time

import pytest

from config import config
from tests.pages.pages import DashboardWithDialogs, SignInPage, VerifyPage
from tests.pages.rollups import clean_session
from tests.test_utils import get_verification_code_by_id

test_group_name = "session-timeout"


def sign_in_as_session_timeout_user(driver):
    login_email = config["broadcast_service"]["session_timeout"]["email"]
    login_pw = config["broadcast_service"]["session_timeout"]["password"]
    sign_in_page = SignInPage(driver)
    sign_in_page.get()
    sign_in_page.login(login_email, login_pw)

    assert sign_in_page.text_is_on_page("a text message with a security code")
    mfa_code = get_verification_code_by_id(
        config["broadcast_service"]["session_timeout"]["id"]
    )

    verify_page = VerifyPage(driver)
    verify_page.verify(code=mfa_code)


@pytest.mark.xdist_group(name=test_group_name)
def test_inactivity_dialog_appears_and_if_no_action_taken_user_is_signed_out(driver):
    clean_session(driver)

    sign_in_as_session_timeout_user(driver)
    sign_in_page = SignInPage(driver)

    dashboard_with_dialogs_page = DashboardWithDialogs(driver)
    assert dashboard_with_dialogs_page.text_is_on_page("Current alerts")
    dashboard_with_dialogs_page.click_element_by_link_text("Templates")
    assert dashboard_with_dialogs_page.is_page_title("Templates")
    time.sleep(6)
    assert dashboard_with_dialogs_page.is_inactivity_warning_dialog_visible()
    time.sleep(6)
    assert dashboard_with_dialogs_page.is_inactivity_dialog_visible()
    time.sleep(8)
    assert sign_in_page.text_is_on_page("You’ve been signed out due to inactivity")
    assert sign_in_page.text_is_on_page(
        "We do this to keep your information secure. Sign back in to continue where you left off."
    )
    assert dashboard_with_dialogs_page.url_contains("status=inactive")
    assert dashboard_with_dialogs_page.url_contains("templates")


@pytest.mark.xdist_group(name=test_group_name)
def test_inactivity_dialog_appears_and_sign_out_button_signs_user_out(driver):
    clean_session(driver)

    sign_in_as_session_timeout_user(driver)

    dashboard_with_dialogs_page = DashboardWithDialogs(driver)
    assert dashboard_with_dialogs_page.text_is_on_page("Current alerts")
    time.sleep(6)
    assert dashboard_with_dialogs_page.is_inactivity_warning_dialog_visible()
    time.sleep(6)
    assert dashboard_with_dialogs_page.is_inactivity_dialog_visible()
    dashboard_with_dialogs_page.click_element_by_link_text("Sign out now")
    sign_in_page = SignInPage(driver)
    assert sign_in_page.text_is_on_page("Sign in")


@pytest.mark.xdist_group(name=test_group_name)
def test_dialogs_appears_and_signs_user_out_at_max_session_lifetime(driver):
    clean_session(driver)

    sign_in_as_session_timeout_user(driver)

    dashboard_with_dialogs_page = DashboardWithDialogs(driver)
    assert dashboard_with_dialogs_page.text_is_on_page("Current alerts")
    time.sleep(5)
    assert dashboard_with_dialogs_page.is_inactivity_warning_dialog_visible()
    time.sleep(5)
    assert dashboard_with_dialogs_page.is_inactivity_dialog_visible()
    dashboard_with_dialogs_page.click_stay_signed_in()
    assert dashboard_with_dialogs_page.is_inactivity_dialog_hidden()
    dashboard_with_dialogs_page.click_element_by_link_text("Templates")
    assert dashboard_with_dialogs_page.is_page_title("Templates")
    time.sleep(5)
    assert dashboard_with_dialogs_page.is_inactivity_dialog_visible()
    dashboard_with_dialogs_page.click_stay_signed_in()
    assert dashboard_with_dialogs_page.is_inactivity_dialog_hidden()
    time.sleep(5)
    assert dashboard_with_dialogs_page.is_expiry_dialog_visible()
    dashboard_with_dialogs_page.click_continue()
    assert dashboard_with_dialogs_page.is_expiry_dialog_hidden()
    time.sleep(6)
    sign_in_page = SignInPage(driver)
    if sign_in_page.h1_is_youve_been_signed_out():
        assert sign_in_page.text_is_on_page(
            "We do this every 6 hours to keep your information secure. Sign back in to start a new session"
        )
        assert dashboard_with_dialogs_page.url_contains("status=expired")
        assert dashboard_with_dialogs_page.url_contains("templates")
    elif sign_in_page.text_is_on_page("You need to sign in again"):
        assert sign_in_page.text_is_on_page(
            "We signed you out because you have not used Emergency Alerts for a while"
        )


@pytest.mark.xdist_group(name=test_group_name)
def test_expiry_dialog_appears_and_click_sign_out_signs_user_out(driver):
    clean_session(driver)

    sign_in_as_session_timeout_user(driver)

    dashboard_with_dialogs_page = DashboardWithDialogs(driver)
    assert dashboard_with_dialogs_page.text_is_on_page("Current alerts")
    time.sleep(5)
    assert dashboard_with_dialogs_page.is_inactivity_dialog_visible()
    dashboard_with_dialogs_page.click_stay_signed_in()
    assert dashboard_with_dialogs_page.is_inactivity_dialog_hidden()
    time.sleep(5)
    assert dashboard_with_dialogs_page.is_inactivity_dialog_visible()
    dashboard_with_dialogs_page.click_stay_signed_in()
    assert dashboard_with_dialogs_page.is_inactivity_dialog_hidden()
    time.sleep(7)
    assert dashboard_with_dialogs_page.is_expiry_dialog_visible()
    dashboard_with_dialogs_page.click_element_by_link_text("Sign out now")
    sign_in_page = SignInPage(driver)
    assert sign_in_page.text_is_on_page("Sign in")
