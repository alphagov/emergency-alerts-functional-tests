from config import config
from tests.pages import SignInPage
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
