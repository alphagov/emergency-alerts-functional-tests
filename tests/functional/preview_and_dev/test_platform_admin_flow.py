import time

import pytest

from tests.pages import AddServicePage, DashboardPage, ServiceSettingsPage
from tests.pages.locators import ServiceSettingsLocators
from tests.pages.pages import BasePage
from tests.pages.rollups import sign_in

TESTSUITE_CODE = "PLATFORM-ADMIN"


@pytest.mark.xdist_group(name=TESTSUITE_CODE)
def test_add_new_service_platform_admin(driver):
    timestamp = str(int(time.time()))
    service_name = f"Functional Test {timestamp}"

    sign_in(driver, account_type="platform_admin")

    landing_page = BasePage(driver)

    if not landing_page.is_text_present_on_page("Add a new service"):
        landing_page.click_element_by_link_text("Switch service")
        landing_page = BasePage(driver)
    landing_page.click_element_by_link_text("Add a new service")

    add_service_page = AddServicePage(driver)
    add_service_page.add_service(service_name)

    dashboard_page = DashboardPage(driver)
    service_id = dashboard_page.get_service_id()
    dashboard_page.go_to_dashboard_for_service(service_id)

    assert dashboard_page.get_service_name() == f"{service_name} TRAINING"

    # test service name change
    dashboard_page.click_element_by_link_text("Settings")
    service_settings_page = ServiceSettingsPage(driver)
    service_settings_page.click_element_by_link_text("Change service name")

    new_service_name = service_name + " NEW"
    service_settings_page.save_service_name(new_service_name)
    assert service_settings_page.check_service_name(new_service_name)

    # delete the service
    service_settings_page.click_element_by_link_text("Delete this service")
    delete_button = service_settings_page.wait_for_element(
        ServiceSettingsLocators.DELETE_CONFIRM_BUTTON
    )
    delete_button.click()

    assert service_settings_page.is_text_present_on_page(
        f"‘{service_name}’ was deleted"
    )

    # sign out
    service_settings_page.get()
    service_settings_page.sign_out()
