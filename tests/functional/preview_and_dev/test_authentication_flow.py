import pytest

from tests.pages import ForgotPasswordPage, SignInPage
from tests.pages.rollups import clean_session

TESTSUITE_CODE = "AUTH-FLOW"


@pytest.mark.xdist_group(name=TESTSUITE_CODE)
def test_reset_forgotten_password(driver):
    clean_session(driver)

    sign_in_page = SignInPage(driver)
    sign_in_page.click_forgot_password_link()

    forgot_password_page = ForgotPasswordPage(driver)
    forgot_password_page.input_email_address("tbd@gov.uk")
    forgot_password_page.click_continue()

    assert forgot_password_page.is_text_present_on_page("Check your email")
