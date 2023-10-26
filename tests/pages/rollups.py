from config import config
from tests.pages import (
    BasePage,
    BroadcastFreeformPage,
    DashboardPage,
    SignInPage,
)
from tests.test_utils import do_email_auth_verify, do_verify, do_verify_by_id


def sign_in(driver, account_type="normal"):
    clean_session(driver)

    _sign_in(driver, account_type)
    identifier = get_identifier(account_type=account_type)
    if account_type.startswith("broadcast"):
        do_verify_by_id(driver, identifier)
    else:
        do_verify(driver, identifier)


def clean_session(driver):
    driver.delete_all_cookies()


def sign_in_email_auth(driver):
    _sign_in(driver, "email_auth")
    assert driver.current_url == config["notify_admin_url"] + "/two-factor-email-sent"
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
    raise Exception("unknown account_type {}".format(account_type))


def get_identifier(account_type):
    if account_type == "normal":
        return config["user"]["mobile"]
    elif account_type == "seeded":
        return config["service"]["seeded_user"]["mobile"]
    elif account_type == "email_auth":
        return config["user"]["mobile"]
    elif account_type == "broadcast_create_user":
        return config["broadcast_service"]["broadcast_user_1"]["id"]
    elif account_type == "broadcast_approve_user":
        return config["broadcast_service"]["broadcast_user_2"]["id"]
    raise Exception("unknown account_type {}".format(account_type))


def create_alert(driver, id):
    sign_in(driver, account_type="broadcast_create_user")

    landing_page = BasePage(driver)
    if not landing_page.is_text_present_on_page("Current alerts"):
        landing_page.click_element_by_link_text("Switch service")
        choose_service_page = BasePage(driver)
        choose_service_page.click_element_by_link_text(
            "Functional Tests Broadcast Service"
        )
    else:
        dashboard_page = DashboardPage(driver)
        dashboard_page.click_element_by_link_text("Current alerts")

    # prepare alert
    current_alerts_page = BasePage(driver)
    broadcast_title = "test broadcast" + id

    current_alerts_page.click_element_by_link_text("New alert")

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

    prepare_alert_pages.click_element_by_link_text("Preview this alert")
    assert prepare_alert_pages.is_text_present_on_page("England")

    prepare_alert_pages.click_continue()
    assert prepare_alert_pages.is_text_present_on_page(
        f"{broadcast_title} is waiting for approval"
    )

    prepare_alert_pages.sign_out()


def approve_alert(driver, id):
    sign_in(driver, account_type="broadcast_approve_user")

    landing_page = BasePage(driver)
    if not landing_page.is_text_present_on_page("Current alerts"):
        landing_page.click_element_by_link_text("Switch service")
        choose_service_page = BasePage(driver)
        choose_service_page.click_element_by_link_text(
            "Functional Tests Broadcast Service"
        )
    else:
        dashboard_page = DashboardPage(driver)
        dashboard_page.click_element_by_link_text("Current alerts")

    current_alerts_page = BasePage(driver)
    current_alerts_page.click_element_by_link_text("test broadcast" + id)
    current_alerts_page.select_checkbox_or_radio(value="y")  # confirm approve alert
    current_alerts_page.click_continue()
    assert current_alerts_page.is_text_present_on_page("since today at")


def cancel_alert(driver, id):
    sign_in(driver, account_type="broadcast_approve_user")

    landing_page = BasePage(driver)
    if not landing_page.is_text_present_on_page("Current alerts"):
        landing_page.click_element_by_link_text("Switch service")
        choose_service_page = BasePage(driver)
        choose_service_page.click_element_by_link_text(
            "Functional Tests Broadcast Service"
        )
    else:
        dashboard_page = DashboardPage(driver)
        dashboard_page.click_element_by_link_text("Current alerts")

    current_alerts_page = BasePage(driver)
    current_alerts_page.click_element_by_link_text("test broadcast" + id)
    current_alerts_page.click_element_by_link_text("Stop sending")
    current_alerts_page.click_continue()  # stop broadcasting

    current_alerts_page.sign_out()
