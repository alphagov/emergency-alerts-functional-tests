import time
from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


class By:
    NAME = "name"
    CSS_SELECTOR = "css"
    ID = "id"
    TAG_NAME = "tag"
    CLASS_NAME = "class"
    LINK_TEXT = "link_text"
    PARTIAL_LINK_TEXT = "partial_link_text"
    XPATH = "xpath"


class NoSuchElementException(Exception):
    pass


class TimeoutException(Exception):
    pass


class StaleElementReferenceException(Exception):
    pass


class WebDriverException(Exception):
    pass


def _locator_to_selector(by, value):  # noqa: C901
    if by == By.NAME:
        return f"[name='{value}']"
    if by == By.CSS_SELECTOR:
        return value
    if by == By.ID:
        return f"#{value}"
    if by == By.TAG_NAME:
        return value
    if by == By.CLASS_NAME:
        return f".{value}"
    if by == By.LINK_TEXT:
        return f'a:has-text("{value}")'
    if by == By.PARTIAL_LINK_TEXT:
        return f'a:has-text("{value}")'
    if by == By.XPATH:
        return f"xpath={value}"
    # fallback to value
    return value


class ElementWrapper:
    def __init__(self, locator):
        self._locator = locator

    @property
    def element(self):
        return self._locator

    def click(self):
        self._locator.click()

    def get_attribute(self, name):
        return self._locator.get_attribute(name)

    @property
    def text(self):
        return self._locator.inner_text()

    def clear(self):
        # fill with empty string
        try:
            self._locator.fill("")
        except PlaywrightTimeoutError:
            pass

    def send_keys(self, value):
        # use fill to replace, then type to simulate slower entry
        try:
            self._locator.fill(value)
        except PlaywrightTimeoutError:
            self._locator.type(value)

    def __getattr__(self, item):
        # delegate to locator where possible
        return getattr(self._locator, item)


class WebDriverWait:
    def __init__(self, driver, timeout):
        self.driver = driver
        self.timeout = timeout

    def until(self, method, message=None):
        end_time = time.time() + self.timeout
        last_exc = None
        while True:
            try:
                value = method(self.driver)
                if value:
                    return value
            except Exception as e:
                last_exc = e
            if time.time() > end_time:
                raise TimeoutException(
                    message or "Timed out waiting for condition", last_exc
                )
            time.sleep(0.1)


class EC:
    @staticmethod
    def presence_of_element_located(locator):
        def _predicate(driver):
            el = driver.find_element(locator[0], locator[1])
            if el:
                return el
            return False

        return _predicate

    @staticmethod
    def visibility_of_element_located(locator):
        def _predicate(driver):
            el = driver.find_element(locator[0], locator[1])
            if el and el._locator.is_visible():
                return el
            return False

        return _predicate

    @staticmethod
    def visibility_of_all_elements_located(locator):
        def _predicate(driver):
            els = driver.find_elements(locator[0], locator[1])
            if els:
                # ensure at least one visible
                return els
            return False

        return _predicate

    @staticmethod
    def presence_of_all_elements_located(locator):
        def _predicate(driver):
            els = driver.find_elements(locator[0], locator[1])
            if els:
                return els
            return False

        return _predicate


class PlaywrightDriver:
    def __init__(self, headless=True, proxy=None, download_dir=None):
        self._pw = sync_playwright().start()
        launch_args = ["--no-sandbox"]
        self.browser = self._pw.chromium.launch(headless=headless, args=launch_args)
        context_args = {"accept_downloads": True}
        if proxy:
            context_args["proxy"] = {"server": proxy}
        # set downloads path if provided
        if download_dir:
            Path(download_dir).mkdir(parents=True, exist_ok=True)
            # Playwright python does not expose downloads_path param in some versions; ignore for now
        self.context = self.browser.new_context(**context_args)
        self.page = self.context.new_page()

    def get(self, url):
        self.page.goto(url)

    @property
    def current_url(self):
        return self.page.url

    @property
    def page_source(self):
        return self.page.content()

    def find_element(self, locator: tuple[By, str], timeout=3000):
        locator_obj = None
        if locator[0] == By.LINK_TEXT:
            locator_obj = self.page.get_by_role("link", name=locator[1])
        # Vibecoded
        else:
            selector = _locator_to_selector(locator[0], locator[1])
            locator_obj = self.page.locator(selector).first

        try:
            locator_obj.wait_for(state="attached", timeout=timeout)
            return ElementWrapper(locator_obj)
        except PlaywrightTimeoutError:
            raise NoSuchElementException(
                f"Could not find element {locator[0]} {locator[1]}"
            )

    def find_elements(self, by=None, value=None):
        selector = _locator_to_selector(by, value)
        locator = self.page.locator(selector)
        count = locator.count()
        return [ElementWrapper(locator.nth(i)) for i in range(count)]

    def execute_script(self, script, *args):
        handles = []
        for a in args:
            if isinstance(a, ElementWrapper):
                h = a._locator.element_handle()
                handles.append(h)
            else:
                handles.append(a)
        try:
            if "arguments[0]" in script:
                # convert to function with element as first arg
                func_name = ", ".join([f"arg{i}" for i in range(len(handles))])
                # replace arguments[0] with arg0
                new_script = script.replace("arguments[0]", "arg0")
                fn = f"({func_name}) => {{ {new_script} }}"
                return self.page.evaluate(fn, *handles)
            else:
                return self.page.evaluate(script)
        except Exception as e:
            raise WebDriverException(str(e))

    def delete_all_cookies(self):
        try:
            self.context.clear_cookies()
        except Exception:
            pass

    def refresh(self):
        self.page.reload()

    def set_window_size(self, w, h):
        try:
            self.page.set_viewport_size({"width": w, "height": h})
        except Exception:
            pass

    def save_screenshot(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.page.screenshot(path=path, full_page=True)

    def close(self):
        try:
            self.context.close()
            self.browser.close()
            self._pw.stop()
        except Exception:
            pass

    def start_tracing(self, screenshots=True, snapshots=True, sources=True):
        try:
            self.context.tracing.start(
                screenshots=screenshots, snapshots=snapshots, sources=sources
            )
        except Exception:
            pass

    def stop_tracing(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.context.tracing.stop(path=path)
