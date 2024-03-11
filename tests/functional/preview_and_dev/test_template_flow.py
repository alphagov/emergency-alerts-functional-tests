from datetime import datetime

import pytest

from tests.pages import EditBroadcastTemplatePage, ShowTemplatesPage
from tests.pages.rollups import sign_in
from tests.test_utils import go_to_templates_page

TESTSUITE_CODE = "TEMPLATES"


@pytest.mark.xdist_group(name=TESTSUITE_CODE)
def test_create_and_delete_template(driver):
    sign_in(driver, account_type="broadcast_create_user")
    go_to_templates_page(driver)

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
    assert edit_template.is_text_present_on_page(alert_name)
    assert edit_template.is_text_present_on_page(alert_content)

    edit_template.click_delete()

    assert page.is_page_title("Templates")
    assert not page.is_text_present_on_page(alert_name)


@pytest.mark.xdist_group(name=TESTSUITE_CODE)
def test_create_edit_and_delete_template(driver):
    sign_in(driver, account_type="broadcast_create_user")
    go_to_templates_page(driver)

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
    assert edit_template.is_text_present_on_page(alert_name)
    assert edit_template.is_text_present_on_page(alert_content)

    extra_text = " with some extra text"
    edit_template.click_edit()
    edit_template.create_template(name=alert_name, content=alert_content + extra_text)

    assert edit_template.is_page_title("Template")
    assert edit_template.is_text_present_on_page(alert_name)
    assert edit_template.is_text_present_on_page(alert_content + extra_text)

    edit_template.click_delete()

    assert page.is_page_title("Templates")
    assert not page.is_text_present_on_page(alert_name)


@pytest.mark.skip("temporarily skip")
@pytest.mark.xdist_group(name=TESTSUITE_CODE)
def test_create_populate_and_delete_folders_and_templates(driver):
    sign_in(driver, account_type="broadcast_create_user")
    go_to_templates_page(driver)

    page = ShowTemplatesPage(driver)
    timestamp = datetime.now().replace(microsecond=0).isoformat()

    folder_name1 = f"Folder1 {timestamp}"
    page.click_add_new_folder(folder_name=folder_name1)
    assert page.is_page_title("Templates")
    assert page.is_text_present_on_page(folder_name1)

    folder_name2 = f"Folder2 {timestamp}"
    page.click_add_new_folder(folder_name=folder_name2)
    assert page.is_page_title("Templates")
    assert page.is_text_present_on_page(folder_name2)

    # create new template 1
    page.click_add_new_template()
    new_template_page = EditBroadcastTemplatePage(driver)
    new_template_page.create_template(name="Template1", content="This is an alert")
    new_template_page.click_element_by_link_text("Templates")

    # move template to folder 1

    # create new template 2

    # move template to folder 2

    # try to delete folder 1 - confirm failure

    # try to delete folder 2 - confirm failure

    # delete template 2

    # delete folder 2

    # delete template 1

    # delete folder 1
