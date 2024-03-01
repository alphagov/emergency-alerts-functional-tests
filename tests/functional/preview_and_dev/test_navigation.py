import pytest

from tests.pages import BasePage
from tests.pages.rollups import sign_in

TESTSUITE_CODE = "BASIC-NAV"


@pytest.mark.xdist_group(name=TESTSUITE_CODE)
def test_user_left_rail_nav(driver):
    sign_in(driver, account_type="broadcast_create_user")

    landing_page = BasePage(driver)
    assert landing_page.url_contains("current-alerts")
    assert landing_page.is_page_title("Current alerts")

    landing_page.click_element_by_link_text("Past alerts")
    assert landing_page.url_contains("past-alerts")
    assert landing_page.is_page_title("Past alerts")

    landing_page.click_element_by_link_text("Rejected alerts")
    assert landing_page.url_contains("rejected-alerts")
    assert landing_page.is_page_title("Rejected alerts")

    landing_page.click_element_by_link_text("Templates")
    assert landing_page.url_contains("rejected-alerts")
    assert landing_page.is_page_title("Templates")

    landing_page.click_element_by_link_text("Team membmers")
    assert landing_page.url_contains("users")
    assert landing_page.is_page_title("Team membmers")


@pytest.mark.xdist_group(name=TESTSUITE_CODE)
def test_footer_links(driver):
    sign_in(driver, account_type="broadcast_create_user")
    back_link = "accounts-or-dashboard"

    landing_page = BasePage(driver)
    landing_page.click_element_by_link_text("Privacy")
    assert landing_page.url_contains("privacy")
    assert landing_page.is_page_title("Emergency Alerts administrators privacy notice")

    landing_page.get(relative_url=back_link)
    landing_page.click_element_by_link_text("Accessibility statement")
    assert landing_page.url_contains("accessibility-statement")
    assert landing_page.is_page_title("Accessibility statement")

    landing_page.get(relative_url=back_link)
    landing_page.click_element_by_link_text("Terms of use")
    assert landing_page.url_contains("terms")
    assert landing_page.is_page_title("Terms of use")

    landing_page.get(relative_url=back_link)
    landing_page.click_element_by_link_text("Cookies")
    assert landing_page.url_contains("cookies")
    assert landing_page.is_page_title("Cookies")

    landing_page.get(relative_url=back_link)
    landing_page.click_element_by_link_text("Security")
    assert landing_page.url_contains("security")
    assert landing_page.is_page_title("security")


@pytest.mark.xdist_group(name=TESTSUITE_CODE)
def test_reject_analytics_cookies(driver):
    sign_in(driver, account_type="broadcast_create_user")

    landing_page = BasePage(driver)
    landing_page.click_element_by_link_text("Cookies")
    assert landing_page.is_page_title("Cookies")

    landing_page.click_element_by_id("cookies-analytics-no")
    landing_page.click_continue()
    assert landing_page.is_text_present_on_page("cookie settings were saved")

    landing_page.sign_out()

    sign_in(driver, account_type="broadcast_create_user")
    assert driver.get_cookie("notify_admin_session")
    assert driver.get_cookie("cookie_policy")
    assert not driver.get_cookie("_ga")
    assert not driver.get_cookie("_gid")
