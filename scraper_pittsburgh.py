from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
from enum import Enum
import time


class Element(Enum):
    """
    The class contains variables that describe different attributes of web elements to be located
    """
    FREE_SEARCH_JS = 'javascript: clickTab("0");'
    DOCUMENT_SEARCH_JS = 'javascript:clickTab("1");'
    TO_DATE_NAME = 'todate'
    FROM_DATE_NAME = 'fromdate'
    OFFICE_ID_NAME = 'officeid'
    DEEDS_NAME = 'deeds'
    MORTGAGE_NAME = 'mortgage'
    DEEDS_VALUE = '60'
    MORTGAGES_VALUE = '61'
    SEARCH_NOW_XPATH = '//a[*="Search now"]'
    TABLE_XPATH = '//table[@bordercolor="#E5E5E5"][2]'
    OPEN_NEW_WINDOW_JS = 'window.open('');'
    NEXT_BUTTON_XPATH = '//a[./text()="Next"]'


class Headers(Enum):
    STREET_NUMBER = 'street_number'
    STREET_ADDRESS = 'street_address'
    ISSUE_DATE = 'issue_date'
    CONSIDERATION = 'consideration'
    DOC_NUMBER = 'docnumber'
    GRANTEE = 'grantee'
    ENTRY_DATE = 'entrydate'
    CITY = 'city'
    STATE = 'state'
    BOOK_PAGE = 'bookpage'
    GRANTOR = 'grantor'


class DetailedElement(Enum):
    STREET_NUMBER_XPATH = '//tr[*="Loc"]/following-sibling::tr/td[3]'
    STREET_ADDRESS_XPATH = '//tr[*="Loc"]/following-sibling::tr/td[4]'
    ISSUE_DATE_XPAHT = '//*[@id="detail"]/form/center/table[1]/tbody/tr[2]/td/table/tbody/tr[3]/td[2]/font'
    CONSIDERATION = '//*[@id="detail"]/form/center/table[1]/tbody/tr[2]/td/table/tbody/tr[3]/td[7]/font'
    DOC_NUMBER = '//*[@id="detail"]/form/center/table[1]/tbody/tr[2]/td/table/tbody/tr[3]/td[1]/font'
    GRANTEE = '//*[@id="detail"]/form/center/table[1]/tbody/' \
              'tr[5]/td/table/tbody/tr[2]/td[2]/table/tbody/tr/td/font/a/font'
    CITY = '//tr[*="Loc"]/following-sibling::tr/td[1]'
    BOOK_PAGE = '//*[@id="detail"]/form/center/table[1]/tbody/tr[2]/td/table/tbody/tr[3]/td[6]/font'
    GRANTOR = '//*[@id="detail"]/form/center/table[1]/tbody/tr[5]/td/table/tbody/tr[1]/td[2]/table/tbody/' \
              'tr/td/font/a/font'
    STATE = 'PA'


DETAILS_MAP = {
    Headers.STREET_NUMBER.value: DetailedElement.STREET_NUMBER_XPATH.value,
    Headers.STREET_ADDRESS.value: DetailedElement.STREET_ADDRESS_XPATH.value,
    Headers.ISSUE_DATE.value: DetailedElement.ISSUE_DATE_XPAHT.value,
    Headers.CONSIDERATION.value: DetailedElement.CONSIDERATION.value,
    Headers.DOC_NUMBER.value: DetailedElement.DOC_NUMBER.value,
    Headers.GRANTEE.value: DetailedElement.GRANTEE.value,
    Headers.CITY.value: DetailedElement.CITY.value,
    Headers.BOOK_PAGE.value: DetailedElement.BOOK_PAGE.value,
    Headers.GRANTOR.value: DetailedElement.GRANTOR.value
}

CONSIDERATION_LIMIT = 1000000


def basic_clean(text: str) -> str:
    """
    Function do a basic clean of the text scraped off the web site, including strip the text off whitespaces,
    linebreaks, ect.
    :param text: input the text to be cleaned
    :return: return the cleaned text
    """
    return text.strip().replace('\r\n', ', ').replace('\r', ', ').replace('\n', ', ')


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


def get_table(driver: webdriver, table_identifier: str) -> list:
    """
    The function gets the table to be scraped by `talbe_id`.
    Tips: after loading a new page, use `wait_for_staleness()` to wait until the old web element to detach the DOM
        to grab the new element. In case `wait_for_staleness()` not working, use `time.sleep()` in below instead.
    :param table_identifier: value in method to identify the table element, can be `id`, `name`, `class`, `xpath` etc.
    :param driver: the web driver in use
    :return: function returns a list of row elements int the table, represented by `tr` tags
    """
    # time.sleep(3)
    element = wait_for_element_load(driver, By.XPATH, table_identifier)
    table_rows = element.find_elements_by_tag_name('tr')
    return table_rows


def get_url_list(table_content: list) -> list:
    """
    The function gets the list of urls of details page of each object to be scraped on the current page
    :param table_content: a list of selenium objects represent rows of the table to be scraped
    :return: a list of urls
    """
    urls = []
    for row in table_content:
        try:
            url_cell = row.find_element_by_tag_name('a')
        except:
            pass
        else:
            urls.append(url_cell.get_attribute('href'))
    return urls


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
        elements = driver.find_elements_by_xpath(xpath)
    except:
        pass
    else:
        obj[detail] = []
        for element in elements:
            val = basic_clean(element.text)
            if detail == Headers.CONSIDERATION.value:  # for `consideration` attribute, convert to float number
                try:
                    val = float(val.replace('$', '').replace(',', ''))
                except ValueError:
                    val = 0
            obj[detail].append(val)
        if len(obj[detail]) <= 1:
            val = obj[detail][0]
            obj[detail] = val
    return obj


def scrape_details(driver: webdriver, url: str) -> [dict, None]:
    """
    The function scrapes data on the details page of the object
    :param driver: the webdriver in use
    :param url: the url of the details page for the object
    :return: a dict of attribute value pairs of the object satisfies given requirements or None if not.
    """
    obj = dict()
    driver.switch_to.window(driver.window_handles[1])
    driver.get(url)  # open the details page
    details = list(DETAILS_MAP.keys())  # get the attributes and the referring content locator from a dict constant
    for detail in details:
        xpath = DETAILS_MAP[detail]
        obj.update(get_detail(driver, detail, xpath))
    if obj[Headers.CONSIDERATION.value] >= CONSIDERATION_LIMIT:
        if type(obj[Headers.STREET_NUMBER.value]) == list:
            street_address_update = [number + " " + address for number, address
                                     in zip(obj[Headers.STREET_NUMBER.value], obj[Headers.STREET_ADDRESS.value])]
        else:
            street_address_update = obj[Headers.STREET_NUMBER.value] + " " + obj[Headers.STREET_ADDRESS.value]
        obj[Headers.STREET_ADDRESS.value] = street_address_update
        obj.pop(Headers.STREET_NUMBER.value)
        obj.update({Headers.STATE.value: DetailedElement.STATE.value})
        obj.update({Headers.ENTRY_DATE.value: datetime.now()})
        return obj
    else:
        return None


def click_next(driver: webdriver, counter: int) -> bool:
    """
    The function clicks the next page
    :param driver: the webdriver in use
    :param counter: the function does nothing if the script is on the first page (`counter` is 0) of the table
    :return: `True` if the next button is successfully clicked, `False` if otherwise
    """
    if counter == 0:
        return True
    else:
        time.sleep(2)
        try:
            driver.find_element_by_xpath(Element.NEXT_BUTTON_XPATH.value).click()
        except:
            return False
        else:
            return True


def scrape_content(driver: webdriver, index: str, days_to_scrape=0) -> list:
    """
    The function scrapes the each and every object on the current page
    :param driver: the webdriver in use
    :param index: the value of the `option` attribute in the drop down list located in the search box. This is
                  to identify the type of the objects to be scraped. `60` for `deeds` and `61` for mortgage.
                  Check the html code of the search box to find out all the values.
    :param days_to_scrape:days prior to today to start scraping. 1 means from yesterday to today, 2 days in total.
                           The value is defaulted to scrape the data for only 1 day, that is today only.
    :return: a list of all the objects in JSON-like format that satisfying a set of given requirements.
    """
    driver.execute_script(Element.FREE_SEARCH_JS.value)
    driver.execute_script(Element.DOCUMENT_SEARCH_JS.value)
    Select(driver.find_element_by_name(Element.OFFICE_ID_NAME.value)).select_by_value(index)
    to_day_input = driver.find_element_by_name(Element.TO_DATE_NAME.value)
    to_day_value = to_day_input.get_attribute("value")
    from_date_value = (datetime.strptime(to_day_value, "%m/%d/%Y")
                       - timedelta(days=days_to_scrape)).strftime("%m/%d/%Y")
    from_date_input = driver.find_element_by_name(Element.FROM_DATE_NAME.value)
    from_date_input.clear()
    from_date_input.send_keys(from_date_value)
    driver.find_element_by_xpath(Element.SEARCH_NOW_XPATH.value).click()

    counter = 0
    objs = []
    while click_next(driver, counter):
        table_rows = get_table(driver, Element.TABLE_XPATH.value)
        table_content = table_rows[1:]
        url_list = get_url_list(table_content)
        driver.execute_script(Element.OPEN_NEW_WINDOW_JS.value)  # open a new window
        for url in url_list:
            obj = scrape_details(driver, url)
            if obj is not None:
                objs.append(obj)
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        counter += 1
    return objs


def scraper_pittsburgh(chrome_path: str, url='https://pa_allegheny.uslandrecords.com/palr/') -> dict:
    """
    The actual scraping process. The function scrapes `deeds` and `mortgage` objects off the website.
    :param chrome_path: the location where the `chrome driver` is stored
    :param url: the url of the website to be scraped
    :return: a list contains a set of `deeds` objects and a set of `mortgage` objects that satisfying a given criteria.
    """
    driver = webdriver.Chrome(chrome_path)
    driver.get(url)
    deeds = scrape_content(driver, Element.DEEDS_VALUE.value)
    mortgage = scrape_content(driver, Element.MORTGAGES_VALUE.value)
    obj = {Element.DEEDS_NAME.value: deeds,
           Element.MORTGAGE_NAME.value: mortgage}
    return obj
