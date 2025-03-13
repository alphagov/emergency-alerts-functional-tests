import time

import pytest

from tests.pages import AddServicePage, CurrentAlertsPage, ServiceSettingsPage
from tests.pages.pages import (
    ApiKeysPage,
    BasePage,
    HomePage,
    InviteUserPage,
    PlatformAdminPage,
    RegisterFromInvite,
    TeamMembersPage,
    VerifyPage,
)
from tests.pages.rollups import sign_in
from tests.test_utils import create_invitation_url, get_verification_code_by_id

test_group_name = "platform-admin"


@pytest.mark.xdist_group(name=test_group_name)
def test_add_rename_and_delete_service(driver):
    timestamp = str(int(time.time()))
    service_name = f"Functional Test {timestamp}"

    sign_in(driver, account_type="platform_admin")

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
    time.sleep(10)
    assert service_settings_page.text_is_on_page(f"‘{new_service_name}’ was deleted")

    # sign out
    service_settings_page.get()
    service_settings_page.sign_out()


@pytest.mark.xdist_group(name=test_group_name)
def test_service_admin_can_invite_new_user_and_delete_user(driver, api_client):
    timestamp = str(int(time.time()))
    time.sleep(30)  # To avoid throttle

    sign_in(driver, account_type="platform_admin")

    current_alerts_page = CurrentAlertsPage(driver)
    current_alerts_page.click_team_members_link()

    team_members_page = TeamMembersPage(driver)
    assert team_members_page.h1_is_team_members()
    team_members_page.click_invite_user()

    invited_user_email = (
        f"emergency-alerts-tests+fake-{timestamp}@digital.cabinet-office.gov.uk"
    )
    invite_user_page = InviteUserPage(driver)
    invite_user_page.send_invitation_without_permissions(invited_user_email)
    assert invite_user_page.is_page_title("Team members")
    assert invite_user_page.text_is_on_page("Invite sent to " + invited_user_email)

    invite_user_page.sign_out()
    time.sleep(30)  # To avoid throttle

    # get user's invitation id from db using their email
    response = api_client.post(url="/user/invited", data={"email": invited_user_email})
    user_invitation_id = response["data"]["id"]

    # generate the same invitation url that is sent by email
    invitation_url = create_invitation_url(str(user_invitation_id))

    home_page = HomePage(driver)
    home_page.get(invitation_url)
    home_page.accept_cookie_warning()

    time.sleep(30)  # To avoid throttle

    registration_page = RegisterFromInvite(driver)
    assert registration_page.is_page_title("Create an account")
    registration_page.fill_registration_form(name="User " + timestamp)
    registration_page.click_continue_to_signin()
    time.sleep(30)
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
    sign_in(driver, account_type="platform_admin")

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
def test_service_admin_search_for_user_by_name_and_email(driver):
    time.sleep(20)
    sign_in(driver, account_type="platform_admin")

    current_alerts_page = CurrentAlertsPage(driver)
    current_alerts_page.click_element_by_link_text("Platform admin")

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
def test_service_can_create_revoke_and_audit_api_keys(driver):
    sign_in(driver, account_type="platform_admin")

    current_alerts_page = CurrentAlertsPage(driver)
    current_alerts_page.click_api_integration()

    api_keys_page = ApiKeysPage(driver)
    assert api_keys_page.is_page_title("API keys")

    # create api key
    api_keys_page.click_element_by_link_text("Create an API key")
    assert api_keys_page.is_page_title("Create an API key")

    timestamp = str(int(time.time()))
    key_name = "Key-" + timestamp
    api_keys_page.create_key(key_name=key_name)
    api_keys_page.wait_until_url_ends_with("/keys")
    assert api_keys_page.text_is_on_page("An admin approval has been created")

    api_keys_page.sign_out()
