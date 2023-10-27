import uuid

import pytest

from tests.pages import AddServicePage, DashboardPage, ServiceSettingsPage
from tests.pages.rollups import sign_in
from tests.test_utils import recordtime


@recordtime
@pytest.mark.xdist_group(name="platform-admin")
def test_add_new_service_platform_admin(driver):
    temp_service_uuid = str(uuid.uuid4())

    sign_in(driver, account_type="platform_admin")

    service_name = f"Functional Test_{temp_service_uuid}"

    add_service_page = AddServicePage(driver)
    assert add_service_page.is_current()
    add_service_page.add_service(service_name)

    dashboard_page = DashboardPage(driver)
    service_id = dashboard_page.get_service_id()
    dashboard_page.go_to_dashboard_for_service(service_id)

    assert dashboard_page.get_service_name() == service_name

    service_settings_page = ServiceSettingsPage(driver)
    service_settings_page.click_element_by_link_text("Delete this service")
    service_settings_page.click_element_by_link_text("Yes, delete")

    assert service_settings_page.is_text_present_on_page(
        f"‘{service_name}’ was deleted"
    )

    # sign out
    service_settings_page.get()
    service_settings_page.sign_out()
