import time

import pytest
from selenium.webdriver.common.by import By

from config import config
from tests.pages import (
    DashboardPage,
    EditBroadcastTemplatePage,
    ManageFolderPage,
    ShowTemplatesPage,
    ViewFolderPage,
)
from tests.pages.rollups import sign_in
from tests.test_utils import go_to_templates_page

TESTSUITE_CODE = "TEMPLATES"


# @pytest.mark.xdist_group(name=TESTSUITE_CODE)
# def test_create_and_delete_template(driver):
#     sign_in(driver, account_type="broadcast_create_user")
#     go_to_templates_page(driver, service="broadcast_service")

#     page = ShowTemplatesPage(driver)
#     assert page.is_page_title("Templates")

#     timestamp = datetime.now().replace(microsecond=0).isoformat()
#     alert_name = f"Test Alert {timestamp}"
#     alert_content = "Test alert content"

#     page.click_add_new_template()
#     edit_template = EditBroadcastTemplatePage(driver)
#     assert edit_template.is_page_title("New template")
#     edit_template.create_template(name=alert_name, content=alert_content)

#     assert edit_template.is_page_title("Template")
#     assert edit_template.is_text_present_on_page(alert_name)
#     assert edit_template.is_text_present_on_page(alert_content)

#     edit_template.click_delete()

#     assert page.is_page_title("Templates")
#     assert not page.is_text_present_on_page(alert_name)


# @pytest.mark.xdist_group(name=TESTSUITE_CODE)
# def test_create_edit_and_delete_template(driver):
#     sign_in(driver, account_type="broadcast_create_user")
#     go_to_templates_page(driver, service="broadcast_service")

#     page = ShowTemplatesPage(driver)
#     assert page.is_page_title("Templates")

#     timestamp = datetime.now().replace(microsecond=0).isoformat()
#     alert_name = f"Test Alert {timestamp}"
#     alert_content = "Test alert content"

#     page.click_add_new_template()
#     edit_template = EditBroadcastTemplatePage(driver)
#     assert edit_template.is_page_title("New template")
#     edit_template.create_template(name=alert_name, content=alert_content)

#     assert edit_template.is_page_title("Template")
#     assert edit_template.is_text_present_on_page(alert_name)
#     assert edit_template.is_text_present_on_page(alert_content)

#     extra_text = " with some extra text"
#     edit_template.click_edit()
#     edit_template.create_template(name=alert_name, content=alert_content + extra_text)

#     assert edit_template.is_page_title("Template")
#     assert edit_template.is_text_present_on_page(alert_name)
#     assert edit_template.is_text_present_on_page(alert_content + extra_text)
#     assert edit_template.is_text_present_on_page("less than a minute ago")

#     edit_template.click_element_by_link_text("See previous versions")
#     assert edit_template.is_text_present_on_page(alert_content)
#     assert edit_template.is_text_present_on_page(alert_content + extra_text)

#     edit_template.click_element_by_link_text("Back to current templates")

#     templates = ShowTemplatesPage(driver)
#     templates.click_template_by_link_text(alert_name)

#     edit_template.click_delete()

#     assert page.is_page_title("Templates")
#     assert not page.is_text_present_on_page(alert_name)


@pytest.mark.xdist_group(name=TESTSUITE_CODE)
def test_create_prep_to_send_and_delete_template(driver):
    sign_in(driver, account_type="broadcast_create_user")
    go_to_templates_page(driver, service="broadcast_service")

    page = ShowTemplatesPage(driver)
    assert page.is_page_title("Templates")

    # timestamp = datetime.now().replace(microsecond=0).isoformat()
    timestamp = str(int(time.time()))
    alert_name = f"Test Alert {timestamp}"
    alert_content = "Test alert content"

    page.click_add_new_template()
    edit_template = EditBroadcastTemplatePage(driver)
    assert edit_template.is_page_title("New template")
    edit_template.create_template(name=alert_name, content=alert_content)

    assert edit_template.is_page_title("Template")
    assert edit_template.is_text_present_on_page(alert_name)
    assert edit_template.is_text_present_on_page(alert_content)

    edit_template.click_prep_to_send()
    assert edit_template.is_page_title("Choose where to send this alert")
    edit_template.click_templates()

    edit_template.click_element_by_link_text(alert_name)
    edit_template.click_delete()

    assert page.is_page_title("Templates")
    assert not page.is_text_present_on_page(alert_name)


@pytest.mark.xdist_group(name=TESTSUITE_CODE)
def test_creating_moving_and_deleting_template_folders(driver):
    sign_in(driver, account_type="broadcast_create_user")

    # create new template
    timestamp = str(int(time.time()))
    template_name = f"template-for-folder-test-{timestamp}"
    folder_name = f"test-folder-{timestamp}"

    dashboard_page = DashboardPage(driver)
    dashboard_page.go_to_dashboard_for_service(config["broadcast_service"]["id"])
    dashboard_page.click_templates()

    show_templates_page = ShowTemplatesPage(driver)
    show_templates_page.click_add_new_template()

    edit_template_page = EditBroadcastTemplatePage(driver)
    edit_template_page.create_template(name=template_name)
    template_id = edit_template_page.get_template_id()
    edit_template_page.click_templates()

    # create folder using add to new folder
    show_templates_page.select_template_checkbox(template_id)
    show_templates_page.add_to_new_folder(folder_name)

    # navigate into folder
    go_to_templates_page(driver, "broadcast_service")
    show_templates_page.click_template_by_link_text(folder_name)

    # rename folder step
    view_folder_page = ViewFolderPage(driver)
    view_folder_page.click_manage_folder()

    manage_folder_page = ManageFolderPage(driver)
    new_folder_name = folder_name + "-new"
    manage_folder_page.set_name(new_folder_name)
    view_folder_page.is_text_present_on_page(new_folder_name)

    # try to delete folder
    view_folder_page.click_manage_folder()
    manage_folder_page.delete_folder()  # fails due to not being empty

    # check error message visible
    assert (
        manage_folder_page.get_errors()
        == "You must empty this folder before you can delete it"
    )

    # move template out of folder
    view_folder_page.select_template_checkbox(template_id)
    view_folder_page.move_to_root_template_folder()

    # delete folder
    view_folder_page.click_manage_folder()
    manage_folder_page.delete_folder()
    manage_folder_page.confirm_delete_folder()
    current_folders = [
        x.text for x in driver.find_elements(By.CLASS_NAME, "template-list-item-label")
    ]
    if len(current_folders) == 0:
        current_folders = [
            x.text for x in driver.find_elements(By.CLASS_NAME, "message-name")
        ]
    # assert folder not visible
    assert new_folder_name not in current_folders

    # delete template
    show_templates_page.click_template_by_link_text(template_name)
    edit_template_page.click_delete()

    assert template_name not in [
        x.text for x in driver.find_elements(By.CLASS_NAME, "message-name")
    ]


# @pytest.mark.skip()
# @pytest.mark.xdist_group(name=TESTSUITE_CODE)
# def test_create_populate_and_delete_folders_and_templates_old(driver):
#     sign_in(driver, account_type="broadcast_create_user")
#     go_to_templates_page(driver, service="broadcast_service")

#     templates = ShowTemplatesPage(driver)
#     assert templates.is_page_title("Templates")
#     timestamp = datetime.now().replace(microsecond=0).isoformat()

#     folder_name1 = f"Folder1 {timestamp}"

#     templates.click_add_new_folder(folder_name=folder_name1)
#     assert templates.is_page_title("Templates")
#     assert templates.is_text_present_on_page(folder_name1)

#     folder_name2 = f"Folder2 {timestamp}"
#     templates.click_add_new_folder(folder_name=folder_name2)
#     assert templates.is_page_title("Templates")
#     assert templates.is_text_present_on_page(folder_name2)

#     new_template_page = EditBroadcastTemplatePage(driver)

#     # create new template 1
#     templates.click_add_new_template()
#     template1_name = f"Template1 {timestamp}"
#     new_template_page.create_template(name=template1_name, content="This is an alert")
#     template1_id = new_template_page.get_template_id()
#     new_template_page.click_element_by_link_text("Templates")

#     # move template to folder 1
#     templates.select_template_checkbox(template1_id)
#     templates.move_to_folder_level(1)
#     # assert template link is not on root
#     assert not templates.is_text_present_on_page(template1_name)

#     # create new template 2
#     templates.click_add_new_template()
#     template2_name = f"Template2 {timestamp}"
#     new_template_page.create_template(name=template2_name, content="This is an alert")
#     template2_id = new_template_page.get_template_id()
#     new_template_page.click_element_by_link_text("Templates")

#     # move template to folder 2
#     templates.select_template_checkbox(template2_id)
#     templates.move_to_folder_level(2)
#     # assert template link is not on root
#     assert not templates.is_text_present_on_page(template2_name)

#     # try to delete folder 1 - confirm failure

#     # try to delete folder 2 - confirm failure

#     # delete template 2

#     # delete folder 2

#     # delete template 1

#     # delete folder 1
