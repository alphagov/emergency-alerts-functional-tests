import pytest

from tests.pages import BasePage, SupportFeedbackPage
from tests.pages.rollups import get_email_and_password, sign_in

TESTSUITE_CODE = "TOP-RAIL"


# @pytest.mark.xdist_group(name=TESTSUITE_CODE)
# def test_report_a_problem(driver):
#     sign_in(driver, account_type="broadcast_create_user")

#     landing_page = BasePage(driver)
#     landing_page.click_element_by_link_text("Support")
#     assert landing_page.is_text_present_on_page("24-hour online support")

#     landing_page.select_checkbox_or_radio(value="report-problem")
#     landing_page.click_continue()

#     report_problem_page = SupportFeedbackPage(driver)
#     assert report_problem_page.is_page_title("Report a problem")
#     report_problem_page.fill_textarea(
#         "Problem description submitted by a functional test"
#     )

#     email, _ = get_email_and_password(account_type="broadcast_create_user")
#     assert report_problem_page.is_text_present_on_page(f"reply to {email}")

#     report_problem_page.click_continue()

#     landing_page.get()
#     assert landing_page.url_contains("thanks")
#     assert landing_page.is_page_title("Thanks for contacting us")

#     landing_page.sign_out()


@pytest.mark.xdist_group(name=TESTSUITE_CODE)
def test_question_or_feedback(driver):
    sign_in(driver, account_type="broadcast_create_user")

    landing_page = BasePage(driver)
    landing_page.click_element_by_link_text("Support")
    assert landing_page.is_text_present_on_page("24-hour online support")

    landing_page.select_checkbox_or_radio(value="ask-question-give-feedback")
    landing_page.click_continue()

    feedback_page = SupportFeedbackPage(driver)
    assert feedback_page.is_page_title("Ask a question or give feedback")
    feedback_page.fill_textarea("Feedback submitted by a functional test")

    email, _ = get_email_and_password(account_type="broadcast_create_user")
    assert feedback_page.is_text_present_on_page(f"reply to {email}")

    feedback_page.click_continue()

    landing_page.get()
    assert landing_page.url_contains("thanks")
    assert landing_page.is_page_title("Thanks for contacting us")

    landing_page.sign_out()
