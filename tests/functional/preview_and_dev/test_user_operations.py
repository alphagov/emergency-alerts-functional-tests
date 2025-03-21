import time

import pytest

from tests.pages import CurrentAlertsPage, ProfileSettingsPage
from tests.pages.rollups import get_verify_code, sign_in

test_group_name = "user-operations"


@pytest.mark.xdist_group(name=test_group_name)
def test_user_can_change_profile_fields(driver):
    sign_in(driver, account_type="broadcast_create_user")

    current_alerts_page = CurrentAlertsPage(driver)
    current_alerts_page.click_element_by_link_text("Profile")

    profile_page = ProfileSettingsPage(driver)
    assert profile_page.text_is_on_page("Your profile")

    # Change username
    profile_page.click_change_setting("name")
    profile_page.wait_until_url_ends_with("/name")
    base_name = "Functional Tests - Broadcast User Create"
    new_name = f"{base_name} {str(int(time.time()))}"
    profile_page.save_name(new_name)
    profile_page.enter_password("Password1234")

    current_alerts_page.wait_until_url_ends_with("/user-profile")
    assert current_alerts_page.text_is_on_page(new_name)

    # Change mobile number
    profile_page.click_change_setting("mobile")
    profile_page.wait_until_url_ends_with("/mobile-number")
    assert profile_page.text_is_on_page("Change your mobile number")

    profile_page.save_mobile_number("+447700900000")
    profile_page.enter_password("Password1234")
    profile_page.wait_until_url_ends_with("/confirm")

    code = get_verify_code("broadcast_create_user")
    profile_page.enter_verification_code(code=code)

    profile_page.wait_until_url_ends_with("/user-profile")
    profile_page.get(relative_url="/user-profile")
    assert profile_page.text_is_on_page("+447700900000")

    # Revert changes to profile settings
    assert profile_page.text_is_on_page("Your profile")

    profile_page.click_change_setting("name")
    profile_page.wait_until_url_ends_with("/name")
    assert profile_page.text_is_on_page("Change your name")
    profile_page.save_name(base_name)
    profile_page.enter_password("Password1234")

    profile_page.wait_until_url_ends_with("/user-profile")
    assert profile_page.text_is_on_page(base_name)

    profile_page.click_change_setting("mobile")
    profile_page.wait_until_url_ends_with("/mobile-number")
    assert profile_page.text_is_on_page("Change your mobile number")
    profile_page.save_mobile_number("+447700900111")
    profile_page.enter_password("Password1234")
    profile_page.wait_until_url_ends_with("/confirm")

    code = get_verify_code("broadcast_create_user")
    profile_page.enter_verification_code(code=code)

    profile_page.wait_until_url_ends_with("/user-profile")
    profile_page.get(relative_url="/user-profile")
    assert profile_page.text_is_on_page("+447700900111")
    profile_page.sign_out()


@pytest.mark.xdist_group(name=test_group_name)
def test_user_can_view_team_members_but_not_invite_a_new_member(driver):
    sign_in(driver, account_type="broadcast_create_user")

    current_alerts_page = CurrentAlertsPage(driver)
    current_alerts_page.click_team_members_link()

    current_alerts_page.wait_until_url_ends_with("users")
    assert current_alerts_page.is_page_title("Team members")

    # verify presence of other users
    assert current_alerts_page.text_is_on_page("Functional Tests - Platform Admin")
    assert current_alerts_page.text_is_on_page(
        "Functional Tests - Broadcast User Approve"
    )

    # verify that invitation button is not available
    assert current_alerts_page.text_is_not_on_page("Invite a team member")

    current_alerts_page.sign_out()
