from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
from enum import Enum
# import time


class TableHTML(Enum):
    """
    The class contains variables that describe the structure of the table to be scraped
    """
    HEADER_AND_ABOVE = 3  # table header and content above has 3 `tr` tags
    PAGE_NAV = 2  # page navigation bar has 2 `tr` tags
    CONTENT_AND_PAGE_NAV = 12  # maximum table content plus page navigation bar has 12 `tr` tags
    HEADER_ROW_POSITION = 2  # the 3rd 'tr' tag in table tag
    PAGE_ROW_POSITION = -1  # the last 'tr' tag in table tag contains the page nav
    CLICK_BUTTON_POSITION = -1  # the last 'td` tag in the last `tr` tag of the table


class Element(Enum):
    """
    The class contains variables that describe different attributes of web elements to be located
    """
    BUILDING_TAB_XPATH = '//*[@title="Building"]'
    DATE_FROM_XPATH = '//*[@id="ctl00_PlaceHolderMain_generalSearchForm_txtGSStartDate"]'
    SEARCH_BUTTON_XPATH = '//*[@id="ctl00_PlaceHolderMain_btnNewSearch"]'
    TABLE_ID = 'ctl00_PlaceHolderMain_dgvPermitList_gdvPermitList'


def wait_for_staleness(driver, element_id, timeout=10):
    """
    The function waits until the old web element detaches the DOM after loading a new page. Otherwise, the script won't
    get the new element and the function raises TimeOut Exception.
    :param driver: the web driver in use
    :param element_id: the id of the web element to be inspected
    :param timeout: wait a timeout period of time for the web element to detach the DOM, defaulted to 10 seconds.
    :return: raise exceptions and exit or no returns
    """
    try:
        WebDriverWait(driver, timeout).until(
            EC.staleness_of(driver.find_element_by_id(element_id))
        )
    except Exception as e:
        print(e)
        exit(1)


def wait_for_page_load(driver: webdriver, by_method: By, method_val: str, timeout=10) -> webdriver:
    """
    The function waits until the expected web element presented in the page to proceed to next
    :param driver: the web driver in use
    :param by_method: a `By` object used to locate the desired web element in by different method
    :param method_val: the values of the `By` method
    :param timeout: wait a timeout period of time for the web element to be presented in the page,
                    defaulted to 10 seconds.
    :return: raise exceptions or return the element be waited on
    """
    try:
        element = WebDriverWait(driver, timeout).until(
           EC.presence_of_element_located((by_method, method_val))
        )
    except Exception as e:
        print(e)
        exit(1)
    else:
        return element


def get_table(driver: webdriver, table_id: str) -> list:
    """
    The function gets the table to be scraped by `talbe_id`.
    Tips: after loading a new page, use `wait_for_staleness()` to wait until the old web element to detach the DOM
        to grab the new element. In case `wait_for_staleness()` not working, use `time.sleep()` in below instead.
    :param driver: the web driver in use
    :param table_id: the `id` of the `table` element to be scraped
    :return: function returns a list of row elements int the table, represented by `tr` tags
    """
    # time.sleep(3)
    element = wait_for_page_load(driver, By.ID, table_id)
    table_rows = element.find_elements_by_tag_name('tr')
    return table_rows


def get_headers(rows: list) -> list:
    """
    Get the headers of the table to be scraped
    :param rows: rows of the table, usually presented in the code as `tr` tags
    :return: returns a list of table header texts
    """
    headers = []
    headers_code = rows[TableHTML.HEADER_ROW_POSITION.value]
    headers_text = headers_code.find_elements_by_tag_name("span")
    for header in headers_text:
        val = header.text.strip()
        if val not in [None, '']:
            headers.append(val)
    headers.append('entrydate')
    return headers


def scrape_content(headers: list, content_rows: list) -> list:
    """
    Get the content of the table
    :param headers: table header
    :param content_rows: row elements of the table content, usually presented as `tr` tags
    :return: returns a list of permit object in dictionary type
    """
    objs = []
    for row in content_rows:
        cells = row.find_elements_by_tag_name('span')
        vals = []
        for cell in cells:
            val = cell.text.strip()
            vals.append(val)
        vals.append(datetime.now())
        obj = dict(zip(headers, vals))
        objs.append(obj)
    return objs


def click_next(page_row) -> bool:
    """
    The function clicks the `next` button located in the lower right conner of the page to get table content
    in the next page. The function also returns the clickability of the next button to determine if at the last page.
    :param page_row: the row element contains the page navigation bar in html
    :return: return if the next button is still clickable
    """
    next_button = page_row.find_elements_by_tag_name('td')[TableHTML.CLICK_BUTTON_POSITION.value]
    try:
        next_button.find_element_by_tag_name('a').click()
    except Exception as e:
        return False
    else:
        return True


def scraper_atlanta(chrome_path: str,
                    url='https://aca3.accela.com/Atlanta_Ga/Welcome.aspx',
                    days_to_scrape=1) -> dict:
    """
    The actual scraping process.
    :param chrome_path: the path in the system where `chromedriver` is stored
    :param url: the url of the website to be scraped
    :param days_to_scrape: days prior to today to start scraping. 1 means from yesterday to today, 2 days in total.
           The value is defaulted to 2 days.
    :return: The function returns a list of permit object in JSON-like style.
    """
    driver = webdriver.Chrome(chrome_path)
    driver.get(url)

    # Start the browser
    driver.find_element_by_xpath(Element.BUILDING_TAB_XPATH.value).click()  # click `building` tab
    element = driver.find_element_by_xpath(Element.DATE_FROM_XPATH.value)  # find `date_from` input
    element.send_keys((datetime.today()
                       - timedelta(days=days_to_scrape)).strftime('%m/%d/%Y'))  # enter `date_from`
    driver.find_element_by_xpath(Element.SEARCH_BUTTON_XPATH.value).click()  # click the `search` button

    table_rows = get_table(driver, Element.TABLE_ID.value)
    headers = get_headers(table_rows)
    permits = dict()

    # determine if there are more than 1 page of the results
    if len(table_rows) < TableHTML.HEADER_AND_ABOVE.value \
            + TableHTML.CONTENT_AND_PAGE_NAV.value:  # if there is only 1 page in the result
        content_rows = table_rows[TableHTML.HEADER_AND_ABOVE.value:]
        permit_objs = scrape_content(headers, content_rows)
    else:  # for multiple pages of results
        page_row = table_rows[TableHTML.PAGE_ROW_POSITION.value]
        content_rows = table_rows[TableHTML.HEADER_AND_ABOVE.value:-TableHTML.PAGE_NAV.value]
        permit_objs = scrape_content(headers, content_rows)
        while click_next(page_row):  # click to goto next page and determine if at the last page
            wait_for_staleness(driver, Element.TABLE_ID.value)
            table_rows = get_table(driver, Element.TABLE_ID.value)
            page_row = table_rows[TableHTML.PAGE_ROW_POSITION.value]
            content_rows = table_rows[TableHTML.HEADER_AND_ABOVE.value:-TableHTML.PAGE_NAV.value]
            permit_objs = permit_objs + scrape_content(headers, content_rows)
    permits["permit"] = permit_objs
    return permits
