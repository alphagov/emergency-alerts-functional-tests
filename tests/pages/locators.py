from tests.playwright_adapter import By


class CommonPageLocators(object):
    NAME_INPUT = (By.NAME, "name")
    REFERENCE_INPUT = (By.NAME, "reference")
    FOLDER_NAME_INPUT = (By.NAME, "name")
    EMAIL_INPUT = (By.NAME, "email_address")
    PASSWORD_INPUT = (By.NAME, "password")
    MOBILE_NUMBER = (By.NAME, "mobile_number")
    SUBMIT_BUTTON = (By.CSS_SELECTOR, "main button.govuk-button")
    CONTINUE_BUTTON = (By.NAME, "continue")
    PREVIEW_BUTTON = (By.NAME, "preview")
    ACCEPT_COOKIE_BUTTON = (By.CLASS_NAME, "notify-cookie-banner__button-accept")
    LIVE_BROADCAST = (By.CLASS_NAME, "live-broadcast")
    H1 = (By.TAG_NAME, "H1")
    CONTINUE_FOOTER_BUTTON = (
        By.CSS_SELECTOR,
        "main button.govuk-button.page-footer__button",
    )
    SUBMIT_FOOTER_BUTTON = (
        By.CSS_SELECTOR,
        "main button.govuk-button.page-footer__button",
    )


class DurationPageLocators(object):
    HOURS_INPUT = (By.ID, "hours")
    MINUTES_INPUT = (By.ID, "minutes")


class MainPageLocators(object):
    SETUP_ACCOUNT_BUTTON = (By.CSS_SELECTOR, "a.govuk-button.product-page-button")


class SignUpPageLocators(object):
    MOBILE_INPUT = (By.NAME, "mobile_number")


class SignInPageLocators(object):
    FORGOT_PASSWORD_LINK = (By.LINK_TEXT, "Forgotten your password?")
    H1 = (By.TAG_NAME, "h1")


class NewPasswordPageLocators(object):
    NEW_PASSWORD_INPUT = (By.NAME, "password")


class VerifyPageLocators(object):
    SMS_INPUT = (By.NAME, "sms_code")


class AddServicePageLocators(object):
    SERVICE_INPUT = (By.NAME, "name")
    ORG_TYPE_INPUT = (By.ID, "organisation_type-0")
    TRAINING_MODE_INPUT = (By.ID, "channel-0")
    OPERATOR_MODE_INPUT = (By.ID, "channel-1")
    ADD_SERVICE_BUTTON = (By.CSS_SELECTOR, "main button.govuk-button")


class NavigationLocators(object):
    SIGN_OUT_LINK = (By.LINK_TEXT, "Sign out")
    TEMPLATES_LINK = (By.LINK_TEXT, "Templates")
    SETTINGS_LINK = (By.LINK_TEXT, "Settings")


class TemplatePageLocators(object):
    SEND_TEST_MESSAGES_LINK = (By.LINK_TEXT, "Send text messages")
    SEND_EMAIL_LINK = (By.LINK_TEXT, "Send emails")
    ADD_NEW_TEMPLATE_LINK = (By.LINK_TEXT, "Add new template")
    ADD_A_NEW_TEMPLATE_LINK = (By.LINK_TEXT, "Add a new template")
    EDIT_TEMPLATE_LINK = (By.LINK_TEXT, "Edit template")
    UPLOAD_RECIPIENTS_LINK = (By.LINK_TEXT, "Upload recipients")


class EditTemplatePageLocators(object):
    TEMPLATE_SUBJECT_INPUT = (By.NAME, "subject")
    TEMPLATE_CONTENT_INPUT = (By.NAME, "content")
    SAVE_BUTTON = (By.CSS_SELECTOR, "main button.govuk-button")
    EDIT_BUTTON = (
        By.XPATH,
        "//a[contains(@class, 'govuk-link') and contains(text(),'Change')]",
    )
    PREP_TO_SEND_BUTTON = (
        By.XPATH,
        "//a[contains(@class, 'govuk-link') and contains(text(),'Save and get ready to send')]",
    )
    DELETE_BUTTON = (By.LINK_TEXT, "Delete this template")
    CONFIRM_DELETE_BUTTON = (By.NAME, "delete")


class ExtraContentPageLocators(object):
    EXTRA_CONTENT_INPUT = (By.NAME, "extra_content")
    SAVE_BUTTON = (By.CSS_SELECTOR, "main button.govuk-button")


class TeamMembersPageLocators(object):
    H1 = (By.TAG_NAME, "h1")
    INVITE_TEAM_MEMBER_BUTTON = (By.CSS_SELECTOR, "a.govuk-button")
    EDIT_TEAM_MEMBER_LINK = (By.LINK_TEXT, "Edit team member")
    CONFIRM_REMOVE_BUTTON = (By.NAME, "delete")


class InviteUserPageLocators(object):
    CREATE_BROADCASTS_CHECKBOX = (
        By.CSS_SELECTOR,
        "[value=create_broadcasts], [name=create_broadcasts]",
    )
    SEND_MESSAGES_CHECKBOX = (
        By.CSS_SELECTOR,
        "[value=send_messages], [name=send_messages]",
    )
    SEE_DASHBOARD_CHECKBOX = (
        By.CSS_SELECTOR,
        "[value=view_activity], [name=view_activity]",
    )
    MANAGE_SERVICES_CHECKBOX = (
        By.CSS_SELECTOR,
        "[value=manage_service], [name=manage_service]",
    )
    MANAGE_API_KEYS_CHECKBOX = (
        By.CSS_SELECTOR,
        "[value=manage_api_keys], [name=manage_api_keys]",
    )
    MANAGE_TEMPLATES_CHECKBOX = (
        By.CSS_SELECTOR,
        "[value=manage_templates], [name=manage_templates]",
    )
    CHOOSE_FOLDERS_BUTTON = (
        By.CSS_SELECTOR,
        "button[aria-controls=folder_permissions]",
    )
    SEND_INVITATION_BUTTON = (
        By.CSS_SELECTOR,
        "form button.govuk-button:not(.govuk-button--secondary)",
    )


class ApiIntegrationPageLocators(object):
    MESSAGE_LOG = (By.CSS_SELECTOR, "div.api-notifications > details:nth-child(1)")
    HEADING_BUTTON = (By.CSS_SELECTOR, ".govuk-details__summary")
    CLIENT_REFERENCE = (By.CSS_SELECTOR, ".api-notifications-item__data-value")
    MESSAGE_LIST = (By.CSS_SELECTOR, ".api-notifications-item__data-value")
    STATUS = (By.CSS_SELECTOR, ".api-notifications-item__data-value:last-of-type")
    VIEW_LETTER_LINK = (By.LINK_TEXT, "View letter")


class ApiKeysPageLocators(object):
    CREATE_KEY_BUTTON = (By.LINK_TEXT, "Create an API key")
    KEY_NAME_INPUT = (By.NAME, "key_name")
    KEY_COPY_VALUE = (By.CLASS_NAME, "copy-to-clipboard")
    KEY_COPY_BUTTON = (By.CLASS_NAME, "copy-to-clipboard__button--copy")
    KEY_SHOW_BUTTON = (By.CLASS_NAME, "copy-to-clipboard__button--show")
    CONFIRM_REVOKE_BUTTON = (By.NAME, "delete")


class ServiceSettingsLocators(object):
    SERVICE_NAME = (By.CSS_SELECTOR, ".navigation-service-name")
    DELETE_CONFIRM_BUTTON = (By.NAME, "delete")


class ChangeNameLocators(object):
    CHANGE_NAME_FIELD = (By.ID, "name")
    PASSWORD_FIELD = (By.ID, "password")


class ViewTemplatePageLocators(object):
    SEND_BUTTON = (By.PARTIAL_LINK_TEXT, "Get ready to send")


class SupportPageLocators(object):
    FEEDBACK_TEXTAREA = (By.ID, "feedback")


class SearchPostcodePageLocators(object):
    POSTCODE_TEXTAREA = (By.ID, "postcode")
    RADIUS_TEXTAREA = (By.ID, "radius")
    SEARCH_BUTTON = (By.NAME, "search_btn")
    PREVIEW_BUTTON = (By.NAME, "preview")


class SearchCoordinatePageLocators(object):
    FIRST_COORDINATE_TEXTAREA = (By.ID, "first_coordinate")
    SECOND_COORDINATE_TEXTAREA = (By.ID, "second_coordinate")
    RADIUS_TEXTAREA = (By.ID, "radius")
    SEARCH_BUTTON = (By.NAME, "radius_btn")
    PREVIEW_BUTTON = (By.NAME, "preview")


class PlatformAdminPageLocators(object):
    SEARCH_INPUT = (By.NAME, "search")


class DashboardWithDialogPageLocators(object):
    STAY_SIGNED_IN_BUTTON = (By.NAME, "stay-signed-in-btn")
    SIGN_OUT_BUTTON = (By.ID, "hmrc-timeout-sign-out-link")
    EXPIRY_DIALOG = (By.XPATH, '//*[@id="expiry" and @class="hmrc-timeout-dialog"]')
    INACTIVITY_DIALOG = (
        By.XPATH,
        '//*[@id="activity" and @class="hmrc-timeout-dialog"]',
    )
    INACTIVITY_WARNING_DIALOG = (
        By.XPATH,
        '//*[@id="activity-warning" and @class="hmrc-timeout-dialog"]',
    )
    CONTINUE_BUTTON = (By.NAME, "continue-btn")


class RejectionFormLocators(object):
    REJECTION_DETAIL_LINK = (
        By.XPATH,
        '//*[@id="rejection_reason_details"]/summary/span',
    )
    REJECTION_DETAIL_ELEMENT = (By.ID, "rejection_reason_details")
    REJECTION_REASON_TEXTAREA = (By.ID, "rejection_reason")
    REJECT_ALERT_BUTTON = (By.NAME, "reject-alert")


class ReturnForEditFormLocators(object):
    RETURN_FOR_EDIT_DETAIL_LINK = (
        By.XPATH,
        '//*[@id="return_for_edit_reason"]/summary/span',
    )
    RETURN_FOR_EDIT_DETAIL_ELEMENT = (By.ID, "return_for_edit_reason")
    RETURN_FOR_EDIT_REASON_TEXTAREA = (By.ID, "return_for_edit_reason")
    RETURN_FOR_EDIT_ALERT_BUTTON = (By.NAME, "return-alert-for-edit")
    RETURN_FOR_EDIT_BANNER = (By.ID, "returned-reason-banner")


class AdminApprovalPageLocators(object):
    APPROVE_BUTTON = (By.CSS_SELECTOR, "button[data-button-type='approve']")
    REJECT_BUTTON = (By.CSS_SELECTOR, "button[data-button-type='reject']")
