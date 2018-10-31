from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
from enum import Enum
import time


class TableHTML(Enum):
    """
    The class contains variables that describe the structure of the table to be scraped
    """
    HEADER_AND_ABOVE = 3  # table header and content above has 3 `tr` tags
    PAGE_NAV = 2  # page navigation bar has 2 `tr` tags
    HEADER_ROW_POSITION = 2  # the 3rd 'tr' tag in table tag
    PAGE_ROW_POSITION = -1  # the last 'tr' tag in table tag contains the page nav
    CLICK_BUTTON_POSITION = -1  # the last 'td` tag in the last `tr` tag of the table
    HEADER_START = 1  # the header starts from the 2nd `th` tag of the header row
    HEADER_END = -1  # the header ends at the 2nd last `th` tag of the header row
    CONTENT_START = 1  # the content starts from the 2nd `td` tag of the table row
    CONTENT_END = -1  # the content ends at the 2nd last `td` tag of the table row
    URL_CELL_POSITION = 2  # the cell contains url of the detail page is in the 3rd `td` tag of the content


class Element(Enum):
    """
    The class contains variables that describe different attributes of web elements to be located
    """
    DATE_FROM_XPATH = '//*[@id="ctl00_PlaceHolderMain_generalSearchForm_txtGSStartDate"]'
    SEARCH_BUTTON_XPATH = '//*[@id="ctl00_PlaceHolderMain_btnNewSearch"]'
    TABLE_ID = 'ctl00_PlaceHolderMain_dgvPermitList_gdvPermitList'
    PAGE_NAV_CLASS = 'aca_pagination'  # class name of page navigation row at the bottom of the
    UNFOLD_BUTTON_XPATH = '//h1/a[@class="NotShowLoading"]'


class DetailedHeader(Enum):
    """
    The class contains attributes of a `permit` object on details page.
    """
    STREET_ADDRESS = 'street_address'
    CONSIDERATION = 'consideration'
    GRANTEE = 'grantee'
    DESCRIPTION = 'description'
    ENTRY_DATE = 'entrydate'


class DetailedElement(Enum):
    """
    The class contains value of html attributes for permit attributes on the detail page of each.
    """
    WORK_LOCATION_XPATH = '//*[@id="divWorkLocationDetail"]'
    OWNER_XPATH = '//div[h1="Owner:"]/span'
    LICENCED_PROFESSIONAL = '//div[h1="Licensed Professional:"]/span'
    JOB_VALUE_XPATH = '//div[span="Job Value($):"]/span[2]'
    NATURE_OF_JOB_XPATH = '//div[span="Nature of Job Desc: "]/following-sibling::div'
    PROJECT_DESCRIPTION = '//div[h1="Project Description:"]/span'
    DESCRIPTIVE_NATURE_XPATH = '//div[span="Descriptive nature of complaint: "]/following-sibling::div'


DETAILS_MAP = {  # the constant maps the attribute needed to scrape to the referring content xpath
    DetailedHeader.STREET_ADDRESS.value: [DetailedElement.WORK_LOCATION_XPATH.value],
    DetailedHeader.CONSIDERATION.value: [DetailedElement.JOB_VALUE_XPATH.value],
    DetailedHeader.GRANTEE.value: [
        DetailedElement.OWNER_XPATH.value,
        DetailedElement.LICENCED_PROFESSIONAL.value],
    DetailedHeader.DESCRIPTION.value: [
        DetailedElement.NATURE_OF_JOB_XPATH.value,
        DetailedElement.PROJECT_DESCRIPTION.value,
        DetailedElement.DESCRIPTIVE_NATURE_XPATH.value
    ]
}


def basic_clean(text: str) -> str:
    """
    Function do a basic clean of the text scraped off the web site, including strip the text off whitespaces,
    linebreaks, ect.
    :param text: input the text to be cleaned
    :return: return the cleaned text
    """
    return text.strip().replace('\r\n', ', ').replace('\r', ', ').replace('\n', ', ')


def wait_for_staleness(driver, element_id, timeout=120):
    """
    The function waits until the old web element detaches the DOM after loading a new page. Otherwise, the script won't
    get the new element and the function raises TimeOut Exception.
    :param driver: the web driver in use
    :param element_id: the id of the web element to be inspected
    :param timeout: wait a timeout period of time for the web element to detach the DOM, defaulted to 120 seconds.
    :return: raise exceptions and exit or no returns
    """
    try:
        WebDriverWait(driver, timeout).until(
            EC.staleness_of(driver.find_element_by_id(element_id))
        )
    except Exception as e:
        print(e)
        exit(1)


def wait_for_element_load(driver: webdriver, by_method: By, method_val: str, timeout=120) -> webdriver:
    """
    The function waits until the expected web element presented in the page to proceed to next
    :param driver: the web driver in use
    :param by_method: a `By` object used to locate the desired web element in by different method
    :param method_val: the values of the `By` method
    :param timeout: wait a timeout period of time for the web element to be presented in the page,
                    defaulted to 120 seconds.
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


def wait_for_elements_load(driver: webdriver, by_method: By, method_val: str, timeout=120) -> list:
    """
    The function waits until all the expected web elements presented in the page to proceed to next
    :param driver: the web driver in use
    :param by_method: a `By` object used to locate the desired web element in by different method
    :param method_val: the values of the `By` method
    :param timeout: wait a timeout period of time for the web element to be presented in the page,
                    defaulted to 120 seconds.
    :return: raise exceptions or return the element be waited on
    """
    try:
        elements = WebDriverWait(driver, timeout).until(
           EC.presence_of_all_elements_located((by_method, method_val))
        )
    except Exception as e:
        print(e)
        exit(1)
    else:
        return elements


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
    element = wait_for_element_load(driver, By.ID, table_id)
    table_rows = element.find_elements_by_tag_name('tr')
    return table_rows


def get_headers(rows: list) -> list:
    """
    The function gets the headers of the table to be scraped
    :param rows: rows of the table, usually presented in the code as `tr` tags
    :return: returns a list of table header texts
    """
    headers = []
    headers_code = rows[TableHTML.HEADER_ROW_POSITION.value]
    headers_text = headers_code.find_elements_by_tag_name('th')[TableHTML.HEADER_START.value:
                                                                TableHTML.HEADER_END.value]
    for header in headers_text:
        val = header.text.strip()
        if val not in [None, '']:
            headers.append(val)
    return headers


def get_detail(driver: webdriver, detail: str, xpath: str) -> dict:
    """
    The function scrapes a specific attribute from a details page
    :param driver: the webdriver in use
    :param detail: the attribute needed to scrape
    :param xpath: the xpath of the attribute needed to scrape
    :return: returns a dictionary key-value pair of the attribute to scrape
    """
    obj = dict()
    try:
        element = driver.find_element_by_xpath(xpath)
    except:
        pass
    else:
        val = basic_clean(element.text)
        if detail == DetailedHeader.CONSIDERATION.value:  # for `consideration` attribute, convert to float number
            try:
                val = float(val.replace('$', '').replace(',', ''))
            except ValueError:
                val = 0
        obj[detail] = val
    return obj


def scrape_details(driver: webdriver, url) -> dict:
    """
    The function scrapes all needed attributes off the details page of each permit
    :param driver: the webdriver in use
    :param url: the url of the details page
    :return: return a JSON-like object contains the attributes get from the detail page
    """
    obj = dict()
    driver.execute_script("window.open('');")  # open a new window
    driver.switch_to.window(driver.window_handles[1])
    driver.get(url)  # open the details page
    collapses = wait_for_elements_load(driver, By.XPATH, Element.UNFOLD_BUTTON_XPATH.value)  # unfold all sub levels
    for button in collapses:
        button.click()
        time.sleep(1)  # wait for hidden content reveals
    details = list(DETAILS_MAP.keys())  # get the attributes and the referring content locator from a dict constant
    for detail in details:
        xpath = DETAILS_MAP[detail]
        for path in xpath:
            obj.update(get_detail(driver, detail, path))
    # time.sleep(3)
    driver.close()
    return obj


def scrape_content(driver: webdriver, headers: list, content_rows: list) -> list:
    """
    Get the content of the table
    :param driver: the webdriver in use
    :param headers: table header
    :param content_rows: row elements of the table content, usually presented as `tr` tags
    :return: returns a list of permit object in dictionary type
    """
    objs = []
    obj_detail = dict()
    for row in content_rows:
        cells = row.find_elements_by_tag_name('td')[TableHTML.CONTENT_START.value:
                                                    TableHTML.CONTENT_END.value]
        vals = []
        for cell in cells:
            val = basic_clean(cell.text)
            vals.append(val)
        url_cell = cells[TableHTML.URL_CELL_POSITION.value]
        try:
            url = url_cell.find_element_by_tag_name('a').get_attribute('href')  # get the url for the detail page
        except:
            pass  # pass to the next permit if details page is not available
        else:
            obj_detail = scrape_details(driver, url)  # scrape off the detail page
            driver.switch_to_window(driver.window_handles[0])  # get back to the table list
        obj = dict(zip(headers, vals))
        obj.update(obj_detail)
        obj.update({DetailedHeader.ENTRY_DATE.value: datetime.now()})  # add timestamp
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


def scraper_fort_worth(chrome_path: str,
                       url='https://accela.fortworthtexas.gov/CitizenAccess/Cap/CapHome.aspx?module=Development&TabName'
                           '=Development&TabList=Home%7C0%7CDevelopment%7C1%7CFire%7C2%7CGasWell%7C3%7CPlanning%7C4%7C'
                           'Licenses%7C5%7CStreetUse%7C6%7CInfrastructure%7C7%7CCurrentTabIndex%7C1',
                       days_to_scrape=1) -> dict:
    """
    The actual scraping process.
    :param chrome_path: the path in the system where `chromedriver` is stored
    :param url: the url of the website to be scraped
    :param days_to_scrape: days prior to today to start scraping. 1 means from yesterday to today, 2 days in total.
           The value is defaulted to scrape the data from yesterday to today.
    :return: The function returns a list of permit object in JSON-like style.
    """
    # initiate the driver and start the browser
    driver = webdriver.Chrome(chrome_path)
    driver.get(url)

    # navigate the page to content to be scraped
    element = driver.find_element_by_xpath(Element.DATE_FROM_XPATH.value)  # find `date_from` input
    element.send_keys((datetime.today()
                       - timedelta(days=days_to_scrape)).strftime('%m/%d/%Y'))  # enter `date_from`
    driver.find_element_by_xpath(Element.SEARCH_BUTTON_XPATH.value).click()  # click the `search` button

    # get the table to be scraped
    table_rows = get_table(driver, Element.TABLE_ID.value)
    headers = get_headers(table_rows)
    permits = dict()

    # determine if there are more than 1 page of the results
    try:
        driver.find_element_by_class_name(Element.PAGE_NAV_CLASS.value)
    except:  # if there is only 1 page in the result
        content_rows = table_rows[TableHTML.HEADER_AND_ABOVE.value:]
        permit_objs = scrape_content(driver, headers, content_rows)
    else:  # for multiple pages of results
        page_row = table_rows[TableHTML.PAGE_ROW_POSITION.value]
        content_rows = table_rows[TableHTML.HEADER_AND_ABOVE.value:-TableHTML.PAGE_NAV.value]
        permit_objs = scrape_content(driver, headers, content_rows)
        while click_next(page_row):  # click to goto next page and determine if at the last page
            wait_for_staleness(driver, Element.TABLE_ID.value)
            table_rows = get_table(driver, Element.TABLE_ID.value)
            page_row = table_rows[TableHTML.PAGE_ROW_POSITION.value]
            content_rows = table_rows[TableHTML.HEADER_AND_ABOVE.value:-TableHTML.PAGE_NAV.value]
            permit_objs = permit_objs + scrape_content(driver, headers, content_rows)
    permits["permit"] = permit_objs
    return permits
