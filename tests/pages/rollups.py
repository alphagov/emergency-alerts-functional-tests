from config import config
from tests.pages import (
    AdminApprovalsPage,
    BasePage,
    BroadcastDurationPage,
    BroadcastFreeformPage,
    CommonPageLocators,
    HomePage,
    PlatformAdminPage,
    SignInPage,
    wait_for_page_load_completion,
)
from tests.test_utils import (
    ACCOUNTS_REQUIRING_SMS_2FA,
    do_email_auth_verify,
    do_verify,
    do_verify_by_id,
    get_verification_code_by_id,
)


def sign_in(driver, account_type="normal"):
    clean_session(driver)

    home_page = HomePage(driver)
    home_page.get()
    home_page.accept_cookie_warning()

    _sign_in(driver, account_type)
    identifier = get_identifier(account_type=account_type)
    if account_type in ACCOUNTS_REQUIRING_SMS_2FA:
        do_verify_by_id(driver, identifier)
    else:
        do_verify(driver, identifier)

    base_page = BasePage(driver)
    if base_page.text_is_on_page_no_wait("temporarily become a platform admin"):
        # It's assumed this is expected by the calling test as part of the elevation process
        # (i.e. let that test handle where it wants to navigate to)
        pass
    elif base_page.text_is_not_on_page_no_wait("Current alerts"):
        if base_page.text_is_on_page_no_wait("Switch service"):
            with wait_for_page_load_completion(driver):
                base_page.click_element_by_link_text("Switch service")

        with wait_for_page_load_completion(driver):
            base_page.click_element_by_link_text(
                config["broadcast_service"]["service_name"]
            )


def sign_in_elevated_platform_admin(
    driver, purge_failed_logins, become_secondary_platform_admin=False
):
    # Platform admins must be elevated by another platform admin first, so this automates that process
    account_type = (
        "platform_admin_2" if become_secondary_platform_admin else "platform_admin"
    )
    opposite_account_type = (
        "platform_admin" if become_secondary_platform_admin else "platform_admin_2"
    )
    sign_in(driver, account_type=account_type)

    # Create the admin approval to elevate
    platform_admin_page = PlatformAdminPage(driver)
    platform_admin_page.get(relative_url="platform-admin")
    platform_admin_page.click_request_elevation_link()
    platform_admin_page.click_continue()
    platform_admin_page.wait_until_url_ends_with("admin-actions")

    platform_admin_page.sign_out()
    purge_failed_logins()  # To avoid throttle
    sign_in(driver, account_type=opposite_account_type)

    # Approve the elevation request
    admin_approvals_page = AdminApprovalsPage(driver)
    admin_approvals_page.get(relative_url="platform-admin/admin-actions")
    admin_approvals_page.approve_action()

    # Sign back in as the intended admin
    admin_approvals_page.sign_out()
    purge_failed_logins()  # To avoid throttle
    sign_in(driver, account_type=account_type)

    assert admin_approvals_page.text_is_on_page_no_wait(
        "approved to temporarily become a platform admin"
    )
    with wait_for_page_load_completion(driver):
        admin_approvals_page.click_continue()
    assert admin_approvals_page.text_is_on_page_no_wait("elevated")

    # This will take the browser to the platform admin page, but let's end up like a sign_in()
    admin_approvals_page.get(relative_url="accounts-or-dashboard")


def get_verify_code(account_identifier):
    identifier = get_identifier(account_type=account_identifier)
    return get_verification_code_by_id(identifier)


def clean_session(driver):
    page = BasePage(driver)
    if page.text_is_on_page_no_wait("Sign out"):
        page.sign_out()
    driver.delete_all_cookies()


def sign_in_email_auth(driver):
    _sign_in(driver, "email_auth")
    assert driver.current_url == config["eas_admin_url"] + "/two-factor-email-sent"
    do_email_auth_verify(driver)


def _sign_in(driver, account_type):
    sign_in_page = SignInPage(driver)
    sign_in_page.get()
    assert sign_in_page.is_current()
    email, password = get_email_and_password(account_type=account_type)
    sign_in_page.login(email, password)


def get_email_and_password(account_type):  # noqa: C901
    if account_type == "normal":
        return config["user"]["email"], config["user"]["password"]
    elif account_type == "seeded":
        return (
            config["service"]["seeded_user"]["email"],
            config["service"]["seeded_user"]["password"],
        )
    elif account_type == "email_auth":
        # has the same password as the seeded user
        return (
            config["service"]["email_auth_account"],
            config["service"]["seeded_user"]["password"],
        )
    elif account_type == "broadcast_create_user":
        return (
            config["broadcast_service"]["broadcast_user_1"]["email"],
            config["broadcast_service"]["broadcast_user_1"]["password"],
        )
    elif account_type == "broadcast_approve_user":
        return (
            config["broadcast_service"]["broadcast_user_2"]["email"],
            config["broadcast_service"]["broadcast_user_2"]["password"],
        )
    elif account_type == "platform_admin":
        return (
            config["broadcast_service"]["platform_admin"]["email"],
            config["broadcast_service"]["platform_admin"]["password"],
        )
    elif account_type == "platform_admin_2":
        return (
            config["broadcast_service"]["platform_admin_2"]["email"],
            config["broadcast_service"]["platform_admin_2"]["password"],
        )
    elif account_type == "session_timeout":
        return (
            config["broadcast_service"]["session_timeout"]["email"],
            config["broadcast_service"]["session_timeout"]["password"],
        )
    raise Exception("unknown account_type {}".format(account_type))


def get_identifier(account_type):  # noqa: C901
    if account_type == "broadcast_approve_user":
        return config["broadcast_service"]["broadcast_user_2"]["id"]
    elif account_type == "broadcast_auth_test_user":
        return config["broadcast_service"]["broadcast_user_3"]["id"]
    elif account_type == "broadcast_create_user":
        return config["broadcast_service"]["broadcast_user_1"]["id"]
    elif account_type in ["normal", "email_auth"]:
        return config["user"]["mobile"]
    elif account_type == "platform_admin":
        return config["broadcast_service"]["platform_admin"]["id"]
    elif account_type == "platform_admin_2":
        return config["broadcast_service"]["platform_admin_2"]["id"]
    elif account_type == "seeded":
        return config["service"]["seeded_user"]["mobile"]
    elif account_type == "session_timeout":
        return config["broadcast_service"]["session_timeout"]["mobile"]
    raise Exception("unknown account_type {}".format(account_type))


def create_alert(driver, id):
    sign_in(driver, account_type="broadcast_create_user")

    # prepare alert
    current_alerts_page = BasePage(driver)
    broadcast_title = "test broadcast " + id

    current_alerts_page.click_element_by_link_text("Create new alert")

    new_alert_page = BasePage(driver)
    new_alert_page.select_checkbox_or_radio(value="freeform")
    new_alert_page.click_continue()

    broadcast_freeform_page = BroadcastFreeformPage(driver)
    broadcast_content = "This is a test broadcast " + id
    broadcast_freeform_page.create_broadcast_content(broadcast_title, broadcast_content)
    broadcast_freeform_page.click_continue()

    # Choosing not to add extra_content
    choose_extra_content_page = BasePage(driver)
    choose_extra_content_page.select_checkbox_or_radio(value="no")
    choose_extra_content_page.click_continue()

    prepare_alert_pages = BasePage(driver)
    prepare_alert_pages.click_element_by_link_text("Countries")
    prepare_alert_pages.select_checkbox_or_radio(value="ctry19-E92000001")  # England
    prepare_alert_pages.click_continue()
    prepare_alert_pages.click_element_by_link_text("Save and continue")

    broadcast_duration_page = BroadcastDurationPage(driver)
    broadcast_duration_page.set_alert_duration(hours="8", minutes="30")
    broadcast_duration_page.click_preview()  # Preview alert

    preview_alert_page = BasePage(driver)
    assert preview_alert_page.text_is_on_page("England")
    assert preview_alert_page.text_is_on_page("8 hours, 30 minutes")

    preview_alert_page.click_submit_for_approval()
    assert preview_alert_page.text_is_on_page(
        f"{broadcast_title} is waiting for approval"
    )

    preview_alert_page.sign_out()


def approve_alert(driver, id):
    sign_in(driver, account_type="broadcast_approve_user")

    current_alerts_page = BasePage(driver)
    current_alerts_page.click_element_by_link_text("test broadcast " + id)
    current_alerts_page.select_checkbox_or_radio(value="y")  # confirm approve alert
    current_alerts_page.click_submit()
    current_alerts_page.wait_for_element(CommonPageLocators.LIVE_BROADCAST)
    assert current_alerts_page.text_is_on_page("since today at")

    current_alerts_page.sign_out()


def broadcast_alert(driver, id):
    create_alert(driver, id)
    approve_alert(driver, id)


def cancel_alert(driver, id):
    sign_in(driver, account_type="broadcast_approve_user")

    current_alerts_page = BasePage(driver)
    current_alerts_page.click_element_by_link_text("test broadcast " + id)
    current_alerts_page.click_element_by_link_text("Stop sending")
    current_alerts_page.click_submit()  # stop broadcasting

    current_alerts_page.sign_out()
