from time import sleep

from retry import retry
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import config
from tests.pages.element import (
    BasePageElement,
    ChangeDurationLink,
    ClearableInputElement,
    CoordinatePreviewButton,
    CoordinateRadiusInputElement,
    CoordinateSearchButton,
    DialogSignOutButton,
    EmailInputElement,
    ExpiryDialog,
    ExpiryDialogContinueButton,
    FeedbackTextAreaElement,
    FirstCoordinateInputElement,
    HoursInputElement,
    InactivityDialog,
    InactivityDialogStaySignedInButton,
    KeyNameInputElement,
    MinutesInputElement,
    MobileInputElement,
    NameInputElement,
    NewPasswordInputElement,
    PasswordInputElement,
    PostcodeInputElement,
    PreviewButton,
    RadiusInputElement,
    RejectAlertButton,
    RejectionDetailElement,
    RejectionDetailLink,
    RejectionReasonTextArea,
    SearchButton,
    SearchInputElement,
    SecondCoordinateInputElement,
    ServiceInputElement,
    SmsInputElement,
    SubjectInputElement,
    TemplateContentElement,
)
from tests.pages.locators import (
    AddServicePageLocators,
    ApiIntegrationPageLocators,
    ApiKeysPageLocators,
    ChangeNameLocators,
    CommonPageLocators,
    DashboardWithDialogPageLocators,
    DurationPageLocators,
    EditTemplatePageLocators,
    InviteUserPageLocators,
    MainPageLocators,
    NavigationLocators,
    RejectionFormLocators,
    SearchCoordinatePageLocators,
    SearchPostcodePageLocators,
    ServiceSettingsLocators,
    SignInPageLocators,
    TeamMembersPageLocators,
    TemplatePageLocators,
    VerifyPageLocators,
    ViewTemplatePageLocators,
)


class RetryException(Exception):
    pass


class AntiStale:
    def __init__(self, driver, locator, webdriverwait_func):
        """
        webdriverwait_func is a function that takes in a locator and returns an element. Probably a webdriverwait.
        """
        self.driver = driver
        self.webdriverwait_func = webdriverwait_func
        self.locator = locator
        # kick it off
        self.element = self.webdriverwait_func(self.locator)

    @retry(RetryException, tries=5)
    def retry_on_stale(self, callable):
        try:
            return callable()
        except StaleElementReferenceException:
            self.reset_element()

    def reset_element(self):
        self.element = self.webdriverwait_func(self.locator)

        raise RetryException("StaleElement {}".format(self.locator))


class AntiStaleElement(AntiStale):
    def click(self):
        def _click():
            # an element might be hidden underneath other elements (eg sticky nav items). To counter this, we can use
            # the scrollIntoView function to bring it to the top of the page
            self.driver.execute_script(
                "arguments[0].scrollIntoViewIfNeeded()", self.element
            )
            try:
                self.element.click()
            except WebDriverException:
                self.driver.execute_script(
                    "arguments[0].scrollIntoView()", self.element
                )
                self.element.click()

        return self.retry_on_stale(_click)

    def __getattr__(self, attr):
        return self.retry_on_stale(lambda: getattr(self.element, attr))


class AntiStaleElementList(AntiStale):
    def __getitem__(self, index):
        class AntiStaleListItem:
            def click(item_self):
                return self.retry_on_stale(lambda: self.element[index].click())

            def __getattr__(item_self, attr):
                return self.retry_on_stale(lambda: getattr(self.element[index], attr))

        return AntiStaleListItem()

    def __len__(self):
        return len(self.element)


class BasePage(object):
    sign_out_link = NavigationLocators.SIGN_OUT_LINK

    def __init__(self, driver):
        self.base_url = config["eas_admin_url"]
        self.driver = driver

    def get(self, url=None, relative_url=None):
        if url:
            self.driver.get(url)
        elif relative_url:
            self.driver.get(f"{self.base_url}/{relative_url}")
        else:
            self.driver.get(self.base_url)

    @property
    def current_url(self):
        return self.driver.current_url

    def wait_for_invisible_element(self, locator):
        return AntiStaleElement(
            self.driver,
            locator,
            lambda locator: WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(locator)
            ),
        )

    def wait_for_element(self, locator, time=10):
        return AntiStaleElement(
            self.driver,
            locator,
            lambda locator: WebDriverWait(self.driver, time).until(
                EC.visibility_of_element_located(locator),
                EC.presence_of_element_located(locator),
            ),
        )

    def wait_for_elements(self, locator):
        return AntiStaleElementList(
            self.driver,
            locator,
            lambda locator: WebDriverWait(self.driver, 10).until(
                EC.visibility_of_all_elements_located(locator),
                EC.presence_of_all_elements_located(locator),
            ),
        )

    def sign_out(self):
        element = self.wait_for_element(BasePage.sign_out_link)
        element.click()
        self.driver.delete_all_cookies()

    def wait_until_url_is(self, url):
        return WebDriverWait(self.driver, 10).until(self.url_contains(url))

    def wait_until_url_ends_with(self, url):
        return WebDriverWait(self.driver, 10).until(self.url_ends_with(url))

    def url_contains(self, url):
        def check_contains_url(driver):
            return url in self.driver.current_url

        return check_contains_url

    def url_ends_with(self, url):
        def check_ends_with(driver):
            return self.driver.current_url.endswith(url)

        return check_ends_with

    def select_checkbox_or_radio(self, element=None, value=None):
        if not element and value:
            locator = (By.CSS_SELECTOR, f"[value={value}]")
            element = self.wait_for_invisible_element(locator)
        if not element.get_attribute("checked"):
            element.click()
            assert element.get_attribute("checked")

    def unselect_checkbox(self, element):
        if element.get_attribute("checked"):
            element.click()
            assert not element.get_attribute("checked")

    def click_templates(self):
        element = self.wait_for_element(NavigationLocators.TEMPLATES_LINK)
        element.click()

    def click_settings(self):
        element = self.wait_for_element(NavigationLocators.SETTINGS_LINK)
        element.click()

    def click_save(self, time=10):
        element = self.wait_for_element(CommonPageLocators.CONTINUE_BUTTON, time=time)
        element.click()

    def click_continue(self):
        element = self.wait_for_element(CommonPageLocators.CONTINUE_BUTTON)
        element.click()

    def click_continue_to_signin(self):
        element = self.wait_for_element(CommonPageLocators.CONTINUE_SIGNIN_BUTTON)
        element.click()

    def click_continue_to_submit(self):
        element = self.wait_for_element(CommonPageLocators.CONTINUE_SIGNIN_BUTTON)
        element.click()

    def is_page_title(self, expected_page_title):
        element = self.wait_for_element(CommonPageLocators.H1)
        return element.text == expected_page_title

    @retry(
        RetryException,
        tries=config["ui_element_retry_times"],
        delay=config["ui_element_retry_interval"],
    )
    def text_is_on_page(self, search_text):
        normalized_page_source = " ".join(self.driver.page_source.split())
        if search_text not in normalized_page_source:
            self.driver.refresh()
            raise RetryException(f'Could not find text "{search_text}"')
        return True

    def text_is_not_on_page(self, search_text):
        normalized_page_source = " ".join(self.driver.page_source.split())
        tries = 0
        while tries < 3:
            if search_text in normalized_page_source:
                return False
            tries += 1
            self.driver.refresh()
            sleep(1)
        return True

    def get_template_id(self):
        # e.g.
        # http://localhost:6012/services/237dd966-b092-42ab-b406-0a00187d007f/templates/4808eb34-5225-492b-8af2-14b232f05b8e/edit
        # circle back and do better
        return self.driver.current_url.split("/templates/")[1].split("/")[0]

    def click_element_by_link_text(self, link_text):
        element = self.wait_for_element((By.LINK_TEXT, link_text))
        element.click()

    def click_element_by_id(self, id):
        element = self.wait_for_element((By.CSS_SELECTOR, f"#{id}"))
        element.click()

    def get_errors(self):
        error_message = (By.CSS_SELECTOR, ".banner-dangerous")
        errors = self.wait_for_element(error_message)
        return errors.text.strip()


class PageWithStickyNavMixin:
    def scrollToRevealElement(self, selector=None, xpath=None, stuckToBottom=True):
        namespace = "window.GOVUK.stickAtBottomWhenScrolling"
        if stuckToBottom is False:
            namespace = "window.GOVUK.stickAtTopWhenScrolling"

        if selector is not None:
            js_str = (
                f"if ('scrollToRevealElement' in {namespace})"
                f"{namespace}.scrollToRevealElement($('{selector}').eq(0))"
            )
            self.driver.execute_script(js_str)
        elif xpath is not None:
            js_str = f"""(function (document) {{
                             if ('scrollToRevealElement' in {namespace}) {{
                                 var matches = document.evaluate("{xpath}", document, null, XPathResult.ANY_TYPE, null);
                                 if (matches) {{
                                     {namespace}.scrollToRevealElement($(matches.iterateNext()));
                                 }}
                             }}
                         }}(document));"""
            self.driver.execute_script(js_str)


class HomePage(BasePage):
    def accept_cookie_warning(self):
        # if the cookie warning isn't present, this does nothing
        try:
            self.wait_for_element(
                CommonPageLocators.ACCEPT_COOKIE_BUTTON, time=1
            ).click()
        except (NoSuchElementException, TimeoutException):
            return


class MainPage(BasePage):
    set_up_account_button = MainPageLocators.SETUP_ACCOUNT_BUTTON

    def click_set_up_account(self):
        element = self.wait_for_element(MainPage.set_up_account_button)
        element.click()


class RegistrationPage(BasePage):
    name_input = NameInputElement()
    email_input = EmailInputElement()
    mobile_input = MobileInputElement()
    password_input = PasswordInputElement()

    def is_current(self):
        return self.wait_until_url_is(self.base_url + "/register")

    def register(self):
        self.name_input = config["user"]["name"]
        self.email_input = config["user"]["email"]
        self.mobile_input = config["user"]["mobile"]
        self.password_input = config["user"]["password"]
        self.click_continue()


class AddServicePage(BasePage):
    service_input = ServiceInputElement()
    org_type_input = AddServicePageLocators.ORG_TYPE_INPUT
    service_mode_input = AddServicePageLocators.SERVICE_MODE_INPUT
    add_service_button = AddServicePageLocators.ADD_SERVICE_BUTTON

    def is_current(self):
        return self.wait_until_url_is(self.base_url + "/add-service?first=first")

    def add_service(self, name):
        self.service_input = name
        try:
            self.click_org_type_input()
        except NoSuchElementException:
            pass
        self.click_add_service_button()

    def select_training_mode(self):
        try:
            self.click_service_mode_input()
        except NoSuchElementException:
            pass
        self.click_continue()

    def confirm_settings(self):
        self.wait_until_url_ends_with("confirm")
        self.click_continue()

    def click_add_service_button(self):
        element = self.wait_for_element(AddServicePage.add_service_button)
        element.click()

    def click_org_type_input(self):
        try:
            element = self.wait_for_invisible_element(AddServicePage.org_type_input)
            element.click()
        except TimeoutException:
            pass

    def click_service_mode_input(self):
        try:
            element = self.wait_for_invisible_element(AddServicePage.service_mode_input)
            element.click()
        except TimeoutException:
            pass


class ForgotPasswordPage(BasePage):
    email_input = EmailInputElement()

    def input_email_address(self, email_address):
        self.email_input = email_address


class NewPasswordPage(BasePage):
    new_password_input = NewPasswordInputElement()

    def __init__(self, driver, url):
        self.driver = driver
        self.driver.get(url)

    def input_new_password(self, password):
        self.new_password_input = password


class SignInPage(BasePage):
    email_input = EmailInputElement()
    password_input = PasswordInputElement()
    forgot_password_link = SignInPageLocators.FORGOT_PASSWORD_LINK

    def get(self):
        self.driver.get(self.base_url + "/sign-in")

    def is_current(self):
        return self.wait_until_url_is(self.base_url + "/sign-in")

    def fill_login_form(self, email, password):
        self.email_input = email
        self.password_input = password

    def click_forgot_password_link(self):
        element = self.wait_for_element(SignInPage.forgot_password_link)
        element.click()

    def login(self, email, password):
        self.fill_login_form(email, password)
        self.click_continue_to_signin()


class VerifyPage(BasePage):
    sms_input = SmsInputElement()

    def verify(self, code):
        element = self.wait_for_element(VerifyPageLocators.SMS_INPUT)
        element.clear()
        self.sms_input = code
        self.click_continue()


class DashboardPage(BasePage):
    h2 = (By.CLASS_NAME, "navigation-service-name")
    team_members_link = (By.LINK_TEXT, "Team members")
    api_keys_link = (By.LINK_TEXT, "API integration")
    navigation = (By.CLASS_NAME, "navigation")

    def _message_count_for_template_div(self, template_id):
        return (By.ID, template_id)

    def is_current(self, service_id):
        expected = "{}/services/{}/dashboard".format(self.base_url, service_id)
        return self.driver.current_url == expected

    def get_service_name(self):
        element = self.wait_for_element(DashboardPage.h2)
        return element.text

    def click_team_members_link(self):
        element = self.wait_for_element(DashboardPage.team_members_link)
        element.click()

    def click_api_integration(self):
        element = self.wait_for_element(DashboardPage.api_keys_link)
        element.click()

    def get_service_id(self):
        return self.driver.current_url.split("/services/")[1].split("/")[0]

    def get_navigation_list(self):
        element = self.wait_for_element(DashboardPage.navigation)
        return element.text

    def go_to_dashboard_for_service(self, service_id=None):
        if not service_id:
            service_id = self.get_service_id()
        url = "{}/services/{}/dashboard".format(self.base_url, service_id)
        self.driver.get(url)


class ShowTemplatesPage(PageWithStickyNavMixin, BasePage):
    add_new_template_link = (By.CSS_SELECTOR, "button[value='add-new-template']")
    add_new_folder_link = (By.CSS_SELECTOR, "button[value='add-new-folder']")
    add_to_new_folder_link = (By.CSS_SELECTOR, "button[value='move-to-new-folder']")
    move_to_existing_folder_link = (
        By.CSS_SELECTOR,
        "button[value='move-to-existing-folder']",
    )
    email_filter_link = (By.LINK_TEXT, "Email")

    email_radio = (By.CSS_SELECTOR, "input[type='radio'][value='email']")
    text_message_radio = (By.CSS_SELECTOR, "input[type='radio'][value='sms']")
    letter_radio = (By.CSS_SELECTOR, "input[type='radio'][value='letter']")

    add_new_folder_textbox = BasePageElement(name="add_new_folder_name")
    add_to_new_folder_textbox = BasePageElement(name="move_to_new_folder_name")

    root_template_folder_radio = (
        By.CSS_SELECTOR,
        "input[type='radio'][value='__NONE__']",
    )

    @staticmethod
    def input_element_by_label_text(text, input_type="checkbox"):
        return (
            By.XPATH,
            f"//label[normalize-space(.)='{text}']/preceding-sibling::input[@type='{input_type}']",
        )

    @staticmethod
    def template_link_text(link_text):
        return (
            By.XPATH,
            f"//div[contains(@id,'template-list')]//a/span[contains(normalize-space(.), '{link_text}')]",
        )

    @staticmethod
    def template_checkbox(template_id):
        return (
            By.CSS_SELECTOR,
            "input[type='checkbox'][value='{}']".format(template_id),
        )

    def click_add_new_template(self):
        element = self.wait_for_element(self.add_new_template_link)
        element.click()

    def click_add_new_folder(self, folder_name):
        element = self.wait_for_element(self.add_new_folder_link)
        element.click()

        self.add_new_folder_textbox = folder_name
        # green submit button
        element = self.wait_for_element(self.add_new_folder_link)
        element.click()

    def click_template_by_link_text(self, link_text):
        element = self.wait_for_element(self.template_link_text(link_text))
        self.scrollToRevealElement(xpath=self.template_link_text(link_text)[1])
        element.click()

    def _select_template_type(self, type):
        # wait for continue button to be displayed - sticky nav has rendered properly
        # we've seen issues
        radio_element = self.wait_for_invisible_element(type)
        self.select_checkbox_or_radio(radio_element)

        self.click_continue()

    def select_template_checkbox(self, template_id):
        element = self.wait_for_invisible_element(self.template_checkbox(template_id))
        self.select_checkbox_or_radio(element)

    def check_input_with_label_text(self, text, input_type):
        element = self.wait_for_invisible_element(
            self.input_element_by_label_text(text, input_type=input_type)
        )
        self.select_checkbox_or_radio(element)

    def add_to_new_folder(self, folder_name):
        # grey button to go to the name input box
        element = self.wait_for_element(self.add_to_new_folder_link)
        element.click()
        self.add_to_new_folder_textbox = folder_name

        # green submit button
        element = self.wait_for_element(self.add_to_new_folder_link)
        element.click()

    def move_to_root_template_folder(self):
        move_button = self.wait_for_element(self.move_to_existing_folder_link)
        move_button.click()
        # wait for continue button to be displayed - sticky nav has rendered properly
        # we've seen issues
        radio_element = self.wait_for_invisible_element(self.root_template_folder_radio)

        self.select_checkbox_or_radio(radio_element)
        self.click_continue()

    def move_template_to_folder(self, folder_name):
        move_button = self.wait_for_element(self.move_to_existing_folder_link)
        move_button.click()
        radio_element = self.wait_for_invisible_element(
            self.input_element_by_label_text(text=folder_name, input_type="radio")
        )
        self.select_checkbox_or_radio(element=radio_element)
        self.click_continue()

    def get_folder_by_name(self, folder_name):
        try:
            return self.wait_for_invisible_element(self.template_link_text(folder_name))
        except TimeoutException:
            return None


class SendSmsTemplatePage(BasePage):
    new_sms_template_link = TemplatePageLocators.ADD_NEW_TEMPLATE_LINK
    edit_sms_template_link = TemplatePageLocators.EDIT_TEMPLATE_LINK

    def click_add_new_template(self):
        element = self.wait_for_element(SendSmsTemplatePage.new_sms_template_link)
        element.click()


class EditBroadcastTemplatePage(BasePage):
    name_input = NameInputElement()
    template_content_input = TemplateContentElement()
    save_button = EditTemplatePageLocators.SAVE_BUTTON
    edit_button = EditTemplatePageLocators.EDIT_BUTTON
    prep_to_send_button = EditTemplatePageLocators.PREP_TO_SEND_BUTTON
    delete_button = EditTemplatePageLocators.DELETE_BUTTON
    confirm_delete_button = EditTemplatePageLocators.CONFIRM_DELETE_BUTTON

    @staticmethod
    def folder_path_item(folder_name):
        return (
            By.XPATH,
            "//a[contains(@class,'folder-heading-folder')]/text()[contains(.,'{}')]/..".format(
                folder_name
            ),
        )

    def create_template(self, name="Template Name", content=None):
        self.name_input = name
        if content:
            self.template_content_input = content
        else:
            self.template_content_input = "Placeholder text for alert content"
        self.click_save()

    def click_save(self):
        element = self.wait_for_element(EditBroadcastTemplatePage.save_button)
        element.click()

    def click_edit(self):
        element = self.wait_for_element(EditBroadcastTemplatePage.edit_button)
        element.click()

    def click_prep_to_send(self):
        element = self.wait_for_element(EditBroadcastTemplatePage.prep_to_send_button)
        element.click()

    def click_delete(self):
        element = self.wait_for_element(EditBroadcastTemplatePage.delete_button)
        element.click()
        element = self.wait_for_element(EditBroadcastTemplatePage.confirm_delete_button)
        element.click()

    def click_folder_path(self, folder_name):
        element = self.wait_for_element(self.folder_path_item(folder_name))
        element.click()


class SendEmailTemplatePage(BasePage):
    add_a_new_email_template_link = TemplatePageLocators.ADD_A_NEW_TEMPLATE_LINK
    add_new_email_template_link = TemplatePageLocators.ADD_NEW_TEMPLATE_LINK
    edit_email_template_link = TemplatePageLocators.EDIT_TEMPLATE_LINK

    def click_add_a_new_template(self):
        element = self.wait_for_element(
            SendEmailTemplatePage.add_a_new_email_template_link
        )
        element.click()

    def click_add_new_template(self):
        element = self.wait_for_element(
            SendEmailTemplatePage.add_new_email_template_link
        )
        element.click()


class ViewTemplatePage(BasePage):
    def click_send(self):
        element = self.wait_for_element(ViewTemplatePageLocators.SEND_BUTTON)
        element.click()


class EditEmailTemplatePage(BasePage):
    name_input = NameInputElement()
    subject_input = SubjectInputElement()
    template_content_input = TemplateContentElement()
    save_button = EditTemplatePageLocators.SAVE_BUTTON
    delete_button = EditTemplatePageLocators.DELETE_BUTTON
    confirm_delete_button = EditTemplatePageLocators.CONFIRM_DELETE_BUTTON

    @staticmethod
    def folder_path_item(folder_name):
        return (
            By.XPATH,
            "//a[contains(@class,'folder-heading-folder') and contains(text(), '{}')]".format(
                folder_name
            ),
        )

    def click_save(self):
        element = self.wait_for_element(EditEmailTemplatePage.save_button)
        element.click()

    def click_delete(self):
        element = self.wait_for_element(EditEmailTemplatePage.delete_button)
        element.click()
        element = self.wait_for_element(EditEmailTemplatePage.confirm_delete_button)
        element.click()

    def create_template(self, name="Test email template", content=None):
        self.name_input = name
        self.subject_input = "Test email from functional tests"
        if content:
            self.template_content_input = content
        else:
            self.template_content_input = "The quick brown fox jumped over the lazy dog. Jenkins job id: ((build_id))"
        self.click_save()

    def click_folder_path(self, folder_name):
        element = self.wait_for_element(self.folder_path_item(folder_name))
        element.click()


class TeamMembersPage(BasePage):
    h1 = TeamMembersPageLocators.H1
    invite_team_member_button = TeamMembersPageLocators.INVITE_TEAM_MEMBER_BUTTON
    edit_team_member_link = TeamMembersPageLocators.EDIT_TEAM_MEMBER_LINK
    confirm_remove_button = TeamMembersPageLocators.CONFIRM_REMOVE_BUTTON

    def get_edit_link_for_member_name(self, email):
        return self.wait_for_element(
            (
                By.XPATH,
                "//h2[@title='{}']/ancestor::div[contains(@class, 'user-list-item')]//a".format(
                    email
                ),
            )
        )

    def h1_is_team_members(self):
        element = self.wait_for_element(TeamMembersPage.h1)
        return element.text == "Team members"

    def click_invite_user(self):
        element = self.wait_for_element(TeamMembersPage.invite_team_member_button)
        element.click()

    def click_edit_team_member(self, email):
        element = self.get_edit_link_for_member_name(email)
        element.click()

    def click_yes_remove(self):
        element = self.wait_for_element(TeamMembersPage.confirm_remove_button)
        element.click()


class InviteUserPage(BasePage):
    email_input = EmailInputElement()
    see_dashboard_check_box = InviteUserPageLocators.SEE_DASHBOARD_CHECKBOX
    choose_folders_button = InviteUserPageLocators.CHOOSE_FOLDERS_BUTTON
    send_messages_checkbox = InviteUserPageLocators.SEND_MESSAGES_CHECKBOX
    manage_services_checkbox = InviteUserPageLocators.MANAGE_SERVICES_CHECKBOX
    manage_templates_checkbox = InviteUserPageLocators.MANAGE_TEMPLATES_CHECKBOX
    manage_api_keys_checkbox = InviteUserPageLocators.MANAGE_API_KEYS_CHECKBOX
    choose_folders_button = InviteUserPageLocators.CHOOSE_FOLDERS_BUTTON
    send_invitation_button = InviteUserPageLocators.SEND_INVITATION_BUTTON

    def get_folder_checkbox(self, folder_name):
        label = self.driver.find_elements(
            By.XPATH, f"//label[contains(text(), '{folder_name}')]"
        )
        return (By.ID, label[0].get_attribute("for"))

    def fill_invitation_form(self, email, send_messages_only):
        self.email_input = email
        if send_messages_only:
            element = self.wait_for_invisible_element(
                InviteUserPage.send_messages_checkbox
            )
            self.select_checkbox_or_radio(element)
        else:
            element = self.wait_for_invisible_element(
                InviteUserPage.see_dashboard_check_box
            )
            self.select_checkbox_or_radio(element)
            element = self.wait_for_invisible_element(
                InviteUserPage.send_messages_checkbox
            )
            self.select_checkbox_or_radio(element)
            element = self.wait_for_invisible_element(
                InviteUserPage.manage_templates_checkbox
            )
            self.select_checkbox_or_radio(element)
            element = self.wait_for_invisible_element(
                InviteUserPage.manage_services_checkbox
            )
            self.select_checkbox_or_radio(element)
            element = self.wait_for_invisible_element(
                InviteUserPage.manage_api_keys_checkbox
            )
            self.select_checkbox_or_radio(element)

    def send_invitation(self):
        element = self.wait_for_element(InviteUserPage.send_invitation_button)
        element.click()

    def send_invitation_without_permissions(self, email):
        self.email_input = email
        element = self.wait_for_element(InviteUserPage.send_invitation_button)
        element.click()

    # support variants of this page with a 'Save' button instead of 'Send invitation' (both use the same locator)
    def click_save(self):
        self.send_invitation()

    def uncheck_folder_permission_checkbox(self, folder_name):
        try:
            choose_folders_button = self.wait_for_invisible_element(
                InviteUserPage.choose_folders_button
            )
            choose_folders_button.click()
        except (NoSuchElementException, TimeoutException):
            pass

        checkbox = self.wait_for_invisible_element(
            self.get_folder_checkbox(folder_name)
        )
        self.unselect_checkbox(checkbox)

    def is_checkbox_checked(self, folder_name):
        try:
            choose_folders_button = self.wait_for_invisible_element(
                InviteUserPage.choose_folders_button
            )
            choose_folders_button.click()
        except (NoSuchElementException, TimeoutException):
            pass

        checkbox = self.wait_for_invisible_element(
            self.get_folder_checkbox(folder_name)
        )
        return checkbox.get_attribute("checked")


class RegisterFromInvite(BasePage):
    name_input = NameInputElement()
    mobile_input = MobileInputElement()
    password_input = PasswordInputElement()

    def fill_registration_form(self, name):
        self.name_input = name
        self.mobile_input = config["user"]["mobile"]
        self.password_input = config["user"]["password"]


class ApiIntegrationPage(BasePage):
    message_log = ApiIntegrationPageLocators.MESSAGE_LOG
    heading_button = ApiIntegrationPageLocators.HEADING_BUTTON
    client_reference = ApiIntegrationPageLocators.CLIENT_REFERENCE
    message_list = ApiIntegrationPageLocators.MESSAGE_LIST
    status = ApiIntegrationPageLocators.STATUS
    view_letter_link = ApiIntegrationPageLocators.VIEW_LETTER_LINK

    def get_notification_id(self):
        element = self.wait_for_elements(ApiIntegrationPage.message_list)[0]
        return element.text

    def expand_all_messages(self):
        buttons = self.wait_for_elements(ApiIntegrationPage.heading_button)
        for index in range(len(buttons)):
            buttons[index].click()

    def get_client_reference(self):
        element = self.wait_for_elements(ApiIntegrationPage.client_reference)[1]
        return element.text

    def go_to_api_integration_for_service(self, service_id):
        url = "{}/services/{}/api".format(self.base_url, service_id)
        self.driver.get(url)

    def get_status_from_message(self):
        element = self.wait_for_elements(ApiIntegrationPage.status)[0]
        return element.text

    def get_view_letter_link(self):
        link = self.wait_for_elements(ApiIntegrationPage.view_letter_link)[0]
        return link.get_attribute("href")

    def go_to_preview_letter(self):
        link = self.wait_for_elements(ApiIntegrationPage.view_letter_link)[0]
        self.driver.get(link.get_attribute("href"))


class ApiKeysPage(BasePage):
    create_key_link = ApiKeysPageLocators.CREATE_KEY_BUTTON
    key_name_input = KeyNameInputElement()
    confirm_revoke_button = ApiKeysPageLocators.CONFIRM_REVOKE_BUTTON

    def click_create_key(self):
        element = self.wait_for_element(ApiKeysPage.create_key_link)
        element.click()

    def create_key(self, key_name):
        self.key_name_input = key_name
        self.select_checkbox_or_radio(value="normal")
        self.click_continue()

    def get_key_name(self):
        element = self.wait_for_element(ApiKeysPageLocators.KEY_COPY_VALUE)
        return element.text

    def wait_for_key_copy_button(self):
        element = self.wait_for_element(ApiKeysPageLocators.KEY_COPY_BUTTON)
        return element

    def wait_for_show_key_button(self):
        element = self.wait_for_element(ApiKeysPageLocators.KEY_SHOW_BUTTON)
        return element

    def check_new_key_name(self, starts_with):
        return self.get_key_name().startswith(starts_with)

    def get_revoke_link_for_api_key(self, key_name):
        return self.wait_for_element(
            (
                By.XPATH,
                f"//tr[.//div[contains(normalize-space(.),'{key_name}')]]//a",
            )
        )

    def revoke_api_key(self, key_name):
        element = self.get_revoke_link_for_api_key(key_name)
        element.click()

        element = self.wait_for_element(ApiKeysPage.confirm_revoke_button)
        element.click()


class ServiceSettingsPage(BasePage):
    h2 = (By.CLASS_NAME, "navigation-service-name")
    name_input = ClearableInputElement(name="name")

    @staticmethod
    def change_setting_link(setting):
        return (
            By.XPATH,
            f"//a[contains(normalize-space(.),'Change')]/span[contains(normalize-space(.),'{setting}')]/parent::a",
        )

    def click_change_setting(self, setting):
        element = self.wait_for_element(self.change_setting_link(setting))
        element.click()

    def get_service_name(self):
        element = self.wait_for_element(ServiceSettingsLocators.SERVICE_NAME)
        return element.text

    def save_service_name(self, new_name):
        self.name_input = new_name
        self.click_save()

    def delete_service(self):
        self.click_element_by_link_text("Delete this service")
        element = self.wait_for_element(ServiceSettingsLocators.DELETE_CONFIRM_BUTTON)
        element.click()


class ProfileSettingsPage(BasePage):
    name_input = ClearableInputElement(name="new_name")
    mobile_input = ClearableInputElement(name="mobile_number")
    password_input = PasswordInputElement()
    verification_code_input = SmsInputElement()

    @staticmethod
    def change_setting_link(setting):
        return (
            By.XPATH,
            f"//a[contains(normalize-space(.),'Change')]/span[contains(normalize-space(.),'{setting}')]/parent::a",
        )

    def click_change_setting(self, setting):
        element = self.wait_for_element(self.change_setting_link(setting))
        element.click()

    def save_name(self, new_name):
        self.name_input = new_name

    def save_mobile_number(self, new_number):
        self.mobile_input = new_number

    def enter_password(self, password):
        self.password_input = password
        self.click_continue_to_submit()

    def enter_verification_code(self, code):
        self.verification_code_input = code
        self.click_save()


class ChangeName(BasePage):
    def go_to_change_service_name(self, service_id):
        url = "{}/services/{}/service-settings/name".format(self.base_url, service_id)
        self.driver.get(url)

    def enter_new_name(self, new_name):
        element = self.wait_for_element(ChangeNameLocators.CHANGE_NAME_FIELD)
        element.clear()
        element.send_keys(new_name)


class OrganisationDashboardPage(BasePage):
    h1 = (By.CSS_SELECTOR, "h1")
    team_members_link = (By.LINK_TEXT, "Team members")
    service_list = (By.CSS_SELECTOR, "main .browse-list-item")

    def is_current(self, org_id):
        expected = "{}/organisations/{}".format(self.base_url, org_id)
        return self.driver.current_url == expected

    def click_team_members_link(self):
        element = self.wait_for_element(DashboardPage.team_members_link)
        element.click()

    def go_to_dashboard_for_org(self, org_id):
        url = "{}/organisations/{}".format(self.base_url, org_id)
        self.driver.get(url)


class InviteUserToOrgPage(BasePage):
    email_input = EmailInputElement()
    send_invitation_button = InviteUserPageLocators.SEND_INVITATION_BUTTON

    def fill_invitation_form(self, email):
        self.email_input = email

    def send_invitation(self):
        element = self.wait_for_element(self.send_invitation_button)
        element.click()


class InboxPage(BasePage):
    def is_current(self, service_id):
        expected = "{}/services/{}/inbox".format(self.base_url, service_id)
        return self.driver.current_url == expected

    def go_to_conversation(self, user_number):
        # link looks like "07123 456789". because i don't know if user_number starts with +44, just get the last 10
        # digits. (so this'll look for partial link text of "123 456789")
        formatted_phone_number = "{} {}".format(user_number[-10:-6], user_number[-6:])
        element = self.wait_for_element((By.PARTIAL_LINK_TEXT, formatted_phone_number))
        element.click()


class ConversationPage(BasePage):
    sms_message = (By.CSS_SELECTOR, ".sms-message-wrapper")

    def get_message(self, content):
        elements = self.wait_for_elements(self.sms_message)
        return next((el for el in elements if content in el.text), None)


class DocumentDownloadBasePage(BasePage):
    def get_errors(self):
        # these are diff to notify admin which has the class .banner-dangerous for its error messages
        error_message = (By.CSS_SELECTOR, ".govuk-error-summary")
        errors = self.wait_for_element(error_message)
        return errors.text.strip()


class DocumentDownloadLandingPage(DocumentDownloadBasePage):
    continue_button = (By.CSS_SELECTOR, "a.govuk-button")

    def get_service_name(self):
        element = self.wait_for_element((By.CSS_SELECTOR, "main p:first-of-type"))

        return element.text.partition(" sent you ")[0]

    def go_to_download_page(self):
        button = self.wait_for_element(self.continue_button)

        button.click()


class DocumentDownloadPage(DocumentDownloadBasePage):
    download_link = (By.PARTIAL_LINK_TEXT, "Download this ")

    def _get_download_link_element(self):
        link = self.wait_for_element(self.download_link)

        return link.element

    def click_download_link(self):
        return self._get_download_link_element().click()

    def get_download_link(self):
        return self._get_download_link_element().get_attribute("href")


class DocumentDownloadConfirmEmailPage(DocumentDownloadBasePage):
    continue_button = CommonPageLocators.CONTINUE_BUTTON
    email_input = EmailInputElement()

    def input_email_address(self, email_address):
        self.email_input = email_address


class ViewFolderPage(ShowTemplatesPage):
    manage_link = (By.CSS_SELECTOR, ".folder-heading-manage-link")
    template_path_and_name = (By.TAG_NAME, "h1")

    def click_manage_folder(self):
        link = self.wait_for_element(self.manage_link)
        link.click()

    def assert_name_equals(self, expected_name):
        h1 = self.wait_for_element(self.template_path_and_name)
        assert expected_name in h1.text


class ManageFolderPage(BasePage):
    delete_link = (By.LINK_TEXT, "Delete this folder")
    name_input = NameInputElement()
    delete_button = (By.NAME, "delete")
    save_button = (
        By.CSS_SELECTOR,
        "form button.govuk-button:not(.govuk-button--secondary)",
    )

    def set_name(self, new_name):
        self.name_input = new_name
        button = self.wait_for_element(self.save_button)
        button.click()

    def delete_folder(self):
        link = self.wait_for_element(self.delete_link)
        link.click()

    def confirm_delete_folder(self):
        link = self.wait_for_element(self.delete_button)
        link.click()


class BroadcastFreeformPage(BasePage):
    title_input = NameInputElement()
    content_input = TemplateContentElement()

    def create_broadcast_content(self, title, content):
        self.title_input = title
        self.content_input = content


class GovUkAlertsPage(BasePage):
    def __init__(self, driver):
        self.gov_uk_alerts_url = config["govuk_alerts_url"]
        self.driver = driver

    def get(self):
        self.driver.get(self.gov_uk_alerts_url)

    @retry(
        RetryException,
        tries=config["govuk_alerts_wait_retry_times"],
        delay=config["govuk_alerts_wait_retry_interval"],
    )
    def check_alert_is_published(self, broadcast_content):
        if not self.text_is_on_page(broadcast_content):
            self.driver.refresh()
            raise RetryException(
                f'Could not find alert with content "{broadcast_content}"'
            )


class BroadcastDurationPage(BasePage):
    change_duration = ChangeDurationLink()
    hours_input = HoursInputElement()
    minutes_input = MinutesInputElement()

    def click_change_duration(self):
        element = self.wait_for_element(DurationPageLocators.CHANGE_DURATION_LINK)
        element.click()

    def set_alert_duration(self, hours, minutes):
        self.hours_input = hours
        self.minutes_input = minutes


class SupportFeedbackPage(BasePage):
    text_input = FeedbackTextAreaElement()

    def fill_textarea(self, text):
        self.text_input = text


class SearchPostcodePage(BasePage):
    postcode_input = PostcodeInputElement()
    radius_input = RadiusInputElement()
    search_button = SearchButton()
    preview_button = PreviewButton()

    def create_custom_area(self, postcode, radius):
        self.postcode_input = postcode
        self.radius_input = radius

    def click_search(self):
        element = self.wait_for_element(SearchPostcodePageLocators.SEARCH_BUTTON)
        element.click()

    def click_preview(self):
        element = self.wait_for_element(SearchPostcodePageLocators.PREVIEW_BUTTON)
        element.click()


class PlatformAdminPage(BasePage):
    search_link = (By.LINK_TEXT, "Search")
    search_input = SearchInputElement()

    def subheading_is(self, expected_subheading):
        element = self.wait_for_element(CommonPageLocators.H2)
        return element.text == expected_subheading

    def click_search_link(self):
        element = self.wait_for_element(PlatformAdminPage.search_link)
        element.click()

    def search_for(self, text):
        self.search_input = text
        self.click_continue()


class ChooseCoordinatesType(BasePage):
    pass


class ChooseCoordinateArea(BasePage):
    first_coordinate_input = FirstCoordinateInputElement()
    second_coordinate_input = SecondCoordinateInputElement()
    radius_input = CoordinateRadiusInputElement()
    search_button = CoordinateSearchButton()
    preview_button = CoordinatePreviewButton()

    def create_coordinate_area(self, first_coordinate, second_coordinate, radius):
        self.first_coordinate_input = first_coordinate
        self.second_coordinate_input = second_coordinate
        self.radius_input = radius

    def click_search(self):
        element = self.wait_for_element(SearchCoordinatePageLocators.SEARCH_BUTTON)
        element.click()

    def click_preview(self):
        element = self.wait_for_element(SearchCoordinatePageLocators.PREVIEW_BUTTON)
        element.click()


class ThrottledPage(BasePage):
    pass


class DashboardWithDialogs(BasePage):
    inactivity_dialog = InactivityDialog()
    inactivity_stay_signed_in_btn = InactivityDialogStaySignedInButton()
    sign_out_btn = DialogSignOutButton()
    expiry_continue_btn = ExpiryDialogContinueButton()
    expiry_dialog = ExpiryDialog()

    def click_stay_signed_in(self):
        element = self.wait_for_element(
            DashboardWithDialogPageLocators.STAY_SIGNED_IN_BUTTON
        )
        element.click()

    def click_continue(self):
        element = self.wait_for_element(DashboardWithDialogPageLocators.CONTINUE_BUTTON)
        element.click()

    def is_inactivity_dialog_visible(self):
        element = self.wait_for_element(
            DashboardWithDialogPageLocators.INACTIVITY_DIALOG
        )
        return element.get_attribute("open")

    def is_expiry_dialog_visible(self):
        element = self.wait_for_element(DashboardWithDialogPageLocators.EXPIRY_DIALOG)
        return element.get_attribute("open")

    def is_inactivity_dialog_hidden(self):
        element = self.wait_for_invisible_element(
            DashboardWithDialogPageLocators.INACTIVITY_DIALOG
        )
        return not element.get_attribute("open")

    def is_expiry_dialog_hidden(self):
        element = self.wait_for_invisible_element(
            DashboardWithDialogPageLocators.EXPIRY_DIALOG
        )
        return not element.get_attribute("open")


class RejectionForm(BasePage):
    rejection_detail_element = RejectionDetailElement()
    rejection_reason_text_area = RejectionReasonTextArea()
    reject_alert_btn = RejectAlertButton()
    rejection_detail_link = RejectionDetailLink()

    def click_open_reject_detail(self):
        element = self.wait_for_element(RejectionFormLocators.REJECTION_DETAIL_LINK)
        element.click()

    def rejection_details_is_open(self):
        element = self.wait_for_element(RejectionFormLocators.REJECTION_DETAIL_ELEMENT)
        return element.get_attribute("open")

    def rejection_details_is_closed(self):
        element = self.wait_for_element(RejectionFormLocators.REJECTION_DETAIL_ELEMENT)
        return not element.get_attribute("open")

    def click_reject_alert(self):
        element = self.wait_for_element(RejectionFormLocators.REJECT_ALERT_BUTTON)
        element.click()

    def create_rejection_reason_input(self, content):
        self.rejection_reason_text_area = content

    def get_rejection_form_errors(self):
        error_message = (By.CSS_SELECTOR, ".govuk-error-message")
        errors = self.wait_for_element(error_message)
        return errors.text.strip()
