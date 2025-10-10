import random
import string

import pytest

from config import config
from tests.pages import (
    BasePage,
    ForgotPasswordPage,
    HomePage,
    NewPasswordPage,
    SignInPage,
    VerifyPage,
)
from tests.pages.rollups import clean_session
from tests.test_utils import (  # get_verify_code_from_api_by_id,
    create_sign_in_url,
    do_verify_by_id,
)

test_group_name = "auth-flow"


@pytest.mark.xdist_group(name=test_group_name)
def test_reset_forgotten_password(driver, purge_failed_logins):
    clean_session(driver)

    home_page = HomePage(driver)
    home_page.get()
    home_page.accept_cookie_warning()

    login_email = config["broadcast_service"]["broadcast_user_3"]["email"]

    sign_in_page = SignInPage(driver)
    sign_in_page.get()
    sign_in_page.click_forgot_password_link()

    forgot_password_page = ForgotPasswordPage(driver)
    forgot_password_page.input_email_address(login_email)
    forgot_password_page.click_submit()
    assert forgot_password_page.text_is_on_page("Check your email")

    password_reset_url = create_sign_in_url(login_email, "new-password")
    new_password_page = NewPasswordPage(driver, password_reset_url)
    assert new_password_page.text_is_on_page("create a new password")

    new_password = "".join(
        [
            random.choice(string.ascii_letters + string.digits + string.punctuation)
            for _ in range(15)
        ]
    )
    new_password_page.input_new_password(new_password)
    purge_failed_logins()
    new_password_page.click_continue_to_signin()

    # verify_code = get_verify_code_from_api_by_id(
    #     config["broadcast_service"]["broadcast_user_3"]["id"]
    # )
    # verify_page = VerifyPage(driver)
    # verify_page.verify(verify_code)

    do_verify_by_id(driver, config["broadcast_service"]["broadcast_user_3"]["id"])

    from datetime import datetime
    from pathlib import Path

    print("URL on verify_page:", driver.current_url)
    filename_datetime = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    filename = str(
        Path.cwd()
        / "screenshots"
        / "{}_{}.png".format(filename_datetime, "verify_page")
    )
    driver.save_screenshot(str(filename))

    # verify_page.wait_until_url_ends_with("/sign-in?reset_password=True")

    # print("URL on verify_page:", driver.current_url)
    # filename_datetime = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    # filename = str(
    #     Path.cwd()
    #     / "screenshots"
    #     / "{}_{}.png".format(filename_datetime, "sign_in_page")
    # )
    # driver.save_screenshot(str(filename))

    # assert verify_page.text_is_on_page(
    #     "You’ve just changed your password. Sign in with your new password."
    # )

    # # Redirects to sign in page so user must sign in again after verifying password reset
    # assert password_reset_sign_in_page.text_is_on_page(
    #     "You've just changed your password. Sign in with your new password."
    # )

    # password_reset_sign_in_page = SignInPage(driver)
    # password_reset_sign_in_page.login(login_email, new_password)

    verify_page = VerifyPage(driver)  # added

    verify_page.login(login_email, new_password)

    # verify_code = get_verify_code_from_api_by_id(
    #     config["broadcast_service"]["broadcast_user_3"]["id"]
    # )
    # verify_page = VerifyPage(driver)
    # verify_page.verify(verify_code)

    do_verify_by_id(driver, config["broadcast_service"]["broadcast_user_3"]["id"])

    landing_page = BasePage(driver)
    assert landing_page.url_contains("current-alerts")


@pytest.mark.xdist_group(name=test_group_name)
def test_sign_in_with_email_mfa(driver, purge_failed_logins):
    clean_session(driver)

    home_page = HomePage(driver)
    home_page.get()
    home_page.accept_cookie_warning()

    login_email = config["broadcast_service"]["broadcast_user_4"]["email"]
    login_pw = config["broadcast_service"]["broadcast_user_4"]["password"]

    purge_failed_logins()
    sign_in_page = SignInPage(driver)
    sign_in_page.get()
    assert sign_in_page.is_current()
    sign_in_page.login(login_email, login_pw)

    sign_in_page.wait_until_url_ends_with("/two-factor-email-sent")
    assert sign_in_page.text_is_on_page("a link to sign in")

    purge_failed_logins()
    sign_in_url = create_sign_in_url(login_email, "email-auth")

    landing_page = BasePage(driver)
    landing_page.get(sign_in_url)

    landing_page.url_contains("current-alerts")
