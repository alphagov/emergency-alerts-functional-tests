import time
from datetime import datetime

import pytest
from selenium.webdriver.common.by import By

from config import config

# from config import config
from tests.pages import (
    DashboardPage,
    EditBroadcastTemplatePage,
    InviteUserPage,
    ManageFolderPage,
    ShowTemplatesPage,
    TeamMembersPage,
    ViewFolderPage,
)
from tests.pages.rollups import sign_in
from tests.test_utils import go_to_templates_page

test_group_name = "templates"


@pytest.mark.xdist_group(name=test_group_name)
def test_create_and_delete_template(driver):
    sign_in(driver, account_type="broadcast_create_user")
    go_to_templates_page(driver, service="broadcast_service")

    page = ShowTemplatesPage(driver)
    assert page.is_page_title("Templates")

    timestamp = datetime.now().replace(microsecond=0).isoformat()
    alert_name = f"Test Alert {timestamp}"
    alert_content = "Test alert content"

    page.click_add_new_template()
    edit_template = EditBroadcastTemplatePage(driver)
    assert edit_template.is_page_title("New template")
    edit_template.create_template(name=alert_name, content=alert_content)

    assert edit_template.is_page_title("Template")
    assert edit_template.text_is_on_page(alert_name)
    assert edit_template.text_is_on_page(alert_content)

    edit_template.click_delete()

    assert page.is_page_title("Templates")
    assert not page.text_is_on_page(alert_name)


@pytest.mark.xdist_group(name=test_group_name)
def test_create_edit_and_delete_template(driver):
    sign_in(driver, account_type="broadcast_create_user")
    go_to_templates_page(driver, service="broadcast_service")

    page = ShowTemplatesPage(driver)
    assert page.is_page_title("Templates")

    timestamp = datetime.now().replace(microsecond=0).isoformat()
    alert_name = f"Test Alert {timestamp}"
    alert_content = "Test alert content"

    page.click_add_new_template()
    edit_template = EditBroadcastTemplatePage(driver)
    assert edit_template.is_page_title("New template")
    edit_template.create_template(name=alert_name, content=alert_content)

    assert edit_template.is_page_title("Template")
    assert edit_template.text_is_on_page(alert_name)
    assert edit_template.text_is_on_page(alert_content)

    extra_text = " with some extra text"
    edit_template.click_edit()
    edit_template.create_template(name=alert_name, content=alert_content + extra_text)

    assert edit_template.is_page_title("Template")
    assert edit_template.text_is_on_page(alert_name)
    assert edit_template.text_is_on_page(alert_content + extra_text)
    assert edit_template.text_is_on_page("less than a minute ago")

    edit_template.click_element_by_link_text("See previous versions")
    assert edit_template.text_is_on_page(alert_content)
    assert edit_template.text_is_on_page(alert_content + extra_text)

    edit_template.click_element_by_link_text("Back to current templates")

    templates = ShowTemplatesPage(driver)
    templates.click_template_by_link_text(alert_name)

    edit_template.click_delete()

    assert page.is_page_title("Templates")
    assert not page.text_is_on_page(alert_name)


@pytest.mark.xdist_group(name=test_group_name)
def test_create_prep_to_send_and_delete_template(driver):
    sign_in(driver, account_type="broadcast_create_user")
    go_to_templates_page(driver, service="broadcast_service")

    page = ShowTemplatesPage(driver)
    assert page.is_page_title("Templates")

    timestamp = str(int(time.time()))
    alert_name = f"Test Alert {timestamp}"
    alert_content = "Test alert content"

    page.click_add_new_template()
    edit_template = EditBroadcastTemplatePage(driver)
    assert edit_template.is_page_title("New template")
    edit_template.create_template(name=alert_name, content=alert_content)

    assert edit_template.is_page_title("Template")
    assert edit_template.text_is_on_page(alert_name)
    assert edit_template.text_is_on_page(alert_content)

    edit_template.click_prep_to_send()
    assert edit_template.is_page_title("Choose where to send this alert")
    edit_template.click_templates()

    edit_template.click_element_by_link_text(alert_name)
    edit_template.click_delete()

    assert page.is_page_title("Templates")
    assert not page.text_is_on_page(alert_name)


@pytest.mark.xdist_group(name=test_group_name)
def test_creating_moving_and_deleting_template_folders(driver):
    sign_in(driver, account_type="broadcast_create_user")

    # create new template
    timestamp = str(int(time.time()))
    template_name = f"template-for-folder-test-{timestamp}"
    folder_name = f"test-folder-{timestamp}"

    go_to_templates_page(driver, "broadcast_service")
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
    view_folder_page.text_is_on_page(new_folder_name)

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
    go_to_templates_page(driver, "broadcast_service")
    view_folder_page.click_template_by_link_text(new_folder_name)
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


@pytest.mark.xdist_group(name=test_group_name)
def test_template_folder_permissions(driver):
    sign_in(driver, account_type="broadcast_create_user")

    timestamp = str(int(time.time()))
    folder_names = [
        "test-parent-folder-{}".format(timestamp),
        "test-child-folder-{}".format(timestamp),
        "test-grandchild-folder-{}".format(timestamp),
    ]
    go_to_templates_page(driver, "broadcast_service")

    show_templates_page = ShowTemplatesPage(driver)

    # a loop to create a folder structure with parent folder, child folder and grandchild folder,
    for folder_name in folder_names:
        show_templates_page.click_add_new_folder(folder_name)
        show_templates_page.click_template_by_link_text(folder_name)

    edit_template_page = EditBroadcastTemplatePage(driver)

    # create one template for each folder
    for i, folder_name in enumerate(folder_names):
        template_name = folder_name + "-template"

        show_templates_page.click_add_new_template()
        edit_template_page.create_template(name=template_name)

        show_templates_page.click_templates()
        show_templates_page.check_input_with_label_text(
            text=template_name, input_type="checkbox"
        )
        show_templates_page.move_template_to_folder(folder_name)

    show_templates_page.sign_out()

    # go to Team members page
    sign_in(driver, account_type="platform_admin")
    dashboard_page = DashboardPage(driver)
    dashboard_page.click_team_members_link()
    team_members_page = TeamMembersPage(driver)

    # edit colleague's permissions so child folder is invisible
    team_members_page.click_edit_team_member(
        config["broadcast_service"]["broadcast_user_2"]["email"]
    )
    edit_team_member_page = InviteUserPage(driver)
    edit_team_member_page.uncheck_folder_permission_checkbox(folder_names[1])
    edit_team_member_page.click_save()

    # check if permissions saved correctly
    dashboard_page.click_team_members_link()
    team_members_page.click_edit_team_member(
        config["broadcast_service"]["broadcast_user_2"]["email"]
    )
    assert not edit_team_member_page.is_checkbox_checked(folder_names[1])

    dashboard_page.sign_out()

    # log in as that colleague
    sign_in(driver, account_type="broadcast_approve_user")
    go_to_templates_page(driver, "broadcast_service")

    # click through, see that child folder invisible
    show_templates_page.click_template_by_link_text(folder_names[0])
    child_folder = show_templates_page.get_folder_by_name(folder_names[1])
    name_of_folder_with_invisible_parent = folder_names[1] + " " + folder_names[2]
    assert child_folder.text == name_of_folder_with_invisible_parent

    # grandchild folder has folder path as a name
    show_templates_page.click_template_by_link_text(
        name_of_folder_with_invisible_parent
    )

    # click grandchild folder template to see that it's there
    show_templates_page.click_template_by_link_text(folder_names[2] + "-template")
    dashboard_page.sign_out()

    # delete everything
    sign_in(driver, account_type="broadcast_create_user")
    go_to_templates_page(driver, "broadcast_service")
    show_templates_page = ShowTemplatesPage(driver)
    show_templates_page.click_template_by_link_text(folder_names[0])

    view_folder_page = ViewFolderPage(driver)
    view_folder_page.click_template_by_link_text(folder_names[1])
    view_folder_page.click_template_by_link_text(folder_names[2])

    for folder_name in reversed(folder_names):
        view_folder_page.click_template_by_link_text(folder_name + "-template")
        template_page = EditBroadcastTemplatePage(driver)
        template_page.click_delete()

        view_folder_page.click_manage_folder()
        manage_folder_page = ManageFolderPage(driver)
        manage_folder_page.delete_folder()
        manage_folder_page.confirm_delete_folder()
