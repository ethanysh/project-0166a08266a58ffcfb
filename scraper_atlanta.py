from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
from enum import Enum
import time


class TableHTML(Enum):
    HEADER_AND_ABOVE = 3  # table header and content above has 3 `tr` tags
    PAGE_NAV = 2  # page navigation bar has 2 `tr` tags
    CONTENT_AND_PAGE_NAV = 12  # maximum table content plus page navigation bar has 12 `tr` tags
    HEADER_ROW_POSITION = 2  # the 3rd 'tr' tag in table tag
    PAGE_ROW_POSITION = -1  # the last 'tr' tag in table tag contains the page nav
    CLICK_BUTTON_POSITION = -1  # the last 'td` tag in the last `tr` tag of the table


class Element(Enum):
    BUILDING_TAB_XPATH = '//*[@title="Building"]'
    DATE_FROM_XPATH = '//*[@id="ctl00_PlaceHolderMain_generalSearchForm_txtGSStartDate"]'
    SEARCH_BUTTON_XPATH = '//*[@id="ctl00_PlaceHolderMain_btnNewSearch"]'
    TABLE_ID = 'ctl00_PlaceHolderMain_dgvPermitList_gdvPermitList'


def wait_for_staleness(driver, element_id, timeout=10):
    try:
        WebDriverWait(driver, timeout).until(
            EC.staleness_of(driver.find_element_by_id(element_id))
        )
    except Exception as e:
        print(e)
        exit(1)


def wait_for_page_load(driver: webdriver, by_method, method_val: str, timeout=10) -> webdriver:
    try:
        element = WebDriverWait(driver, timeout).until(
           EC.presence_of_element_located((by_method, method_val))
        )
    except Exception as e:
        print(e)
        exit(1)
    else:
        return element


def get_table(driver) -> list:
    # time.sleep(3)
    element = wait_for_page_load(driver, By.ID, Element.TABLE_ID.value)
    table_rows = element.find_elements_by_tag_name('tr')
    return table_rows


def get_headers(rows: list) -> list:
    headers = []
    headers_code = rows[TableHTML.HEADER_ROW_POSITION.value]
    headers_text = headers_code.find_elements_by_tag_name("span")
    for header in headers_text:
        val = header.text.strip()
        if val not in [None, '']:
            headers.append(val)
    return headers


def scrape_content(headers: list, content_rows: list) -> list:
    objs = []
    for row in content_rows:
        cells = row.find_elements_by_tag_name('span')
        vals = []
        for cell in cells:
            val = cell.text.strip()
            vals.append(val)
        obj = dict(zip(headers, vals))
        objs.append(obj)
    return objs


def click_next(page_row) -> bool:
    next_button = page_row.find_elements_by_tag_name('td')[TableHTML.CLICK_BUTTON_POSITION.value]
    try:
        next_button.find_element_by_tag_name('a').click()
    except Exception as e:
        return False
    else:
        return True


def scraper_atlanta(chrome_path: str,
                    url='https://aca3.accela.com/Atlanta_Ga/Welcome.aspx',
                    days_to_scrape=1):
    driver = webdriver.Chrome(chrome_path)
    driver.get(url)

    # Start the browser
    driver.find_element_by_xpath(Element.BUILDING_TAB_XPATH.value).click()  # click `building` tab
    element = driver.find_element_by_xpath(Element.DATE_FROM_XPATH.value)  # find `date_from` input
    element.send_keys((datetime.today()
                       - timedelta(days=days_to_scrape)).strftime('%m/%d/%Y'))  # enter `date_from`
    driver.find_element_by_xpath(Element.SEARCH_BUTTON_XPATH.value).click()  # click the `search` button

    table_rows = get_table(driver)
    headers = get_headers(table_rows)

    # determine if there are more than 1 page of the results
    if len(table_rows) < TableHTML.HEADER_AND_ABOVE.value + TableHTML.CONTENT_AND_PAGE_NAV.value:
        content_rows = table_rows[TableHTML.HEADER_AND_ABOVE.value:]
        permits = scrape_content(headers, content_rows)
    else:
        page_row = table_rows[TableHTML.PAGE_ROW_POSITION.value]
        content_rows = table_rows[TableHTML.HEADER_AND_ABOVE.value:-TableHTML.PAGE_NAV.value]
        permits = scrape_content(headers, content_rows)
        # determine if at the last page
        while click_next(page_row):
            wait_for_staleness(driver, Element.TABLE_ID.value)
            table_rows = get_table(driver)
            page_row = table_rows[TableHTML.PAGE_ROW_POSITION.value]
            content_rows = table_rows[TableHTML.HEADER_AND_ABOVE.value:-TableHTML.PAGE_NAV.value]
            permits = permits + scrape_content(headers, content_rows)
    return permits
