import time

import bs4
from selenium import webdriver

from constants.constants import LEET_CODE_LOGIN_URL, USERNAME_HTML_ELEMENT_NAME, PASSWORD_HTML_ELEMENT_NAME, \
    ACTUAL_PREMIUM_PASSWORD, ACTUAL_PREMIUM_USERNAME, LEET_CODE_PROBLEM_SET, SUBMIT_BUTTON_CLASS_NAME, \
    COMPANY_SECTION_ID, ANCHOR_ELEMENT, COMPANY_PREFIX, HREF_ATTRIBUTE, LEET_CODE_HOME_URL, SUBSCRIBE, SIGN_IN_SLEEP, \
    SIGN_IN_PAGE_LOAD_SLEEP, QUESTION_NAVIGATION_TIME_SLEEP, QUESTION_LOAD_TIME_SLEEP, T_BODY_HTML_ELEMENT, \
    COMPANY_WISE_QUESTION_LIST_HTML_CLASS, TR_HTML_ELEMENT, TD_HTML_ELEMENT, TXT_EXTENSION, URL_SPLITTER, \
    VALUE_HTML_ATTRIBUTE, QUESTION_ID_NAME_SEPARATOR, PREMIUM_QUESTION_LIST_ID, ORDERED_LIST_HTML_ELEMENT, \
    LISTED_ITEM_HTML_ELEMENT, LIST_SEPARATOR, QUESTION_DESCRIPTION_CLASS_NAME, DIV_HTML_ELEMENT, HTML_EXTENSION, \
    HTML_TEMPLATE_START, HTML_TEMPLATE_END, OUTPUT_PATH, COMPANIES_LIST_NAME, PREMIUM_QUESTIONS_NAME, \
    PREMIUM_QUESTIONS_PATH


# login into Leetcode to get the dumps
def sign_in_user(driver, url):
    driver.get(url)
    username = driver.find_element_by_name(USERNAME_HTML_ELEMENT_NAME)
    password = driver.find_element_by_name(PASSWORD_HTML_ELEMENT_NAME)
    username.send_keys(ACTUAL_PREMIUM_USERNAME)
    password.send_keys(ACTUAL_PREMIUM_PASSWORD)
    # change this time based on whether you get recaptcha
    # :( we have to manually check whether it asks for recaptcha if yes, click on signin button
    # and recaptcha it before this time ends, else you signout and comeback to this login page
    # and manually enter the credentials and wait, will find a better way to handle this in future
    time.sleep(SIGN_IN_SLEEP)
    sign_in_button = driver.find_element_by_class_name(SUBMIT_BUTTON_CLASS_NAME)
    sign_in_button.click()


def get_logged_in_dumps(url_of_dump_needed):
    # Open firefox, and login and go to problems page
    driver = webdriver.Firefox()
    sign_in_user(driver, LEET_CODE_LOGIN_URL)
    driver.get(url_of_dump_needed)
    time.sleep(SIGN_IN_PAGE_LOAD_SLEEP)
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


def visit_pages_scrap_question_url(companies_list):
    driver = webdriver.Firefox()
    sign_in_user(driver, LEET_CODE_LOGIN_URL)
    time.sleep(QUESTION_NAVIGATION_TIME_SLEEP)
    for company in companies_list:
        driver.get(LEET_CODE_HOME_URL + company)
        time.sleep(QUESTION_LOAD_TIME_SLEEP)
        page_src = driver.page_source
        soup = bs4.BeautifulSoup(page_src)
        problems_table = soup.find(T_BODY_HTML_ELEMENT, {"class": COMPANY_WISE_QUESTION_LIST_HTML_CLASS})
        rows = problems_table.find_all(TR_HTML_ELEMENT)
        with open(OUTPUT_PATH + company.split(URL_SPLITTER)[2] + TXT_EXTENSION, 'w') as f2:
            for row in rows:
                question_data = row.find_all(TD_HTML_ELEMENT)
                question_id = question_data[1].attrs[VALUE_HTML_ATTRIBUTE]
                question_name = question_data[2].attrs[VALUE_HTML_ATTRIBUTE]
                f2.write(question_id + QUESTION_ID_NAME_SEPARATOR + question_name + "\n")
            f2.close()
    driver.close()


def store_premium_question_links(driver):
    driver.get(LEET_CODE_HOME_URL + SUBSCRIBE)
    time.sleep(QUESTION_NAVIGATION_TIME_SLEEP)
    page_src = driver.page_source
    soup = bs4.BeautifulSoup(page_src)
    list_of_questions = soup.find(id=PREMIUM_QUESTION_LIST_ID).find_all_next(ORDERED_LIST_HTML_ELEMENT)[0]\
        .find_all_next(LISTED_ITEM_HTML_ELEMENT)
    with open(OUTPUT_PATH + PREMIUM_QUESTIONS_NAME, 'w') as f3:
        for question in list_of_questions:
            question_data = question.find(ANCHOR_ELEMENT)
            f3.write(question_data.attrs[HREF_ATTRIBUTE] + LIST_SEPARATOR)
        f3.close()


def open_premium_questions_and_fetch_content(driver):
    with open(OUTPUT_PATH + PREMIUM_QUESTIONS_NAME, 'r') as premium_questions_file:
        questions = premium_questions_file.readlines()
        premium_questions_file.close()
    questions_list = []
    if len(questions) > 0:
        questions_list = questions[0].split(LIST_SEPARATOR)
    sign_in_user(driver, LEET_CODE_LOGIN_URL)
    time.sleep(QUESTION_NAVIGATION_TIME_SLEEP)
    for question in questions_list:
        driver.get(LEET_CODE_HOME_URL + question)
        time.sleep(QUESTION_NAVIGATION_TIME_SLEEP)
        question_description = bs4.BeautifulSoup(driver.page_source)\
            .find_all(DIV_HTML_ELEMENT, {"class": QUESTION_DESCRIPTION_CLASS_NAME})
        with open(OUTPUT_PATH + PREMIUM_QUESTIONS_PATH + question.split(URL_SPLITTER)[2] + HTML_EXTENSION, 'w') \
                as premium_file:
            premium_file.write(HTML_TEMPLATE_START + str(question_description[0]) + HTML_TEMPLATE_END)
            premium_file.close()


def fetch_premium_questions():
    should_store_premium_questions = False
    driver = webdriver.Firefox()
    if should_store_premium_questions:
        store_premium_question_links(driver)
    open_premium_questions_and_fetch_content(driver)
    driver.close()


def fetch_company_wise_questions():
    should_fetch_company_list = False
    if should_fetch_company_list:
        page_source = get_logged_in_dumps(LEET_CODE_PROBLEM_SET)
        company_list = get_company_list(page_source)
        with open(OUTPUT_PATH + COMPANIES_LIST_NAME, 'w') as f:
            for item in company_list:
                f.write("%s," % item)
            f.close()
    with open(OUTPUT_PATH + COMPANIES_LIST_NAME, 'r') as f:
        companies = f.readlines()
        f.close()
    company_list = []
    if len(companies) > 0:
        company_list = companies[0].split(LIST_SEPARATOR)
    visit_pages_scrap_question_url(company_list)


if __name__ == '__main__':
    should_fetch_company_wise_questions = False
    should_fetch_premium_questions = True
    if should_fetch_company_wise_questions:
        fetch_company_wise_questions()

    if should_fetch_premium_questions:
        fetch_premium_questions()


