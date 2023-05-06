import logging
import functools
from typing import Optional
from typing import Generator
from typing import Callable

from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api._generated import BrowserType
from playwright.sync_api._generated import Page


logging.basicConfig(format=".. %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

BROWSER_TIMEOUT = 25 * 1000


def retry_wraps(times: int = 3) -> Callable:
    def retry(function: Callable) -> Callable:
        """tries to run a function after an unsuccessful attempt."""

        @functools.wraps(function)
        def inner(*args, **kwargs):
            for _ in range(times):
                try:
                    return function(*args, **kwargs)
                except Exception as err:
                    logger.error(err)

        return inner

    return retry


# @retry_wraps()
def goto_url(url: str, page: Page, page_load_state: str = "load") -> None:
    logger.info(f"Visiting the url -> {url}")
    page.wait_for_load_state(page_load_state)
    response = page.goto(url)
    if response.ok:
        logger.debug("Page Done Loading...")


def get_page_object(browser: BrowserType, proxies_pool: Optional[Generator] = None):
    if proxies_pool:
        proxy = next(proxies_pool)
        proxy_dict = {
            "server": f"http://{proxy.get('host').strip()}:{proxy.get('port').strip()}"
        }

        if len(proxy) == 4:
            proxy_dict["username"] = proxy.get("username").strip()
            proxy_dict["password"] = proxy.get("password").strip()
        context = browser.new_context(proxy=proxy_dict)
    else:
        context = browser.new_context()

    page = context.new_page()
    page.set_default_timeout(BROWSER_TIMEOUT)
    page.set_default_navigation_timeout(BROWSER_TIMEOUT)
    return page


playwright = sync_playwright().start()
browser = playwright.chromium.launch(headless=False, slow_mo=400)


ibba_homepage = "https://www.ibba.org"

page = get_page_object(browser)
# goto_url(ibba_homepage, page)


place = "oregon"

place_uri = f"/find-a-business-broker/?place={place.lower()}"
goto_url(ibba_homepage + place_uri, page)
