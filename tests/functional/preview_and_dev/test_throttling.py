import pytest

from tests.pages.rollups import clean_session

test_group_name = "throttling"


@pytest.mark.xdist_group(name=test_group_name)
def test_expected_failure(driver, failed_login_purge):
    clean_session(driver)
    assert 2 == 1


# @recordtime
# @pytest.mark.xdist_group(name=test_group_name)
# def test_login_attempt_throttled_after_failed_login(driver, failed_login_purge):
#     clean_session(driver)

#     login_email = config["broadcast_service"]["throttled_user"]["email"]
#     login_pw = "incorrect password"

#     sign_in_page = SignInPage(driver)
#     sign_in_page.get()
#     assert sign_in_page.is_current()
#     sign_in_page.login(login_email, login_pw)

#     # Assert here that error text appears
#     assert sign_in_page.is_text_present_on_page(
#         "The email address or password you entered is incorrect."
#     )

#     # Attempts again
#     login_email = config["broadcast_service"]["throttled_user"]["email"]
#     login_pw = config["broadcast_service"]["throttled_user"]["password"]

#     sign_in_page = SignInPage(driver)
#     sign_in_page.get()
#     assert sign_in_page.is_current()
#     sign_in_page.login(login_email, login_pw)

#     throttled_page = ThrottledPage(driver)
#     assert throttled_page.check_page_for_text_with_retry("Too many requests")
#     assert throttled_page.check_page_for_text_with_retry(
#         "You've been temporarily throttled due to too many login attempts."
#     )

#     # Waits some time to avoid throttle
#     time.sleep(30)

#     # Attempts again
#     throttled_page.click_element_by_link_text("Sign in")

#     login_email = config["broadcast_service"]["throttled_user"]["email"]
#     login_pw = config["broadcast_service"]["throttled_user"]["password"]

#     sign_in_page = SignInPage(driver)
#     sign_in_page.get()
#     assert sign_in_page.is_current()
#     sign_in_page.login(login_email, login_pw)

#     # Successful login renders MFA page

#     assert sign_in_page.check_page_for_text_with_retry(
#         "text message with a security code"
#     )

#     sign_in_url = create_sign_in_url(login_email, "email-auth")

#     landing_page = BasePage(driver)
#     landing_page.get(sign_in_url)

#     landing_page.url_contains("current-alerts")
