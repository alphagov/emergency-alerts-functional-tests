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


@pytest.skip()
@pytest.mark.xdist_group(name=TESTSUITE_CODE)
def test_create_populate_and_delete_folders_and_templates(driver):
    sign_in(driver, account_type="broadcast_create_user")
    go_to_templates_page(driver)

    page = ShowTemplatesPage(driver)

    folder_name1 = f"Folder1 {datetime.now().replace(microsecond=0).isoformat()}"
    page.click_add_new_folder(folder_name=folder_name1)
    assert page.is_page_title("Templates")
    assert page.is_text_present_on_page(folder_name1)

    folder_name2 = f"Folder2 {datetime.now().replace(microsecond=0).isoformat()}"
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
