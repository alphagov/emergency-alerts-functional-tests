import time

import pytest

from tests.pages import AddServicePage, CurrentAlertsPage, ServiceSettingsPage
from tests.pages.pages import (
    AdminApprovalsPage,
    ApiKeysPage,
    BasePage,
    HomePage,
    InviteUserPage,
    PlatformAdminPage,
    RegisterFromInvite,
    TeamMembersPage,
    VerifyPage,
)
from tests.pages.rollups import sign_in, sign_in_elevated_platform_admin
from tests.test_utils import create_invitation_url, get_verification_code_by_id

test_group_name = "platform-admin"


@pytest.mark.xdist_group(name=test_group_name)
def test_add_rename_and_delete_training_service(driver, purge_failed_logins):
    timestamp = str(int(time.time()))
    service_name = f"Functional Test {timestamp}"

    sign_in_elevated_platform_admin(driver, purge_failed_logins)

    landing_page = BasePage(driver)

    if landing_page.text_is_not_on_page("Add a new service"):
        landing_page.click_element_by_link_text("Switch service")
        landing_page = BasePage(driver)
    landing_page.click_element_by_link_text("Add a new service")

    add_service_page = AddServicePage(driver)
    add_service_page.add_service(service_name)
    add_service_page.select_training_mode()
    add_service_page.confirm_settings()

    service_settings_page = ServiceSettingsPage(driver)
    assert service_settings_page.get_service_name() == f"{service_name} TRAINING"

    service_settings_page.click_change_setting("service name")

    new_service_name = service_name + " NEW"
    service_settings_page.save_service_name(new_service_name)
    assert service_settings_page.get_service_name() == f"{new_service_name} TRAINING"

    service_settings_page.delete_service()
    assert service_settings_page.text_is_on_page_no_wait(
        f"‘{new_service_name}’ was deleted"
    )

    service_settings_page.sign_out()


@pytest.mark.xdist_group(name=test_group_name)
def test_add_modify_and_delete_live_service(driver, purge_failed_logins):
    timestamp = str(int(time.time()))
    service_name = f"Functional Test {timestamp}"

    sign_in_elevated_platform_admin(driver, purge_failed_logins)

    landing_page = BasePage(driver)

    if landing_page.text_is_not_on_page("Add a new service"):
        landing_page.click_element_by_link_text("Switch service")
        landing_page = BasePage(driver)
    landing_page.click_element_by_link_text("Add a new service")

    add_service_page = AddServicePage(driver)
    add_service_page.add_service(service_name)
    add_service_page.select_operator_mode()

    choose_operator_page = BasePage(driver)
    choose_operator_page.wait_until_url_ends_with("/operator")
    assert choose_operator_page.is_page_title("Choose one or more mobile networks")
    choose_operator_page.select_checkbox_or_radio(value="all")
    choose_operator_page.click_continue()

    confirm_settings_page = BasePage(driver)
    confirm_settings_page.wait_until_url_ends_with("/confirm")
    assert confirm_settings_page.is_page_title("Confirm emergency alert settings")
    confirm_settings_page.click_continue_to_submit()
    confirm_settings_page.wait_until_url_ends_with("/service-settings")

    service_settings_page = ServiceSettingsPage(driver)
    assert service_settings_page.get_service_name() == f"{service_name} OPERATOR"
    service_settings_page.click_change_setting("emergency alerts")

    change_service_page = AddServicePage(driver)
    change_service_page.select_operator_mode()
    change_service_page.select_checkbox_or_radio(value="ee")
    change_service_page.select_checkbox_or_radio(value="o2")
    choose_operator_page.click_continue()

    confirm_settings_page = BasePage(driver)
    confirm_settings_page.wait_until_url_ends_with("/confirm")
    assert confirm_settings_page.is_page_title("Confirm emergency alert settings")
    confirm_settings_page.click_continue_to_submit()

    service_settings_page = ServiceSettingsPage(driver)
    assert (
        service_settings_page.get_service_name()
        == f"{service_name} OPERATOR (THREE, VODAFONE)"
    )

    service_settings_page.delete_service()
    assert service_settings_page.text_is_on_page(f"‘{service_name}’ was deleted")

    # sign out
    service_settings_page.get()
    service_settings_page.sign_out()


@pytest.mark.xdist_group(name=test_group_name)
@pytest.mark.parametrize(
    "user_requires_admin_approval",
    ((True), (False)),
)
def test_platform_admin_can_invite_new_user_and_delete_user(
    driver, api_client, purge_failed_logins, user_requires_admin_approval
):
    """
    This refers to the unprivileged user flow - i.e. a user without a permission that would
    require approval from another admin.
    """
    timestamp = str(int(time.time()))

    sign_in_elevated_platform_admin(driver, purge_failed_logins)

    current_alerts_page = CurrentAlertsPage(driver)
    current_alerts_page.click_team_members_link()

    team_members_page = TeamMembersPage(driver)
    assert team_members_page.h1_is_team_members()
    team_members_page.click_invite_user()

    invited_user_email = (
        f"emergency-alerts-tests+fake-{timestamp}@digital.cabinet-office.gov.uk"
    )
    invite_user_page = InviteUserPage(driver)
    if user_requires_admin_approval:
        invite_user_page.check_create_broadcasts_checkbox()
    invite_user_page.send_invitation_to_email(invited_user_email)

    assert invite_user_page.is_page_title("Team members")

    if user_requires_admin_approval:
        invite_user_page.assert_text_is_on_page("An admin approval has been created")

        # Login again as a different platform admin to approve
        invite_user_page.sign_out()
        purge_failed_logins()  # To avoid throttle - email lookups trigger throttle logic
        # We do not need an elevated platform admin to approve admin actions
        sign_in(driver, account_type="platform_admin_2")

        # Approve/create it
        admin_approvals_page = AdminApprovalsPage(driver)
        admin_approvals_page.get(relative_url="/platform-admin/admin-actions")
        admin_approvals_page.approve_action()

        assert invite_user_page.text_is_on_page(
            "Sent invite to user " + invited_user_email
        )

    else:
        assert invite_user_page.text_is_on_page("Invite sent to " + invited_user_email)

    invite_user_page.sign_out()
    purge_failed_logins()  # To avoid throttle - email lookups trigger throttle logic

    # get user's invitation id from db using their email
    response = api_client.post(url="/user/invited", data={"email": invited_user_email})
    user_invitation_id = response["data"]["id"]

    # generate the same invitation url that is sent by email
    invitation_url = create_invitation_url(str(user_invitation_id))

    home_page = HomePage(driver)
    home_page.get(invitation_url)
    home_page.accept_cookie_warning()

    purge_failed_logins()  # To avoid throttle - email lookups trigger throttle logic

    registration_page = RegisterFromInvite(driver)
    assert registration_page.is_page_title("Create an account")
    registration_page.fill_registration_form(name="User " + timestamp)
    registration_page.click_continue_to_signin()
    time.sleep(1)
    # get user_id of invited user by their email
    response = api_client.post(url="/user/email", data={"email": invited_user_email})
    user_id = response["data"]["id"]
    code = get_verification_code_by_id(user_id)

    verify_page = VerifyPage(driver)
    verify_page.verify(code=code)

    base_page = BasePage(driver)
    # verify tour pages
    base_page.wait_until_url_ends_with("/broadcast-tour/live/1")
    base_page.click_element_by_link_text("Continue")
    base_page.wait_until_url_ends_with("/broadcast-tour/live/2")
    base_page.click_element_by_link_text("Continue")

    current_alerts_page = CurrentAlertsPage(driver)
    assert current_alerts_page.is_page_title("Current alerts")
    current_alerts_page.sign_out()

    # delete new user
    sign_in_elevated_platform_admin(driver, purge_failed_logins, False)

    current_alerts_page = CurrentAlertsPage(driver)
    current_alerts_page.click_team_members_link()

    team_members_page = TeamMembersPage(driver)
    assert team_members_page.h1_is_team_members()

    # click 'Change details' link associated with last invited user
    team_members_page.click_edit_team_member(invited_user_email)
    team_members_page.wait_for_element(TeamMembersPage.h1)

    # click link with text "Remove this team member"
    team_members_page.click_element_by_link_text("Remove this team member")
    team_members_page.click_yes_remove()

    team_members_page.wait_until_url_ends_with("/users")
    assert team_members_page.text_is_not_on_page(invited_user_email)

    team_members_page.sign_out()


@pytest.mark.xdist_group(name=test_group_name)
def test_service_admin_search_for_user_by_name_and_email(driver, purge_failed_logins):
    sign_in_elevated_platform_admin(driver, purge_failed_logins)

    current_alerts_page = CurrentAlertsPage(driver)
    # Due to the CSS of the tag component it ends up as uppercase
    current_alerts_page.click_element_by_link_text("Platform admin ELEVATED")

    admin_page = PlatformAdminPage(driver)

    # search for user by partial email
    admin_page.click_search_link()
    admin_page.search_for(text="emergency-alerts-tests+user3")
    assert admin_page.text_is_on_page("Functional Tests - Broadcast User Auth Test")

    # search for service by partial name
    admin_page.click_search_link()
    admin_page.search_for(text="Functional Tests")
    assert admin_page.text_is_on_page("Functional Tests Broadcast Service")

    admin_page.sign_out()


@pytest.mark.xdist_group(name=test_group_name)
def test_service_can_create_and_approve_and_revoke_api_keys(
    driver, purge_failed_logins
):
    sign_in_elevated_platform_admin(driver, purge_failed_logins)

    current_alerts_page = CurrentAlertsPage(driver)
    current_alerts_page.click_api_integration()

    api_keys_page = ApiKeysPage(driver)
    assert api_keys_page.is_page_title("API keys")

    # Create api key
    api_keys_page.click_element_by_link_text("Create an API key")
    assert api_keys_page.is_page_title("Create an API key")

    timestamp = str(int(time.time()))
    key_name = "Key-" + timestamp
    api_keys_page.create_key(key_name=key_name)
    api_keys_page.wait_until_url_ends_with("/keys")
    api_keys_page.assert_text_is_on_page("An admin approval has been created")

    # Login again as a different platform admin to approve
    # Approving does not need elevation
    api_keys_page.sign_out()
    sign_in(driver, account_type="platform_admin_2")

    # Approve/create it
    admin_approvals_page = AdminApprovalsPage(driver)
    admin_approvals_page.get(relative_url="/platform-admin/admin-actions")
    admin_approvals_page.approve_action()

    copy_key_btn = admin_approvals_page.wait_for_key_copy_button()
    # Key value gets normalized (no spaces, lowercase, etc)
    key_value = admin_approvals_page.get_key_name()
    assert key_value.startswith("key" + timestamp)

    # click "copy key"
    copy_key_btn.click()
    admin_approvals_page.wait_for_show_key_button()
    admin_approvals_page.assert_text_is_on_page("Copy your key to somewhere safe")
    admin_approvals_page.assert_text_is_on_page("Copied to clipboard")

    # revoke api key
    api_keys_page.click_element_by_link_text("Back to API keys")
    assert api_keys_page.is_page_title("API keys")
    api_keys_page.revoke_api_key(key_name=key_name)
    api_keys_page.wait_until_url_ends_with("/keys")
    api_keys_page.assert_text_is_on_page(f"‘{key_name}’ was revoked")

    # check audit trail for api key
    # We need to be an elevated admin to see the service history section
    api_keys_page.sign_out()
    sign_in_elevated_platform_admin(driver, purge_failed_logins, True)

    api_keys_page.click_element_by_link_text(
        "Settings", exact=True
    )  # non-exact matches cookie settings
    api_keys_page.click_element_by_link_text("Service history")
    api_keys_page.click_element_by_link_text("API keys")

    api_keys_page.assert_text_is_on_page(f"Created an API key called ‘{key_name}’")
    api_keys_page.assert_text_is_on_page(f"Revoked the ‘{key_name}’ API key")
