from tests.pages.locators import (
    AddServicePageLocators,
    ApiKeysPageLocators,
    CommonPageLocators,
    DashboardWithDialogPageLocators,
    DurationPageLocators,
    EditTemplatePageLocators,
    ExtraContentPageLocators,
    NewPasswordPageLocators,
    PlatformAdminPageLocators,
    RejectionFormLocators,
    ReturnForEditFormLocators,
    SearchCoordinatePageLocators,
    SearchPostcodePageLocators,
    SignUpPageLocators,
    SupportPageLocators,
    VerifyPageLocators,
)
from tests.playwright_adapter import By, WebDriverWait


class BasePageElement(object):
    def __init__(self, name=None):
        if name:
            self.name = name

    def __set__(self, obj, value):
        driver = obj.driver
        WebDriverWait(driver, 100).until(
            lambda driver: driver.find_element((By.NAME, self.name))
        )
        driver.find_element((By.NAME, self.name)).send_keys(value)

    def __get__(self, obj, owner):
        driver = obj.driver
        WebDriverWait(driver, 100).until(
            lambda driver: driver.find_element((By.NAME, self.name))
        )
        element = driver.find_element((By.NAME, self.name))
        return element.get_attribute("value")


class ClearableInputElement(BasePageElement):
    def __init__(self, name=None):
        if name:
            self.name = name

    def __set__(self, obj, value, clear=True):
        driver = obj.driver
        WebDriverWait(driver, 100).until(
            lambda driver: driver.find_element((By.NAME, self.name))
        )
        input = driver.find_element((By.NAME, self.name))
        input.clear()
        input.send_keys(value)


class ServiceInputElement(BasePageElement):
    name = AddServicePageLocators.SERVICE_INPUT[1]


class ServiceOrgTypeElement(BasePageElement):
    name = AddServicePageLocators.ORG_TYPE_INPUT[1]


class EmailInputElement(BasePageElement):
    name = CommonPageLocators.EMAIL_INPUT[1]


class NewPasswordInputElement(BasePageElement):
    name = NewPasswordPageLocators.NEW_PASSWORD_INPUT[1]


class PasswordInputElement(BasePageElement):
    name = CommonPageLocators.PASSWORD_INPUT[1]


class SmsInputElement(BasePageElement):
    name = VerifyPageLocators.SMS_INPUT[1]


class NameInputElement(ClearableInputElement):
    name = CommonPageLocators.NAME_INPUT[1]


class ReferenceInputElement(ClearableInputElement):
    name = CommonPageLocators.REFERENCE_INPUT[1]


class FolderNameInputElement(ClearableInputElement):
    name = CommonPageLocators.FOLDER_NAME_INPUT[1]


class HoursInputElement(ClearableInputElement):
    name = DurationPageLocators.HOURS_INPUT[1]


class MinutesInputElement(ClearableInputElement):
    name = DurationPageLocators.MINUTES_INPUT[1]


class MobileInputElement(BasePageElement):
    name = SignUpPageLocators.MOBILE_INPUT[1]


class TemplateContentElement(BasePageElement):
    name = EditTemplatePageLocators.TEMPLATE_CONTENT_INPUT[1]


class ExtraContentElement(BasePageElement):
    name = ExtraContentPageLocators.EXTRA_CONTENT_INPUT[1]


class SubjectInputElement(BasePageElement):
    name = EditTemplatePageLocators.TEMPLATE_SUBJECT_INPUT[1]


class FeedbackTextAreaElement(BasePageElement):
    name = SupportPageLocators.FEEDBACK_TEXTAREA[1]


class PostcodeInputElement(BasePageElement):
    name = SearchPostcodePageLocators.POSTCODE_TEXTAREA[1]


class RadiusInputElement(BasePageElement):
    name = SearchPostcodePageLocators.RADIUS_TEXTAREA[1]


class SearchButton(BasePageElement):
    name = SearchPostcodePageLocators.SEARCH_BUTTON[1]


class PreviewButton(BasePageElement):
    name = SearchPostcodePageLocators.PREVIEW_BUTTON[1]


class SearchInputElement(BasePageElement):
    name = PlatformAdminPageLocators.SEARCH_INPUT[1]


class KeyNameInputElement(BasePageElement):
    name = ApiKeysPageLocators.KEY_NAME_INPUT[1]


class FirstCoordinateInputElement(BasePageElement):
    name = SearchCoordinatePageLocators.FIRST_COORDINATE_TEXTAREA[1]


class SecondCoordinateInputElement(BasePageElement):
    name = SearchCoordinatePageLocators.SECOND_COORDINATE_TEXTAREA[1]


class CoordinateRadiusInputElement(BasePageElement):
    name = SearchCoordinatePageLocators.RADIUS_TEXTAREA[1]


class CoordinateSearchButton(BasePageElement):
    name = SearchCoordinatePageLocators.SEARCH_BUTTON[1]


class CoordinatePreviewButton(BasePageElement):
    name = SearchCoordinatePageLocators.PREVIEW_BUTTON[1]


class InactivityDialogStaySignedInButton(BasePageElement):
    name = DashboardWithDialogPageLocators.STAY_SIGNED_IN_BUTTON[1]


class DialogSignOutButton(BasePageElement):
    name = DashboardWithDialogPageLocators.SIGN_OUT_BUTTON[1]


class InactivityDialog(BasePageElement):
    name = DashboardWithDialogPageLocators.INACTIVITY_DIALOG[1]


class ExpiryDialog(BasePageElement):
    name = DashboardWithDialogPageLocators.EXPIRY_DIALOG[1]


class ExpiryDialogContinueButton(BasePageElement):
    name = DashboardWithDialogPageLocators.CONTINUE_BUTTON[1]


class RejectionDetailElement(BasePageElement):
    name = RejectionFormLocators.REJECTION_DETAIL_ELEMENT[1]


class RejectionReasonTextArea(BasePageElement):
    name = RejectionFormLocators.REJECTION_REASON_TEXTAREA[1]


class RejectAlertButton(BasePageElement):
    name = RejectionFormLocators.REJECT_ALERT_BUTTON[1]


class RejectionDetailLink:
    name = RejectionFormLocators.REJECTION_DETAIL_LINK[1]


class ReturnForEditReasonTextArea(BasePageElement):
    name = ReturnForEditFormLocators.RETURN_FOR_EDIT_REASON_TEXTAREA[1]
