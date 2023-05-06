import logging

from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api._generated import BrowserType
from playwright.sync_api._generated import Page


logging.basicConfig(format="--- %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

PROXIES_POOL = False
BROWSER_TIMEOUT = 25 * 1000


# @retry_wraps()
def goto_url(url: str, page) -> None:
    logger.info(f"\nVisiting the url -> {url}")
    page.wait_for_load_state("networkidle")
    response = page.goto(url)
    if response.ok:
        logger.debug("Page Done Loading...")


def get_page_object(browser: BrowserType, proxies_pool: Optional[Generator] = None):
    if PROXIES_POOL:
        proxy = next(PROXIES_POOL)
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

page = get_page_object()
goto_url(ibba_homepage)


# "/find-a-business-broker/?place=oregon"
