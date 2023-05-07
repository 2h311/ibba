import re
import logging
import functools
from queue import Queue
from typing import Callable
from typing import Optional
from typing import Generator

from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api._generated import Page
from playwright.sync_api._generated import BrowserType
from playwright.sync_api._generated import ElementHandle


logging.basicConfig(format=".. %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

BROWSER_TIMEOUT = 42 * 1000


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
    print(page_load_state)
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


def get_text_from_page_element(page_element: ElementHandle) -> str:
	return page_element.text_content().strip()


playwright = sync_playwright().start()
browser = playwright.chromium.launch(headless=False, slow_mo=400)


ibba_homepage = "https://www.ibba.org"

page = get_page_object(browser)
# goto_url(ibba_homepage, page)


place = "mississippi"
place_uri = f"/find-a-business-broker/?place={place.lower()}"
goto_url(ibba_homepage + place_uri, page, "domcontentloaded")


site_content_container = page.wait_for_selector("div#content")
listing_container = site_content_container.query_selector("div#listings")

h5_text = listing_container.wait_for_selector("h5").text_content()
total_number_of_brokers = int(re.search(r"\d+", h5_text).group())
logger.info(h5_text)


brokers = listing_container.query_selector_all("div.broker-block")
assert len(brokers) == total_number_of_brokers


broker_queue = Queue()
for broker in brokers:
	broker_profile_href = broker.query_selector("a").get_attribute("href")
	broker_name = broker.query_selector("h3").text_content()
	logger.info(f"Name: {broker_name}")
	logger.info(f"Profile Page: {broker_profile_href}")
	broker_queue.put(broker_profile_href)
assert broker_queue.qsize() == total_number_of_brokers



# while not broker_queue.empty():
profile_url = broker_queue.get()
goto_url(profile_url, page)


broker_profile_image_link = page.query_selector("div.brokers__profile--image img").get_attribute("src")


profile_information = page.query_selector("div.brokers__profile--information")
profile_information_name = profile_information.query_selector("h1.brokers__profile--informationName")
broker_name = get_text_from_page_element(profile_information_name)


broker_is_cbi = "No"
top_cbi = profile_information.query_selector_all("span.brokers__item--topCBI")
if top_cbi:
	text = get_text_from_page_element(top_cbi[-1])
	if text == "CBI":
		broker_is_cbi = "Yes"


member_date = page.query_selector("div.brokers__profile--memberDate")
broker_member_date = get_text_from_page_element(member_date)


# # tel = left_phone[0].query_selector("span > a").get_attribute("href")
# # broker_phone = tel.lstrip("tel:")
# # email = left_phone[1].query_selector("a").get_attribute("href")


left_phone = page.query_selector_all("div.brokers__profile--leftPhone > a")
broker_phone = get_text_from_page_element(left_phone[0])
broker_email = get_text_from_page_element(left_phone[1])


city = page.query_selector("div.brokers__profile--leftCity")
broker_city = get_text_from_page_element(city).replace("\n", "")


address = page.query_selector("div.brokers__profile--leftAddress")
broker_address = get_text_from_page_element(address).lstrip("apartment ")


broker_website = ""
left_links = page.query_selector_all("div.brokers__profile--leftLink > a")
for link in left_links:
	value = link.get_property("target").json_value()
	if value:
		broker_website = link.get_attribute("href")
		break


speciality = page.query_selector("ul.brokers__profile--leftSpeciality")
broker_speciality = ",".join([element.text_content().strip() for element in speciality.query_selector_all("li") ])


