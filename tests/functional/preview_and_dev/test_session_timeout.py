import time

import pytest

from tests.pages.pages import (
    DashboardWithExpiryDialog,
    DashboardWithInactivityDialog,
    SignInPage,
)
from tests.pages.rollups import clean_session, sign_in

test_group_name = "session-timeout"


@pytest.mark.xdist_group(name=test_group_name)
def test_inactivity_dialog_appears_and_if_no_action_taken_user_is_signed_out(driver):
    clean_session(driver)
    sign_in(driver, account_type="session_timeout")
    inactive_dashboard_page = DashboardWithInactivityDialog(driver)
    inactive_dashboard_page.click_element_by_link_text("Templates")
    assert inactive_dashboard_page.is_page_title("Templates")
    time.sleep(11)
    assert inactive_dashboard_page.is_dialog_visible()
    time.sleep(10)
    sign_in_page = SignInPage(driver)
    assert sign_in_page.is_text_present_on_page(
        "You’ve been signed out due to inactivity"
    )
    assert sign_in_page.is_text_present_on_page(
        "We do this to keep your information secure. Sign back in to continue where you left off."
    )
    assert inactive_dashboard_page.url_contains("status=inactive")
    assert inactive_dashboard_page.url_contains("templates")


@pytest.mark.xdist_group(name=test_group_name)
def test_dialogs_appears_and_signs_user_out_at_max_session_lifetime(driver):
    clean_session(driver)
    sign_in(driver, account_type="session_timeout")
    inactive_dashboard_page = DashboardWithInactivityDialog(driver)
    time.sleep(11)
    assert inactive_dashboard_page.is_dialog_visible()
    inactive_dashboard_page.click_stay_signed_in()
    assert not inactive_dashboard_page.is_dialog_visible()
    inactive_dashboard_page.click_element_by_link_text("Templates")
    assert inactive_dashboard_page.is_page_title("Templates")
    time.sleep(20)
    dashboard_to_expire_page = DashboardWithExpiryDialog(driver)
    assert dashboard_to_expire_page.expiry_dialog.is_dialog_visible()
    dashboard_to_expire_page.click_continue()
    assert not dashboard_to_expire_page.is_dialog_visible()
    time.sleep(10)
    sign_in_page = SignInPage(driver)
    assert sign_in_page.is_text_present_on_page("You’ve been signed out")
    assert sign_in_page.is_text_present_on_page(
        "We do this every hour to keep your information secure. Sign back in to start a new session"
    )
    assert inactive_dashboard_page.url_contains("status=expired")
    assert inactive_dashboard_page.url_contains("templates")


@pytest.mark.xdist_group(name=test_group_name)
def test_inactivity_dialog_appears_and_sign_out_button_signs_user_out(driver):
    clean_session(driver)
    sign_in(driver, account_type="session_timeout")
    inactive_dashboard_page = DashboardWithInactivityDialog(driver)
    time.sleep(11)
    assert inactive_dashboard_page.is_dialog_visible()
    inactive_dashboard_page.click_sign_out()
    assert not inactive_dashboard_page.is_dialog_visible()
    sign_in_page = SignInPage(driver)
    assert sign_in_page.is_text_present_on_page("Sign in")


@pytest.mark.xdist_group(name=test_group_name)
def test_expiry_dialog_appears_and_click_sign_out_signs_user_out(driver):
    clean_session(driver)
    sign_in(driver, account_type="session_timeout")
    inactive_dashboard_page = DashboardWithInactivityDialog(driver)
    time.sleep(11)
    assert inactive_dashboard_page.is_dialog_visible()
    inactive_dashboard_page.click_stay_signed_in()
    assert not inactive_dashboard_page.is_dialog_visible()
    time.sleep(20)
    dashboard_to_expire_page = DashboardWithExpiryDialog(driver)
    assert dashboard_to_expire_page.is_dialog_visible()
    dashboard_to_expire_page.click_sign_out()
    sign_in_page = SignInPage(driver)
    assert sign_in_page.is_text_present_on_page("Sign in")
