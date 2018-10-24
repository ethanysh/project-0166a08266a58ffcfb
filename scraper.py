from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
from enum import Enum
import time

URL_TO_SCRAPE = 'https://aca3.accela.com/Atlanta_Ga/Welcome.aspx'
CHROME_PATH = r'C:\Users\ethan\OneDrive\Documents\freelance\chromedriver.exe'
DAYS_TO_START_FROM_TODAY = 1  # 1 means from yesterday, 2 from the day before yesterday
WAIT_TIME = 10  # wait until page load (in seconds)
TABLE_ID = 'ctl00_PlaceHolderMain_dgvPermitList_gdvPermitList'
LAST_CELL_ID = 'ctl00_PlaceHolderMain_dgvPermitList_gdvPermitList_ctl11_lblShortNote'


class TableHTML(Enum):
    NUM_TR_TAG_HEADER_AND_ABOVE = 3
    NUM_TR_TAG_AFTER_CONTENT = 2
    NUM_TR_TAG_CONTENT_WITH_PAGE_NAV = 12
    HEADER_ROW_LOCATION = 2  # the 3rd 'tr' tag in table tag
    PAGE_ROW_LOCATION = -1  # the last 'tr' tag in table tag contains the page nav


def wait_for_page_load(driver: webdriver, wait_time: int, by_method, method_val: str):
    try:
        element = WebDriverWait(driver, wait_time).until(
           EC.presence_of_element_located((by_method, method_val))
        )
    except Exception as e:
        print(e)
        exit(1)
    else:
        return element


def wait_for_stalness(driver, wait_time, element_id):
    try:
        is_attached = WebDriverWait(driver, wait_time).until(
            EC.staleness_of(driver.find_element_by_id(element_id))
        )
    except Exception as e:
        print(e)
        exit(1)
    else:
        return is_attached


def scrape_content(content_rows: list) -> list:
    obj_list = []
    for row in content_rows:
        cells = row.find_elements_by_tag_name('span')
        vals = []
        for cell in cells:
            val = cell.text.strip()
            vals.append(val)
        obj = dict(zip(headers, vals))
        obj_list.append(obj)
    return obj_list


def click_next(page_row) -> bool:
    next_button = page_row.find_elements_by_tag_name('td')[-1]
    try:
        next_button.find_element_by_tag_name('a').click()
    except Exception as e:
        return False
    else:
        return True


def get_table(driver):
    # time.sleep(3)
    element = wait_for_page_load(driver, WAIT_TIME, By.ID, TABLE_ID)
    table_block = element.find_element_by_tag_name('tbody')
    table_rows = table_block.find_elements_by_tag_name('tr')
    return table_rows


driver = webdriver.Chrome(CHROME_PATH)
driver.get(URL_TO_SCRAPE)
driver.find_element_by_xpath('//*[@title="Building"]').click()
element = driver.find_element_by_xpath('//*[@id="ctl00_PlaceHolderMain_generalSearchForm_txtGSStartDate"]')
element.send_keys((datetime.today() - timedelta(days=DAYS_TO_START_FROM_TODAY)).strftime('%m/%d/%Y'))
driver.find_element_by_xpath('//*[@id="ctl00_PlaceHolderMain_btnNewSearch"]').click()

permits = []

rows = get_table(driver)

# get header
header_block = rows[TableHTML.HEADER_ROW_LOCATION.value]
header_list = header_block.find_elements_by_tag_name("span")
headers = []
for header in header_list:
    val = header.text.strip()
    if val not in [None, '']:
        headers.append(header.text.strip())

# determine if there are more than 1 page of the results
if len(rows) < TableHTML.NUM_TR_TAG_HEADER_AND_ABOVE.value + TableHTML.NUM_TR_TAG_CONTENT_WITH_PAGE_NAV.value:
    content_rows = rows[TableHTML.NUM_TR_TAG_HEADER_AND_ABOVE.value:]
    permits = scrape_content(content_rows)
else:
    page_row = rows[TableHTML.PAGE_ROW_LOCATION.value]
    content_rows = rows[TableHTML.NUM_TR_TAG_HEADER_AND_ABOVE.value:-TableHTML.NUM_TR_TAG_AFTER_CONTENT.value]
    permits = scrape_content(content_rows)
    # determine if at the last page
    while click_next(page_row):
        wait_for_stalness(driver, WAIT_TIME, TABLE_ID)
        rows = get_table(driver)
        page_row = rows[TableHTML.PAGE_ROW_LOCATION.value]
        content_rows = rows[TableHTML.NUM_TR_TAG_HEADER_AND_ABOVE.value:-TableHTML.NUM_TR_TAG_AFTER_CONTENT.value]
        permits = permits + scrape_content(content_rows)
