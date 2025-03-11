import time
import uuid
from datetime import datetime, timedelta

import pytest

from config import config
from tests.functional.preview_and_dev.sample_cap_xml import (
    ALERT_XML,
    CANCEL_XML,
)
from tests.pages import (
    BasePage,
    BroadcastFreeformPage,
    DashboardPage,
    ShowTemplatesPage,
)
from tests.pages.pages import (
    ChooseCoordinateArea,
    ChooseCoordinatesType,
    RejectionForm,
    SearchPostcodePage,
)
from tests.pages.rollups import sign_in
from tests.test_utils import (
    check_alert_is_published_on_govuk_alerts,
    convert_naive_utc_datetime_to_cap_standard_string,
    create_broadcast_template,
    delete_template,
    go_to_templates_page,
)

test_group_name = "broadcast-flow"


@pytest.mark.xdist_group(name=test_group_name)
def test_prepare_broadcast_with_new_content(driver):
    sign_in(driver, account_type="broadcast_create_user")

    landing_page = BasePage(driver)
    if not landing_page.text_is_on_page("Current alerts"):
        landing_page.click_element_by_link_text("Switch service")
        choose_service_page = BasePage(driver)
        choose_service_page.click_element_by_link_text(
            config["broadcast_service"]["service_name"]
        )
    else:
        dashboard_page = DashboardPage(driver)
        dashboard_page.click_element_by_link_text("Current alerts")

    # prepare alert
    current_alerts_page = BasePage(driver)
    test_uuid = str(uuid.uuid4())
    broadcast_title = "test broadcast" + test_uuid

    current_alerts_page.click_element_by_link_text("Create new alert")

    new_alert_page = BasePage(driver)
    new_alert_page.select_checkbox_or_radio(value="freeform")
    new_alert_page.click_continue()

    broadcast_freeform_page = BroadcastFreeformPage(driver)
    broadcast_content = "This is a test broadcast " + test_uuid
    broadcast_freeform_page.create_broadcast_content(broadcast_title, broadcast_content)
    broadcast_freeform_page.click_continue()

    prepare_alert_pages = BasePage(driver)
    prepare_alert_pages.click_element_by_link_text("Local authorities")
    prepare_alert_pages.click_element_by_link_text("Adur")
    prepare_alert_pages.select_checkbox_or_radio(value="wd23-E05007564")
    prepare_alert_pages.select_checkbox_or_radio(value="wd23-E05007565")
    prepare_alert_pages.click_continue()

    prepare_alert_pages.click_element_by_link_text(
        "Save and preview alert"
    )  # Remove once alert duration added back in
    # here check if selected areas displayed
    assert prepare_alert_pages.text_is_on_page("Cokeham")
    assert prepare_alert_pages.text_is_on_page("Eastbrook")

    # prepare_alert_pages.click_element_by_link_text("Continue")
    # prepare_alert_pages.select_checkbox_or_radio(value="PT30M")
    # prepare_alert_pages.click_continue()  # click "Preview alert"
    prepare_alert_pages.click_continue_to_submit()  # click "Submit for approval"
    assert prepare_alert_pages.text_is_on_page(
        f"{broadcast_title} is waiting for approval"
    )

    prepare_alert_pages.sign_out()

    # approve the alert
    sign_in(driver, account_type="broadcast_approve_user")

    landing_page = BasePage(driver)
    if not landing_page.text_is_on_page("Current alerts"):
        landing_page.click_element_by_link_text("Switch service")
        choose_service_page = BasePage(driver)
        choose_service_page.click_element_by_link_text(
            config["broadcast_service"]["service_name"]
        )
    else:
        dashboard_page = DashboardPage(driver)
        dashboard_page.click_element_by_link_text("Current alerts")

    current_alerts_page.click_element_by_link_text(broadcast_title)
    current_alerts_page.select_checkbox_or_radio(value="y")  # confirm approve alert
    current_alerts_page.click_continue()
    assert current_alerts_page.text_is_on_page("since today at")
    alert_page_url = current_alerts_page.current_url

    time.sleep(10)
    check_alert_is_published_on_govuk_alerts(
        driver, "Current alerts", broadcast_content
    )

    # get back to the alert page
    current_alerts_page.get(alert_page_url)

    # stop sending the alert
    current_alerts_page.click_element_by_link_text("Stop sending")
    current_alerts_page.click_continue()  # stop broadcasting
    assert current_alerts_page.text_is_on_page(
        "Stopped by Functional Tests - Broadcast User Approve"
    )
    current_alerts_page.click_element_by_link_text("Past alerts")
    past_alerts_page = BasePage(driver)
    assert past_alerts_page.text_is_on_page(broadcast_title)

    time.sleep(10)
    check_alert_is_published_on_govuk_alerts(driver, "Past alerts", broadcast_content)

    current_alerts_page.get()
    current_alerts_page.sign_out()


@pytest.mark.xdist_group(name=test_group_name)
def test_prepare_broadcast_with_template(driver):
    sign_in(driver, account_type="broadcast_create_user")

    go_to_templates_page(driver, service="broadcast_service")
    template_name = "test broadcast" + str(uuid.uuid4())
    content = "This is a test only."
    create_broadcast_template(driver, name=template_name, content=content)

    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service(
        service_id=config["broadcast_service"]["id"]
    )

    dashboard_page.click_element_by_link_text("Current alerts")

    current_alerts_page = BasePage(driver)
    current_alerts_page.click_element_by_link_text("Create new alert")

    new_alert_page = BasePage(driver)
    new_alert_page.select_checkbox_or_radio(value="template")
    new_alert_page.click_continue()

    templates_page = ShowTemplatesPage(driver)
    templates_page.click_template_by_link_text(template_name)

    templates_page.click_element_by_link_text("Save and get ready to send")

    prepare_alert_pages = BasePage(driver)
    prepare_alert_pages.click_element_by_link_text("Local authorities")
    prepare_alert_pages.click_element_by_link_text("Adur")
    prepare_alert_pages.select_checkbox_or_radio(value="wd23-E05007564")
    prepare_alert_pages.select_checkbox_or_radio(value="wd23-E05007565")
    prepare_alert_pages.click_continue()
    prepare_alert_pages.click_element_by_link_text(
        "Save and preview alert"
    )  # Remove once alert duration added back in
    # here check if selected areas displayed
    assert prepare_alert_pages.text_is_on_page("Cokeham")
    assert prepare_alert_pages.text_is_on_page("Eastbrook")

    # prepare_alert_pages.click_element_by_link_text("Continue")
    # prepare_alert_pages.select_checkbox_or_radio(value="PT30M")
    # prepare_alert_pages.click_continue()  # click "Preview alert"
    prepare_alert_pages.click_continue_to_submit()  # click "Submit for approval"
    assert prepare_alert_pages.text_is_on_page(
        f"{template_name} is waiting for approval"
    )

    prepare_alert_pages.click_element_by_link_text("Discard this alert")
    prepare_alert_pages.click_element_by_link_text("Rejected alerts")
    rejected_alerts_page = BasePage(driver)
    assert rejected_alerts_page.text_is_on_page(template_name)

    delete_template(driver, template_name, service="broadcast_service")

    current_alerts_page.get()
    current_alerts_page.sign_out()


@pytest.mark.xdist_group(name=test_group_name)
def test_create_and_then_reject_broadcast_using_the_api(driver, broadcast_client):
    sent_time = convert_naive_utc_datetime_to_cap_standard_string(
        datetime.utcnow() - timedelta(hours=1)
    )
    cancel_time = convert_naive_utc_datetime_to_cap_standard_string(datetime.utcnow())
    identifier = uuid.uuid4()
    event = f"test broadcast {identifier}"
    broadcast_content = f"Flood warning {identifier} has been issued"

    new_alert_xml = ALERT_XML.format(
        identifier=identifier,
        alert_sent=sent_time,
        event=event,
        broadcast_content=broadcast_content,
    )
    broadcast_client.post_broadcast_data(new_alert_xml)

    sign_in(driver, account_type="broadcast_approve_user")
    page = BasePage(driver)
    page.click_element_by_link_text("Current alerts")
    page.click_element_by_link_text(event)

    assert page.text_is_on_page(f"An API call wants to broadcast {event}")

    reject_broadcast_xml = CANCEL_XML.format(
        identifier=identifier,
        alert_sent=sent_time,
        cancel_sent=cancel_time,
        event=event,
    )
    broadcast_client.post_broadcast_data(reject_broadcast_xml)

    time.sleep(10)
    page.click_element_by_link_text("Rejected alerts")
    assert page.text_is_on_page(event)

    page.get()
    page.sign_out()


@pytest.mark.xdist_group(name=test_group_name)
def test_cancel_live_broadcast_using_the_api(driver, broadcast_client):
    sent_time = convert_naive_utc_datetime_to_cap_standard_string(
        datetime.utcnow() - timedelta(hours=1)
    )
    cancel_time = convert_naive_utc_datetime_to_cap_standard_string(datetime.utcnow())
    identifier = uuid.uuid4()
    event = f"test broadcast {identifier}"
    broadcast_content = f"Flood warning {identifier} has been issued"

    new_alert_xml = ALERT_XML.format(
        identifier=identifier,
        alert_sent=sent_time,
        event=event,
        broadcast_content=broadcast_content,
    )
    broadcast_client.post_broadcast_data(new_alert_xml)

    sign_in(driver, account_type="broadcast_approve_user")

    page = BasePage(driver)
    page.click_element_by_link_text("Current alerts")
    page.click_element_by_link_text(event)
    page.select_checkbox_or_radio(value="y")  # confirm approve alert
    page.click_continue()

    assert page.text_is_on_page("since today at")

    alert_page_url = page.current_url

    time.sleep(10)
    check_alert_is_published_on_govuk_alerts(
        driver, "Current alerts", broadcast_content
    )

    cancel_broadcast_xml = CANCEL_XML.format(
        identifier=identifier,
        alert_sent=sent_time,
        cancel_sent=cancel_time,
        event=event,
    )
    broadcast_client.post_broadcast_data(cancel_broadcast_xml)

    # go back to the page for the current alert
    time.sleep(10)
    page.get(alert_page_url)

    # assert that it's now cancelled
    assert page.text_is_on_page("Stopped by an API call")
    page.click_element_by_link_text("Past alerts")
    assert page.text_is_on_page(event)

    time.sleep(10)
    check_alert_is_published_on_govuk_alerts(driver, "Past alerts", broadcast_content)

    page.get()
    page.sign_out()


@pytest.mark.xdist_group(name=test_group_name)
def test_prepare_broadcast_with_new_content_for_postcode_area(driver):
    sign_in(driver, account_type="broadcast_create_user")

    landing_page = BasePage(driver)
    if not landing_page.text_is_on_page("Current alerts"):
        landing_page.click_element_by_link_text("Switch service")
        choose_service_page = BasePage(driver)
        choose_service_page.click_element_by_link_text(
            config["broadcast_service"]["service_name"]
        )
    else:
        dashboard_page = DashboardPage(driver)
        dashboard_page.click_element_by_link_text("Current alerts")

    # prepare alert
    current_alerts_page = BasePage(driver)
    test_uuid = str(uuid.uuid4())
    broadcast_title = "test broadcast" + test_uuid

    current_alerts_page.click_element_by_link_text("Create new alert")

    new_alert_page = BasePage(driver)
    new_alert_page.select_checkbox_or_radio(value="freeform")
    new_alert_page.click_continue()

    broadcast_freeform_page = BroadcastFreeformPage(driver)
    broadcast_content = "This is a test broadcast " + test_uuid
    broadcast_freeform_page.create_broadcast_content(broadcast_title, broadcast_content)
    broadcast_freeform_page.click_continue()

    prepare_alert_pages = BasePage(driver)
    prepare_alert_pages.click_element_by_link_text("Postcode areas")
    # This is where it varies
    search_postcode_page = SearchPostcodePage(driver)
    postcode_to_search = "BD1 1EE"
    radius_to_add = "5"
    search_postcode_page.create_custom_area(postcode_to_search, radius_to_add)
    search_postcode_page.click_search()
    # assert areas appear here

    search_postcode_page.click_preview()

    # here check if selected areas displayed
    assert prepare_alert_pages.text_is_on_page(
        "5km around the postcode BD1 1EE in Bradford"
    )
    prepare_alert_pages.click_continue_to_submit()  # click "Submit for approval"
    assert prepare_alert_pages.text_is_on_page(
        f"{broadcast_title} is waiting for approval"
    )

    prepare_alert_pages.sign_out()

    # approve the alert
    sign_in(driver, account_type="broadcast_approve_user")

    landing_page = BasePage(driver)
    if not landing_page.text_is_on_page("Current alerts"):
        landing_page.click_element_by_link_text("Switch service")
        choose_service_page = BasePage(driver)
        choose_service_page.click_element_by_link_text(
            config["broadcast_service"]["service_name"]
        )
    else:
        dashboard_page = DashboardPage(driver)
        dashboard_page.click_element_by_link_text("Current alerts")

    current_alerts_page.click_element_by_link_text(broadcast_title)
    current_alerts_page.select_checkbox_or_radio(value="y")  # confirm approve alert
    current_alerts_page.click_continue()
    assert current_alerts_page.text_is_on_page("since today at")
    alert_page_url = current_alerts_page.current_url

    time.sleep(10)
    check_alert_is_published_on_govuk_alerts(
        driver, "Current alerts", broadcast_content
    )

    # get back to the alert page
    current_alerts_page.get(alert_page_url)

    # stop sending the alert
    current_alerts_page.click_element_by_link_text("Stop sending")
    current_alerts_page.click_continue()  # stop broadcasting
    assert current_alerts_page.text_is_on_page(
        "Stopped by Functional Tests - Broadcast User Approve"
    )
    current_alerts_page.click_element_by_link_text("Past alerts")
    past_alerts_page = BasePage(driver)
    assert past_alerts_page.text_is_on_page(broadcast_title)

    time.sleep(10)
    check_alert_is_published_on_govuk_alerts(driver, "Past alerts", broadcast_content)

    current_alerts_page.get()
    current_alerts_page.sign_out()


@pytest.mark.xdist_group(name=test_group_name)
@pytest.mark.parametrize(
    "coordinate_type, post_data, expected_area_description",
    (
        (
            "easting_northing",
            {
                "first_coordinate": "416567",
                "second_coordinate": "432994",
                "radius": "3",
            },
            "3km around the easting of 416567 and the northing of 432994 in Bradford",
        ),
        (
            "easting_northing",
            {
                "first_coordinate": "419763",
                "second_coordinate": "456038",
                "radius": "5",
            },
            "5km around the easting of 419763 and the northing of 456038 in North Yorkshire",
        ),
        (
            "latitude_longitude",
            {"first_coordinate": "53.793", "second_coordinate": "-1.75", "radius": "3"},
            "3km around 53.793 latitude, -1.75 longitude in Bradford",
        ),
        (
            "latitude_longitude",
            {"first_coordinate": "54", "second_coordinate": "-1.7", "radius": "5"},
            "5km around 54.0 latitude, -1.7 longitude in North Yorkshire",
        ),
    ),
)
def test_prepare_broadcast_with_new_content_for_coordinate_area(
    driver, coordinate_type, post_data, expected_area_description
):
    sign_in(driver, account_type="broadcast_create_user")

    landing_page = BasePage(driver)
    if not landing_page.text_is_on_page("Current alerts"):
        landing_page.click_element_by_link_text("Switch service")
        choose_service_page = BasePage(driver)
        choose_service_page.click_element_by_link_text(
            config["broadcast_service"]["service_name"]
        )
    else:
        dashboard_page = DashboardPage(driver)
        dashboard_page.click_element_by_link_text("Current alerts")

    # prepare alert
    current_alerts_page = BasePage(driver)
    test_uuid = str(uuid.uuid4())
    broadcast_title = f"test broadcast{test_uuid}"

    current_alerts_page.click_element_by_link_text("Create new alert")

    new_alert_page = BasePage(driver)
    new_alert_page.select_checkbox_or_radio(value="freeform")
    new_alert_page.click_continue()

    broadcast_freeform_page = BroadcastFreeformPage(driver)
    broadcast_content = f"This is a test broadcast {test_uuid}"
    broadcast_freeform_page.create_broadcast_content(broadcast_title, broadcast_content)
    broadcast_freeform_page.click_continue()

    prepare_alert_pages = BasePage(driver)
    prepare_alert_pages.click_element_by_link_text("Coordinates")
    # This is where it varies
    choose_type_page = ChooseCoordinatesType(driver)
    choose_type_page.select_checkbox_or_radio(value=coordinate_type)
    choose_type_page.click_continue()

    choose_coordinate_area_page = ChooseCoordinateArea(driver)
    choose_coordinate_area_page.create_coordinate_area(
        post_data["first_coordinate"],
        post_data["second_coordinate"],
        post_data["radius"],
    )
    choose_coordinate_area_page.click_search()
    choose_coordinate_area_page.click_preview()

    # here check if selected areas displayed
    assert prepare_alert_pages.text_is_on_page(expected_area_description)

    prepare_alert_pages.click_continue_to_submit()  # click "Submit for approval"
    assert prepare_alert_pages.text_is_on_page(
        f"{broadcast_title} is waiting for approval"
    )

    prepare_alert_pages.sign_out()

    # approve the alert
    sign_in(driver, account_type="broadcast_approve_user")

    landing_page = BasePage(driver)
    if not landing_page.text_is_on_page("Current alerts"):
        landing_page.click_element_by_link_text("Switch service")
        choose_service_page = BasePage(driver)
        choose_service_page.click_element_by_link_text(
            config["broadcast_service"]["service_name"]
        )
    else:
        dashboard_page = DashboardPage(driver)
        dashboard_page.click_element_by_link_text("Current alerts")

    current_alerts_page.click_element_by_link_text(broadcast_title)
    current_alerts_page.select_checkbox_or_radio(value="y")  # confirm approve alert
    current_alerts_page.click_continue()
    assert current_alerts_page.text_is_on_page("since today at")
    alert_page_url = current_alerts_page.current_url

    time.sleep(10)
    check_alert_is_published_on_govuk_alerts(
        driver, "Current alerts", broadcast_content
    )

    # get back to the alert page
    current_alerts_page.get(alert_page_url)

    # stop sending the alert
    current_alerts_page.click_element_by_link_text("Stop sending")
    current_alerts_page.click_continue()  # stop broadcasting
    assert current_alerts_page.text_is_on_page(
        "Stopped by Functional Tests - Broadcast User Approve"
    )
    current_alerts_page.click_element_by_link_text("Past alerts")
    past_alerts_page = BasePage(driver)
    assert past_alerts_page.text_is_on_page(broadcast_title)

    time.sleep(10)
    check_alert_is_published_on_govuk_alerts(driver, "Past alerts", broadcast_content)

    current_alerts_page.get()
    current_alerts_page.sign_out()


@pytest.mark.xdist_group(name=test_group_name)
def test_reject_alert_with_reason(driver):
    sign_in(driver, account_type="broadcast_create_user")

    landing_page = BasePage(driver)
    if not landing_page.text_is_on_page("Current alerts"):
        landing_page.click_element_by_link_text("Switch service")
        choose_service_page = BasePage(driver)
        choose_service_page.click_element_by_link_text(
            config["broadcast_service"]["service_name"]
        )
    else:
        dashboard_page = DashboardPage(driver)
        dashboard_page.click_element_by_link_text("Current alerts")

    # prepare alert
    current_alerts_page = BasePage(driver)
    test_uuid = str(uuid.uuid4())
    broadcast_title = f"test broadcast{test_uuid}"

    current_alerts_page.click_element_by_link_text("Create new alert")

    new_alert_page = BasePage(driver)
    new_alert_page.select_checkbox_or_radio(value="freeform")
    new_alert_page.click_continue()

    broadcast_freeform_page = BroadcastFreeformPage(driver)
    broadcast_content = f"This is a test broadcast {test_uuid}"
    broadcast_freeform_page.create_broadcast_content(broadcast_title, broadcast_content)
    broadcast_freeform_page.click_continue()

    prepare_alert_pages = BasePage(driver)
    prepare_alert_pages.click_element_by_link_text("Local authorities")
    prepare_alert_pages.click_element_by_link_text("Adur")
    prepare_alert_pages.select_checkbox_or_radio(value="wd23-E05007564")
    prepare_alert_pages.select_checkbox_or_radio(value="wd23-E05007565")
    prepare_alert_pages.click_continue()

    prepare_alert_pages.click_element_by_link_text(
        "Save and preview alert"
    )  # Remove once alert duration added back in
    # here check if selected areas displayed
    assert prepare_alert_pages.text_is_on_page("Cokeham")
    assert prepare_alert_pages.text_is_on_page("Eastbrook")

    prepare_alert_pages.click_continue_to_submit()  # click "Submit for approval"
    assert prepare_alert_pages.text_is_on_page(
        f"{broadcast_title} is waiting for approval"
    )

    prepare_alert_pages.sign_out()

    # reject the alert
    sign_in(driver, account_type="broadcast_approve_user")

    landing_page = BasePage(driver)
    if not landing_page.text_is_on_page("Current alerts"):
        landing_page.click_element_by_link_text("Switch service")
        choose_service_page = BasePage(driver)
        choose_service_page.click_element_by_link_text(
            config["broadcast_service"]["service_name"]
        )
    else:
        dashboard_page = DashboardPage(driver)
        dashboard_page.click_element_by_link_text("Current alerts")

    current_alerts_page.click_element_by_link_text(broadcast_title)  # to access alert

    alert_page_with_rejection = RejectionForm(driver)
    assert alert_page_with_rejection.rejection_details_is_closed()
    alert_page_with_rejection.click_open_reject_detail()
    assert alert_page_with_rejection.rejection_details_is_open()

    # Without rejection reason
    rejection_reason = ""
    alert_page_with_rejection.click_reject_alert()

    # Assert errors appear
    assert (
        alert_page_with_rejection.get_rejection_form_errors()
        == "Error:\nEnter the reason for rejecting the alert"
    )

    # With rejection reason
    rejection_reason = "This is a test rejection reason."
    alert_page_with_rejection.create_rejection_reason_input(rejection_reason)
    alert_page_with_rejection.click_reject_alert()

    assert landing_page.text_is_on_page("Current alerts")
    landing_page.click_element_by_link_text("Rejected alerts")

    rejected_alerts_page = BasePage(driver)

    assert rejected_alerts_page.text_is_on_page(broadcast_title)
    assert rejected_alerts_page.text_is_on_page(rejection_reason)
    assert rejected_alerts_page.text_is_on_page(rejection_reason)
