import time
import uuid
from datetime import datetime, timedelta, timezone

import pytest

from config import config
from tests.functional.preview_and_dev.sample_cap_xml import (
    ALERT_XML,
    CANCEL_XML,
)
from tests.pages import (
    BasePage,
    BroadcastDurationPage,
    BroadcastFreeformPage,
    CurrentAlertsPage,
    ShowTemplatesPage,
)
from tests.pages.pages import (
    ChooseCoordinateArea,
    ChooseCoordinatesType,
    ExtraContentPage,
    RejectionForm,
    ReturnAlertForEditForm,
    SearchFloodWarningAreaPage,
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

    # prepare alert
    current_alerts_page = BasePage(driver)
    test_uuid = str(uuid.uuid4())
    broadcast_title = "test broadcast " + test_uuid

    current_alerts_page.click_element_by_link_text("Create new alert")

    new_alert_page = BasePage(driver)
    new_alert_page.select_checkbox_or_radio(value="freeform")
    new_alert_page.click_continue()

    broadcast_freeform_page = BroadcastFreeformPage(driver)
    broadcast_content = "This is a test broadcast " + test_uuid
    broadcast_freeform_page.create_broadcast_content(broadcast_title, broadcast_content)
    broadcast_freeform_page.click_continue()

    # Choosing not to add extra_content
    choose_extra_content_page = BasePage(driver)
    choose_extra_content_page.select_checkbox_or_radio(value="no")
    choose_extra_content_page.click_continue()

    prepare_alert_pages = BasePage(driver)
    prepare_alert_pages.click_element_by_link_text("Local authorities")
    prepare_alert_pages.click_element_by_link_text("Adur")
    prepare_alert_pages.select_checkbox_or_radio(value="wd23-E05007564")
    prepare_alert_pages.select_checkbox_or_radio(value="wd23-E05007565")
    prepare_alert_pages.click_continue()
    prepare_alert_pages.click_element_by_link_text("Save and continue")

    broadcast_duration_page = BroadcastDurationPage(driver)
    broadcast_duration_page.set_alert_duration(hours="8", minutes="30")
    broadcast_duration_page.click_preview()  # Preview alert

    # check for selected areas and duration
    preview_alert_page = BasePage(driver)
    assert preview_alert_page.text_is_on_page("Cokeham")
    assert preview_alert_page.text_is_on_page("Eastbrook")
    assert preview_alert_page.text_is_on_page("8 hours, 30 minutes")

    preview_alert_page.click_submit_for_approval()  # click "Submit for approval"
    assert preview_alert_page.text_is_on_page(
        f"{broadcast_title} is waiting for approval"
    )

    preview_alert_page.sign_out()

    # approve the alert
    sign_in(driver, account_type="broadcast_approve_user")

    current_alerts_page.click_element_by_link_text(broadcast_title)
    current_alerts_page.select_checkbox_or_radio(value="y")  # confirm approve alert
    current_alerts_page.click_submit()
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
    current_alerts_page.click_submit()  # stop broadcasting
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
    create_broadcast_template(driver, reference=template_name, content=content)

    current_alerts_page = CurrentAlertsPage(driver)
    current_alerts_page.go_to_service_landing_page(
        service_id=config["broadcast_service"]["id"]
    )
    current_alerts_page.click_element_by_link_text("Current alerts")
    current_alerts_page.click_element_by_link_text("Create new alert")

    new_alert_page = BasePage(driver)
    new_alert_page.select_checkbox_or_radio(value="template")
    new_alert_page.click_continue()

    templates_page = ShowTemplatesPage(driver)
    templates_page.click_template_by_link_text(template_name)

    templates_page.click_element_by_link_text("Save and get ready to send")

    # Choosing not to add extra_content
    choose_extra_content_page = BasePage(driver)
    choose_extra_content_page.select_checkbox_or_radio(value="no")
    choose_extra_content_page.click_continue()

    prepare_alert_pages = BasePage(driver)
    prepare_alert_pages.click_element_by_link_text("Local authorities")
    prepare_alert_pages.click_element_by_link_text("Adur")
    prepare_alert_pages.select_checkbox_or_radio(value="wd23-E05007564")
    prepare_alert_pages.select_checkbox_or_radio(value="wd23-E05007565")
    prepare_alert_pages.click_continue()
    prepare_alert_pages.click_element_by_link_text("Save and continue")

    broadcast_duration_page = BroadcastDurationPage(driver)
    broadcast_duration_page.set_alert_duration(hours="8", minutes="30")
    broadcast_duration_page.click_preview()  # Preview alert

    # check for selected areas and duration
    preview_alert_page = BasePage(driver)
    assert prepare_alert_pages.text_is_on_page("Cokeham")
    assert prepare_alert_pages.text_is_on_page("Eastbrook")
    assert preview_alert_page.text_is_on_page("8 hours, 30 minutes")

    prepare_alert_pages.click_submit_for_approval()  # click "Submit for approval"
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
        datetime.now(timezone.utc) - timedelta(hours=1)
    )
    cancel_time = convert_naive_utc_datetime_to_cap_standard_string(
        datetime.now(timezone.utc)
    )
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
        datetime.now(timezone.utc) - timedelta(hours=1)
    )
    cancel_time = convert_naive_utc_datetime_to_cap_standard_string(
        datetime.now(timezone.utc)
    )
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
    page.click_element_by_link_text(event)
    page.select_checkbox_or_radio(value="y")  # confirm approve alert
    page.click_submit()

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

    # Choosing not to add extra_content
    choose_extra_content_page = BasePage(driver)
    choose_extra_content_page.select_checkbox_or_radio(value="no")
    choose_extra_content_page.click_continue()

    prepare_alert_pages = BasePage(driver)
    prepare_alert_pages.click_element_by_link_text("Postcode areas")
    # This is where it varies
    search_postcode_page = SearchPostcodePage(driver)
    postcode_to_search = "BD1 1EE"
    radius_to_add = "5"
    search_postcode_page.create_custom_area(postcode_to_search, radius_to_add)
    search_postcode_page.click_search()
    # assert areas appear here

    search_postcode_page.click_continue()

    broadcast_duration_page = BroadcastDurationPage(driver)
    broadcast_duration_page.set_alert_duration(hours="8", minutes="30")
    broadcast_duration_page.click_preview()  # Preview alert

    # here check if selected areas displayed
    preview_alert_page = BasePage(driver)
    assert preview_alert_page.text_is_on_page(
        "5km around the postcode BD1 1EE in Bradford"
    )
    assert preview_alert_page.text_is_on_page("8 hours, 30 minutes")

    preview_alert_page.click_submit_for_approval()  # click "Submit for approval"
    assert preview_alert_page.text_is_on_page(
        f"{broadcast_title} is waiting for approval"
    )

    preview_alert_page.sign_out()

    # approve the alert
    sign_in(driver, account_type="broadcast_approve_user")

    current_alerts_page.click_element_by_link_text(broadcast_title)
    current_alerts_page.select_checkbox_or_radio(value="y")  # confirm approve alert
    current_alerts_page.click_submit()
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
    current_alerts_page.click_submit()  # stop broadcasting
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
            "latitude_longitude",
            {"first_coordinate": "53.793", "second_coordinate": "-1.75", "radius": "3"},
            "3km around 53.793 latitude, -1.75 longitude in Bradford",
        ),
    ),
)
def test_prepare_broadcast_with_new_content_for_coordinate_area(
    driver, coordinate_type, post_data, expected_area_description
):
    sign_in(driver, account_type="broadcast_create_user")

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

    # Choosing not to add extra_content
    choose_extra_content_page = BasePage(driver)
    choose_extra_content_page.select_checkbox_or_radio(value="no")
    choose_extra_content_page.click_continue()

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
    choose_coordinate_area_page.click_continue()

    broadcast_duration_page = BroadcastDurationPage(driver)
    broadcast_duration_page.set_alert_duration(hours="8", minutes="30")
    broadcast_duration_page.click_preview()  # Preview alert

    # here check if selected areas displayed
    preview_alert_page = BasePage(driver)
    assert preview_alert_page.text_is_on_page(expected_area_description)
    assert preview_alert_page.text_is_on_page("8 hours, 30 minutes")

    preview_alert_page.click_submit_for_approval()  # click "Submit for approval"
    assert preview_alert_page.text_is_on_page(
        f"{broadcast_title} is waiting for approval"
    )

    preview_alert_page.sign_out()

    # approve the alert
    sign_in(driver, account_type="broadcast_approve_user")

    current_alerts_page.click_element_by_link_text(broadcast_title)
    current_alerts_page.select_checkbox_or_radio(value="y")  # confirm approve alert
    current_alerts_page.click_submit()
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
    current_alerts_page.click_submit()  # stop broadcasting
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
def test_prepare_broadcast_with_REPPIR_site(driver):
    sign_in(driver, account_type="broadcast_create_user")

    # prepare alert
    current_alerts_page = BasePage(driver)
    test_uuid = str(uuid.uuid4())
    broadcast_title = "test broadcast " + test_uuid

    current_alerts_page.click_element_by_link_text("Create new alert")

    new_alert_page = BasePage(driver)
    new_alert_page.select_checkbox_or_radio(value="freeform")
    new_alert_page.click_continue()

    broadcast_freeform_page = BroadcastFreeformPage(driver)
    broadcast_content = "This is a test broadcast " + test_uuid
    broadcast_freeform_page.create_broadcast_content(broadcast_title, broadcast_content)
    broadcast_freeform_page.click_continue()

    # Choosing not to add extra_content
    choose_extra_content_page = BasePage(driver)
    choose_extra_content_page.select_checkbox_or_radio(value="no")
    choose_extra_content_page.click_continue()

    prepare_alert_pages = BasePage(driver)
    prepare_alert_pages.click_element_by_link_text("REPPIR DEPZ sites")
    prepare_alert_pages.select_checkbox_or_radio(
        value="REPPIR_DEPZ_sites-awe_aldermaston"
    )
    prepare_alert_pages.click_continue()
    prepare_alert_pages.click_element_by_link_text("Save and continue")

    broadcast_duration_page = BroadcastDurationPage(driver)
    broadcast_duration_page.set_alert_duration(hours="8", minutes="30")
    broadcast_duration_page.click_preview()  # Preview alert

    # check for selected areas and duration
    preview_alert_page = BasePage(driver)
    assert preview_alert_page.text_is_on_page("AWE Aldermaston")
    assert preview_alert_page.text_is_on_page("8 hours, 30 minutes")

    preview_alert_page.click_submit_for_approval()  # click "Submit for approval"
    assert preview_alert_page.text_is_on_page(
        f"{broadcast_title} is waiting for approval"
    )

    preview_alert_page.sign_out()

    # approve the alert
    sign_in(driver, account_type="broadcast_approve_user")

    current_alerts_page.click_element_by_link_text(broadcast_title)
    current_alerts_page.select_checkbox_or_radio(value="y")  # confirm approve alert
    current_alerts_page.click_submit()
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
    current_alerts_page.click_submit()  # stop broadcasting
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
def test_prepare_broadcast_with_flood_warning_target_area(driver):
    sign_in(driver, account_type="broadcast_create_user")

    # prepare alert
    current_alerts_page = BasePage(driver)
    test_uuid = str(uuid.uuid4())
    broadcast_title = "test broadcast " + test_uuid

    current_alerts_page.click_element_by_link_text("Create new alert")

    new_alert_page = BasePage(driver)
    new_alert_page.select_checkbox_or_radio(value="freeform")
    new_alert_page.click_continue()

    broadcast_freeform_page = BroadcastFreeformPage(driver)
    broadcast_content = "This is a test broadcast " + test_uuid
    broadcast_freeform_page.create_broadcast_content(broadcast_title, broadcast_content)
    broadcast_freeform_page.click_continue()

    # Choosing not to add extra_content
    choose_extra_content_page = BasePage(driver)
    choose_extra_content_page.select_checkbox_or_radio(value="no")
    choose_extra_content_page.click_continue()

    prepare_alert_pages = BasePage(driver)
    prepare_alert_pages.click_element_by_link_text(
        "Flood Warning Target Areas (TA code)"
    )

    # Enter TA code and click 'Add area' button to add area to alert
    search_flood_warning_area_page = SearchFloodWarningAreaPage(driver)
    TA_code = "122FWB112"

    search_flood_warning_area_page.create_ta_code_input(TA_code)
    search_flood_warning_area_page.click_add_area()

    assert search_flood_warning_area_page.text_is_on_page(
        "122FWB112: Hull city centre"
    )  # Area has been returned and displayed correctly

    search_flood_warning_area_page.click_element_by_link_text(
        "Save and continue to preview"
    )

    broadcast_duration_page = BroadcastDurationPage(driver)
    broadcast_duration_page.set_alert_duration(hours="8", minutes="30")
    broadcast_duration_page.click_preview()  # Preview alert

    # check for selected areas and duration
    preview_alert_page = BasePage(driver)
    assert preview_alert_page.text_is_on_page("Hull city centre")
    assert preview_alert_page.text_is_on_page("8 hours, 30 minutes")

    preview_alert_page.click_submit_for_approval()  # click "Submit for approval"
    assert preview_alert_page.text_is_on_page(
        f"{broadcast_title} is waiting for approval"
    )

    preview_alert_page.sign_out()

    # approve the alert
    sign_in(driver, account_type="broadcast_approve_user")

    current_alerts_page.click_element_by_link_text(broadcast_title)
    current_alerts_page.select_checkbox_or_radio(value="y")  # confirm approve alert
    current_alerts_page.click_submit()
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
    current_alerts_page.click_submit()  # stop broadcasting
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

    # prepare alert
    current_alerts_page = BasePage(driver)
    test_uuid = str(uuid.uuid4())
    broadcast_title = f"test broadcast {test_uuid}"

    current_alerts_page.click_element_by_link_text("Create new alert")

    new_alert_page = BasePage(driver)
    new_alert_page.select_checkbox_or_radio(value="freeform")
    new_alert_page.click_continue()

    broadcast_freeform_page = BroadcastFreeformPage(driver)
    broadcast_content = f"This is a test broadcast {test_uuid}"
    broadcast_freeform_page.create_broadcast_content(broadcast_title, broadcast_content)
    broadcast_freeform_page.click_continue()

    # Choosing not to add extra_content
    choose_extra_content_page = BasePage(driver)
    choose_extra_content_page.select_checkbox_or_radio(value="no")
    choose_extra_content_page.click_continue()

    prepare_alert_pages = BasePage(driver)
    prepare_alert_pages.click_element_by_link_text("Local authorities")
    prepare_alert_pages.click_element_by_link_text("Adur")
    prepare_alert_pages.select_checkbox_or_radio(value="wd23-E05007564")
    prepare_alert_pages.select_checkbox_or_radio(value="wd23-E05007565")
    prepare_alert_pages.click_continue()
    prepare_alert_pages.click_element_by_link_text("Save and continue")

    broadcast_duration_page = BroadcastDurationPage(driver)
    broadcast_duration_page.set_alert_duration(hours="8", minutes="30")
    broadcast_duration_page.click_preview()  # Preview alert

    # check for selected areas and duration
    preview_alert_page = BasePage(driver)
    assert preview_alert_page.text_is_on_page("Cokeham")
    assert preview_alert_page.text_is_on_page("Eastbrook")
    assert preview_alert_page.text_is_on_page("8 hours, 30 minutes")

    preview_alert_page.click_submit_for_approval()  # click "Submit for approval"
    assert preview_alert_page.text_is_on_page(
        f"{broadcast_title} is waiting for approval"
    )

    preview_alert_page.sign_out()

    # reject the alert
    sign_in(driver, account_type="broadcast_approve_user")

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

    assert current_alerts_page.text_is_on_page("Current alerts")
    current_alerts_page.click_element_by_link_text("Rejected alerts")

    rejected_alerts_page = BasePage(driver)
    assert rejected_alerts_page.text_is_on_page(broadcast_title)
    assert rejected_alerts_page.text_is_on_page(rejection_reason)


@pytest.mark.xdist_group(name=test_group_name)
def test_return_alert_for_edit(driver):
    sign_in(driver, account_type="broadcast_create_user")

    # prepare alert
    current_alerts_page = BasePage(driver)
    test_uuid = str(uuid.uuid4())
    broadcast_title = f"test broadcast {test_uuid}"

    current_alerts_page.click_element_by_link_text("Create new alert")

    new_alert_page = BasePage(driver)
    new_alert_page.select_checkbox_or_radio(value="freeform")
    new_alert_page.click_continue()

    broadcast_freeform_page = BroadcastFreeformPage(driver)
    broadcast_content = f"This is a test broadcast {test_uuid}"
    broadcast_freeform_page.create_broadcast_content(broadcast_title, broadcast_content)
    broadcast_freeform_page.click_continue()

    # Choosing not to add extra_content
    choose_extra_content_page = BasePage(driver)
    choose_extra_content_page.select_checkbox_or_radio(value="no")
    choose_extra_content_page.click_continue()

    prepare_alert_pages = BasePage(driver)
    prepare_alert_pages.click_element_by_link_text("Local authorities")
    prepare_alert_pages.click_element_by_link_text("Adur")
    prepare_alert_pages.select_checkbox_or_radio(value="wd23-E05007564")
    prepare_alert_pages.select_checkbox_or_radio(value="wd23-E05007565")
    prepare_alert_pages.click_continue()
    prepare_alert_pages.click_element_by_link_text("Save and continue")

    broadcast_duration_page = BroadcastDurationPage(driver)
    broadcast_duration_page.set_alert_duration(hours="8", minutes="30")
    broadcast_duration_page.click_preview()  # Preview alert

    # check for selected areas and duration
    preview_alert_page = BasePage(driver)
    assert preview_alert_page.text_is_on_page("Cokeham")
    assert preview_alert_page.text_is_on_page("Eastbrook")
    assert preview_alert_page.text_is_on_page("8 hours, 30 minutes")

    preview_alert_page.click_submit_for_approval()  # click "Submit for approval"
    assert preview_alert_page.text_is_on_page(
        f"{broadcast_title} is waiting for approval"
    )

    preview_alert_page.sign_out()

    # Return the alert for edit
    sign_in(driver, account_type="broadcast_approve_user")

    current_alerts_page.click_element_by_link_text(broadcast_title)  # to access alert

    alert_page_with_return_for_edit = ReturnAlertForEditForm(driver)
    assert alert_page_with_return_for_edit.return_for_edit_details_is_closed()
    alert_page_with_return_for_edit.click_open_return_for_edit_detail()
    assert alert_page_with_return_for_edit.return_for_edit_details_is_open()

    # Without rejection reason
    reason_for_returning_alert = ""
    alert_page_with_return_for_edit.create_return_for_edit_reason_input(
        reason_for_returning_alert
    )
    alert_page_with_return_for_edit.click_return_alert_for_edit()

    # Assert errors appear
    assert (
        alert_page_with_return_for_edit.get_return_for_edit_form_errors()
        == "Error:\nEnter the reason for returning the alert for edit"
    )

    # With reason for returning alert for edit
    reason_for_returning_alert = (
        "This is a test reason for returning the alert for edit."
    )
    alert_page_with_return_for_edit.create_return_for_edit_reason_input(
        reason_for_returning_alert
    )
    alert_page_with_return_for_edit.click_return_alert_for_edit()
    assert (
        f"This alert has been returned to edit, because: {reason_for_returning_alert}"
        in alert_page_with_return_for_edit.get_returned_banner_text()
    )
    assert alert_page_with_return_for_edit.text_is_on_page(
        "Submitted by Functional Tests - Broadcast User Create"
    )
    assert alert_page_with_return_for_edit.text_is_on_page(
        "Returned by Functional Tests - Broadcast User Approve"
    )

    assert current_alerts_page.text_is_on_page("Current alerts")
    assert current_alerts_page.text_is_on_page(broadcast_title)


@pytest.mark.xdist_group(name=test_group_name)
def test_prepare_broadcast_with_extra_content(driver):
    sign_in(driver, account_type="broadcast_create_user")

    # prepare alert
    current_alerts_page = BasePage(driver)
    test_uuid = str(uuid.uuid4())
    broadcast_title = "test broadcast " + test_uuid

    current_alerts_page.click_element_by_link_text("Create new alert")

    new_alert_page = BasePage(driver)
    new_alert_page.select_checkbox_or_radio(value="freeform")
    new_alert_page.click_continue()

    broadcast_freeform_page = BroadcastFreeformPage(driver)
    broadcast_content = "This is a test broadcast " + test_uuid
    broadcast_freeform_page.create_broadcast_content(broadcast_title, broadcast_content)
    broadcast_freeform_page.click_continue()

    # Choosing to add exra_content to alert
    choose_extra_content_page = BasePage(driver)
    choose_extra_content_page.select_checkbox_or_radio(value="yes")
    choose_extra_content_page.click_continue()

    # Adding extra_content to textarea and submitting
    add_extra_content_page = ExtraContentPage(driver)
    extra_content = "This is extra content " + test_uuid
    add_extra_content_page.create_extra_content(extra_content)
    add_extra_content_page.click_continue()

    prepare_alert_pages = BasePage(driver)
    prepare_alert_pages.click_element_by_link_text("Countries")
    prepare_alert_pages.select_checkbox_or_radio(value="ctry19-W92000004")
    prepare_alert_pages.click_continue()
    prepare_alert_pages.click_element_by_link_text("Save and continue")

    broadcast_duration_page = BroadcastDurationPage(driver)
    broadcast_duration_page.set_alert_duration(hours="8", minutes="30")
    broadcast_duration_page.click_preview()  # Preview alert

    # check for selected areas and duration
    preview_alert_page = BasePage(driver)
    assert preview_alert_page.text_is_on_page("Wales")
    assert preview_alert_page.text_is_on_page("8 hours, 30 minutes")

    preview_alert_page.click_submit_for_approval()  # click "Submit for approval"
    assert preview_alert_page.text_is_on_page(
        f"{broadcast_title} is waiting for approval"
    )

    preview_alert_page.sign_out()

    # approve the alert
    sign_in(driver, account_type="broadcast_approve_user")

    current_alerts_page.click_element_by_link_text(broadcast_title)
    current_alerts_page.select_checkbox_or_radio(value="y")  # confirm approve alert
    current_alerts_page.click_submit()
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
    current_alerts_page.click_submit()  # stop broadcasting
    assert current_alerts_page.text_is_on_page(
        "Stopped by Functional Tests - Broadcast User Approve"
    )
    current_alerts_page.click_element_by_link_text("Past alerts")
    past_alerts_page = BasePage(driver)
    assert past_alerts_page.text_is_on_page(broadcast_title)

    time.sleep(10)
    check_alert_is_published_on_govuk_alerts(
        driver, "Past alerts", broadcast_content, extra_content
    )

    current_alerts_page.get()
    current_alerts_page.sign_out()
