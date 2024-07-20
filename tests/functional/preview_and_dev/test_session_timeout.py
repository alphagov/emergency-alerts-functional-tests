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
def test_inactivity_dialog_appears(driver):
    clean_session(driver)
    sign_in(driver, account_type="session_timeout")
    inactive_dashboard_page = DashboardWithInactivityDialog(driver)
    time.sleep(30)
    assert inactive_dashboard_page.inactivity_dialog.is_displayed()


@pytest.mark.xdist_group(name=test_group_name)
def test_expiry_dialog_appears(driver):
    clean_session(driver)
    sign_in(driver, account_type="session_timeout")
    inactive_dashboard_page = DashboardWithInactivityDialog(driver)
    time.sleep(30)
    assert inactive_dashboard_page.inactivity_dialog.is_displayed()
    inactive_dashboard_page.click_stay_signed_in()
    time.sleep(30)
    inactive_dashboard_page.click_stay_signed_in()
    time.sleep(30)
    inactive_dashboard_page.click_stay_signed_in()
    time.sleep(30)
    dashboard_to_expire_page = DashboardWithExpiryDialog(driver)
    assert dashboard_to_expire_page.expiry_dialog.is_displayed()
    time.sleep(30)


@pytest.mark.xdist_group(name=test_group_name)
def test_activity_in_another_tab_delays_dialog(driver):
    clean_session(driver)
    sign_in(driver, account_type="session_timeout")
    time.sleep(300)


@pytest.mark.xdist_group(name=test_group_name)
def test_expiry_auto_logout_retains_last_page(driver):
    clean_session(driver)
    sign_in(driver, account_type="session_timeout")
    inactive_dashboard_page = DashboardWithInactivityDialog(driver)
    time.sleep(30)
    assert inactive_dashboard_page.inactivity_dialog.is_displayed()
    inactive_dashboard_page.click_stay_signed_in()
    time.sleep(30)
    inactive_dashboard_page.click_stay_signed_in()
    time.sleep(30)
    inactive_dashboard_page.click_stay_signed_in()
    time.sleep(30)
    dashboard_to_expire_page = DashboardWithExpiryDialog(driver)
    assert dashboard_to_expire_page.expiry_dialog.is_displayed()
    dashboard_to_expire_page.click_sign_out()
    sign_in_page = SignInPage(driver)
    assert sign_in_page.is_text_present_on_page("You've been signed out")


@pytest.mark.xdist_group(name=test_group_name)
def test_inactivity_auto_logout_retains_last_page(driver):
    clean_session(driver)
    sign_in(driver, account_type="session_timeout")
    inactive_dashboard_page = DashboardWithInactivityDialog(driver)
    time.sleep(60)
    assert inactive_dashboard_page.inactivity_dialog.is_displayed()
    inactive_dashboard_page.click_stay_signed_in()
    time.sleep(30)
    inactive_dashboard_page.click_stay_signed_in()
    time.sleep(30)
    inactive_dashboard_page.click_stay_signed_in()
    time.sleep(30)
    dashboard_to_expire_page = DashboardWithExpiryDialog(driver)
    assert dashboard_to_expire_page.expiry_dialog.is_displayed()
    dashboard_to_expire_page.click_sign_out()
    sign_in_page = SignInPage(driver)
    assert sign_in_page.is_text_present_on_page("You've been signed out")
