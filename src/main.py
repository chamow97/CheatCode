import time

import bs4
from selenium import webdriver

from constants.constants import LEET_CODE_LOGIN_URL, USERNAME_HTML_ELEMENT_NAME, PASSWORD_HTML_ELEMENT_NAME, \
    ACTUAL_PREMIUM_PASSWORD, ACTUAL_PREMIUM_USERNAME, LEET_CODE_PROBLEM_SET, SUBMIT_BUTTON_CLASS_NAME, \
    COMPANY_SECTION_ID, ANCHOR_ELEMENT, COMPANY_PREFIX, HREF_ATTRIBUTE, LEET_CODE_HOME_URL, SUBSCRIBE


# login into Leetcode to get the dumps
def sign_in_user(driver, url):
    driver.get(url)
    username = driver.find_element_by_name(USERNAME_HTML_ELEMENT_NAME)
    password = driver.find_element_by_name(PASSWORD_HTML_ELEMENT_NAME)
    username.send_keys(ACTUAL_PREMIUM_USERNAME)
    password.send_keys(ACTUAL_PREMIUM_PASSWORD)
    time.sleep(65)
    sign_in_button = driver.find_element_by_class_name(SUBMIT_BUTTON_CLASS_NAME)
    sign_in_button.click()


def get_logged_in_dumps(url_of_dump_needed):
    # Open firefox, and login and go to problems page
    driver = webdriver.Firefox()
    sign_in_user(driver, LEET_CODE_LOGIN_URL)
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


def visit_pages_scrap_question_url(companies_list):
    driver = webdriver.Firefox()
    sign_in_user(driver, LEET_CODE_LOGIN_URL)
    time.sleep(10)
    for company in companies_list:
        driver.get(LEET_CODE_HOME_URL + company)
        time.sleep(16)
        page_src = driver.page_source
        soup = bs4.BeautifulSoup(page_src)
        problems_table = soup.find("tbody", {"class": "reactable-data"})
        rows = problems_table.find_all("tr")
        with open("../output/" + company.split("/")[2] + ".txt", 'w') as f2:
            for row in rows:
                question_data = row.find_all("td")
                question_id = question_data[1].attrs["value"]
                question_name = question_data[2].attrs["value"]
                f2.write(question_id + ":" + question_name + "\n")
            f2.close()
    driver.close()
    return []


def store_premium_question_links(driver):
    driver.get(LEET_CODE_HOME_URL + SUBSCRIBE)
    time.sleep(10)
    page_src = driver.page_source
    soup = bs4.BeautifulSoup(page_src)
    list_of_questions = soup.find(id='pq-list').find_all_next("ol")[0].find_all_next("li")
    with open("../output/premium_questions.txt", 'w') as f3:
        for question in list_of_questions:
            question_data = question.find("a")
            f3.write(question_data.attrs["href"] + ",")
        f3.close()


def open_premium_questions_and_fetch_content(driver):
    with open("../output/premium_questions.txt", 'r') as premium_questions_file:
        questions = premium_questions_file.readlines()
        premium_questions_file.close()
    questions_list = []
    if len(questions) > 0:
        questions_list = questions[0].split(",")
    sign_in_user(driver, LEET_CODE_LOGIN_URL)
    time.sleep(10)
    for question in questions_list:
        driver.get(LEET_CODE_HOME_URL + question)
        time.sleep(10)
        question_description = bs4.BeautifulSoup(driver.page_source).find_all("div", {"class": "description__24sA"})
        with open("../output/premiumq/" + question.split("/")[2] + ".html", 'w') as premium_file:
            premium_file.write("<html><body>" + str(question_description[0]) + "</body></html>")
            premium_file.close()


def fetch_premium_questions():
    should_store_premium_questions = False
    driver = webdriver.Firefox()
    if should_store_premium_questions:
        store_premium_question_links(driver)
    open_premium_questions_and_fetch_content(driver)
    driver.close()


if __name__ == '__main__':
    should_fetch_company_wise_questions = False
    should_fetch_premium_questions = True
    if should_fetch_company_wise_questions:
        should_fetch_company_list = False
        if should_fetch_company_list:
            page_source = get_logged_in_dumps(LEET_CODE_PROBLEM_SET)
            company_list = get_company_list(page_source)
            with open('../output/companies.txt', 'w') as f:
                for item in company_list:
                    f.write("%s," % item)
                f.close()
        with open('../output/companies.txt', 'r') as f:
            companies = f.readlines()
            f.close()
        company_list = []
        if len(companies) > 0:
            company_list = companies[0].split(',')
        get_company_wise_questions = visit_pages_scrap_question_url(company_list)

    if should_fetch_premium_questions:
        fetch_premium_questions()


