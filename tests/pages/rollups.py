from config import config
from tests.pages import (
    BasePage,
    BroadcastDurationPage,
    BroadcastFreeformPage,
    CommonPageLocators,
    HomePage,
    SignInPage,
)
from tests.test_utils import (
    ACCOUNTS_REQUIRING_SMS_2FA,
    do_email_auth_verify,
    do_verify,
    do_verify_by_id,
    get_verification_code_by_id,
    go_to_service_dashboard,
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

    go_to_service_dashboard(driver, "broadcast_service")


def get_verify_code(account_identifier):
    identifier = get_identifier(account_type=account_identifier)
    return get_verification_code_by_id(identifier)


def clean_session(driver):
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


def get_email_and_password(account_type):
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
    elif account_type == "session_timeout":
        return (
            config["broadcast_service"]["session_timeout"]["email"],
            config["broadcast_service"]["session_timeout"]["password"],
        )
    raise Exception("unknown account_type {}".format(account_type))


def get_identifier(account_type):
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
    elif account_type == "seeded":
        return config["service"]["seeded_user"]["mobile"]
    elif account_type == "session_timeout":
        return config["broadcast_service"]["session_timeout"]["mobile"]
    raise Exception("unknown account_type {}".format(account_type))


def create_alert(driver, id):
    sign_in(driver, account_type="broadcast_create_user")

    # prepare alert
    current_alerts_page = BasePage(driver)
    broadcast_title = "test broadcast" + id

    current_alerts_page.click_element_by_link_text("Create new alert")

    new_alert_page = BasePage(driver)
    new_alert_page.select_checkbox_or_radio(value="freeform")
    new_alert_page.click_continue()

    broadcast_freeform_page = BroadcastFreeformPage(driver)
    broadcast_content = "This is a test broadcast " + id
    broadcast_freeform_page.create_broadcast_content(broadcast_title, broadcast_content)
    broadcast_freeform_page.click_continue()

    prepare_alert_pages = BasePage(driver)
    prepare_alert_pages.click_element_by_link_text("Countries")
    prepare_alert_pages.select_checkbox_or_radio(value="ctry19-E92000001")  # England
    prepare_alert_pages.click_continue()
    prepare_alert_pages.click_element_by_link_text("Continue")

    broadcast_duration_page = BroadcastDurationPage(driver)
    broadcast_duration_page.click_change_duration()
    broadcast_duration_page.set_alert_duration(hours="8", minutes="30")
    broadcast_duration_page.click_continue()  # Preview alert

    preview_alert_page = BasePage(driver)
    preview_alert_page.click_element_by_link_text("Preview alert")
    assert preview_alert_page.text_is_on_page("England")
    assert preview_alert_page.text_is_on_page("8 hours, 30 minutes")

    preview_alert_page.click_continue()
    assert preview_alert_page.text_is_on_page(
        f"{broadcast_title} is waiting for approval"
    )

    preview_alert_page.sign_out()


def approve_alert(driver, id):
    sign_in(driver, account_type="broadcast_approve_user")

    current_alerts_page = BasePage(driver)
    current_alerts_page.click_element_by_link_text("test broadcast" + id)
    current_alerts_page.select_checkbox_or_radio(value="y")  # confirm approve alert
    current_alerts_page.click_continue()
    current_alerts_page.wait_for_element(CommonPageLocators.LIVE_BROADCAST)
    assert current_alerts_page.text_is_on_page("since today at")


def broadcast_alert(driver, id):
    create_alert(driver, id)
    approve_alert(driver, id)


def cancel_alert(driver, id):
    sign_in(driver, account_type="broadcast_approve_user")

    current_alerts_page = BasePage(driver)
    current_alerts_page.click_element_by_link_text("test broadcast" + id)
    current_alerts_page.click_element_by_link_text("Stop sending")
    current_alerts_page.click_continue()  # stop broadcasting

    current_alerts_page.sign_out()
