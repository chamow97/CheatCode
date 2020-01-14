import time

import bs4
from selenium import webdriver

from constants.constants import LEET_CODE_LOGIN_URL, USERNAME_HTML_ELEMENT_NAME, PASSWORD_HTML_ELEMENT_NAME, \
    ACTUAL_PREMIUM_PASSWORD, ACTUAL_PREMIUM_USERNAME, LEET_CODE_PROBLEM_SET, SUBMIT_BUTTON_CLASS_NAME, \
    COMPANY_SECTION_ID, ANCHOR_ELEMENT, COMPANY_PREFIX, HREF_ATTRIBUTE, LEET_CODE_HOME_URL


# login into Leetcode to get the dumps


def get_logged_in_dumps(url_of_dump_needed):
    # Open firefox, and login and go to problems page
    driver = webdriver.Firefox()
    driver.get(LEET_CODE_LOGIN_URL)
    username = driver.find_element_by_name(USERNAME_HTML_ELEMENT_NAME)
    password = driver.find_element_by_name(PASSWORD_HTML_ELEMENT_NAME)
    username.send_keys(ACTUAL_PREMIUM_USERNAME)
    password.send_keys(ACTUAL_PREMIUM_PASSWORD)
    time.sleep(5)
    sign_in_button = driver.find_element_by_class_name(SUBMIT_BUTTON_CLASS_NAME)
    sign_in_button.click()
    driver.get(url_of_dump_needed)
    time.sleep(5)
    html_page_source = driver.page_source
    driver.close()
    return html_page_source


def get_company_list(source):
    soup = bs4.BeautifulSoup(source)
    company_list_links = soup.find(id=COMPANY_SECTION_ID).find_all_next(ANCHOR_ELEMENT)
    company_urls = []
    for company in company_list_links:
        if company.attrs[HREF_ATTRIBUTE].startswith(COMPANY_PREFIX):
            company_urls.append(company.attrs[HREF_ATTRIBUTE])
    return company_urls


def visit_pages_scrap_question_url(companies):
    for company in companies:
        print(get_logged_in_dumps(LEET_CODE_HOME_URL + company))
        break
    return []


if __name__ == '__main__':
    page_source = get_logged_in_dumps(LEET_CODE_PROBLEM_SET)
    company_list = get_company_list(page_source)
    get_company_wise_questions = visit_pages_scrap_question_url(company_list)