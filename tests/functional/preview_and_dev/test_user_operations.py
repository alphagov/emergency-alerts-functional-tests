import pytest

from tests.pages import DashboardPage, ProfileSettingsPage
from tests.pages.rollups import sign_in

test_group_name = "user-operations"


@pytest.mark.xdist_group(name=test_group_name)
def test_user_can_change_profile_fields(driver):
    sign_in(driver, account_type="broadcast_create_user")

    dashboard_page = DashboardPage(driver)
    dashboard_page.click_element_by_link_text("Profile")

    profile_page = ProfileSettingsPage(driver)
    assert profile_page.is_text_present_on_page("Your profile")

    # Change username
    profile_page.click_change_setting("name")
    profile_page.wait_until_url_ends_with("/name")
    profile_page.save_name("Functional Tests - Broadcast User Create - NEW")

    dashboard_page.wait_until_url_ends_with("/user-profile")
    assert dashboard_page.is_text_present_on_page(
        "Functional Tests - Broadcast User Create - NEW"
    )

    # Change mobile number
    profile_page.click_change_setting("mobile")
    profile_page.wait_until_url_ends_with("/mobile-number")
    profile_page.save_mobile_number("+447700900000")

    dashboard_page.wait_until_url_ends_with("/user-profile")
    assert dashboard_page.is_text_present_on_page("+447700900000")

    # Revert changes to profile settings
    assert profile_page.is_text_present_on_page("Your profile")

    profile_page.click_change_setting("name")
    profile_page.wait_until_url_ends_with("/name")
    profile_page.save_name("Functional Tests - Broadcast User Create")

    dashboard_page.wait_until_url_ends_with("/user-profile")
    assert dashboard_page.is_text_present_on_page(
        "Functional Tests - Broadcast User Create"
    )

    profile_page.click_change_setting("mobile")
    profile_page.wait_until_url_ends_with("/mobile-number")
    profile_page.save_mobile_number("+447700900111")

    dashboard_page.wait_until_url_ends_with("/user-profile")
    assert dashboard_page.is_text_present_on_page("+447700900111")


@pytest.mark.xdist_group(name=test_group_name)
def test_user_can_view_team_members_but_not_invite_a_new_member(driver):
    sign_in(driver, account_type="broadcast_create_user")

    dashboard_page = DashboardPage(driver)
    dashboard_page.click_team_members_link()

    dashboard_page.wait_until_url_ends_with("users")
    assert dashboard_page.is_page_title("Team members")

    # verify presence of other users
    assert dashboard_page.is_text_present_on_page("Functional Tests - Platform Admin")
    assert dashboard_page.is_text_present_on_page(
        "Functional Tests - Broadcast User Approve"
    )

    # verify that invitation button is not available
    assert not dashboard_page.is_text_present_on_page("Invite a team member")
