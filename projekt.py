from operator import concat
from sys import platform
import argparse
from urllib.parse import urlsplit

from selenium import webdriver
from selenium.common import WebDriverException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium_stealth import stealth
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.chrome.options import Options
import json
import time
import re
"""
    Get job offers from justjoin.it
"""

class JobOfferScraper:
    def __init__(self, location, job_name):
        options = Options()
        options.add_argument("--log-level=4")
        options.add_argument("--disable-blink-features=AutomationControlled")

        self.driver = webdriver.Chrome(options=options)
        stealth(self.driver,
                     languages=["en-US", "en"],
                     vendor="Google Inc.",
                     platform="Win32",
                     webgl_vendor="Intel Inc.",
                     renderer="Intel Iris OpenGL Engine",
                     fix_hairline=True,
                     )
        self.start_url = "https://justjoin.it/"
        self.location = location
        self.job_name = job_name
        self.job_info = []
        self.elements = []
        self.driver.implicitly_wait(10)

    def setup(self):
        cookie = self.wait_for_one("div[id=cookiescript_reject]").click()

        self.driver.find_element(By.CSS_SELECTOR, "div > div > div > div > button").click()
        self.driver.find_element(By.CSS_SELECTOR, f'button[value="{self.location}"]').click()
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

    def search(self):
        self.go_somewhere(self.start_url)
        self.setup()

        time.sleep(4)
        search_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div > input"))
            )
        search_input.click()

        search_input.send_keys(self.job_name + Keys.ENTER)

        time.sleep(2)

        length = self.get_amount_of_offers()
        print(f'Amount of offers: {length}')
        urls = self.get_offers(0, length)

        if len(urls) > 0:
            self.get_the_data(urls)
            self.write_results()
        else:
            print('There are no offerts for this job')

    def get_offers(self, dataindex, length):
        urls = []
        while dataindex < length:
            el = self.wait_for_one(f'li[data-index="{dataindex}"]', 1)
            if el != None:
                self.elements.append(el)
                urls.append(el.find_element(By.CSS_SELECTOR, "a").get_attribute("href") )
                dataindex += 1
            else:
                self.driver.execute_script('window.scrollTo({top: window.pageYOffset + window.innerHeight, behavior: "smooth",});')
        return urls
    def get_amount_of_offers(self):
        length = self.wait_for_one("h1").text
        temp = re.findall("[0-9]", length)
        length = ""
        for el in temp:
            length += el
        return int(length)

    def get_the_data(self, urls):
        print(f"Getting info of {len(urls)} offers...")
        for url in urls:
            self.go_somewhere(url)
            self.job_info.append(self.get_one_el(url))

    def get_one_el(self, url):
        title = self.wait_for_one("h1")
        title = self.check_if_null(title)

        company = self.wait_for_one("h2")
        company = self.check_if_null(company)

        salary_info = self.wait("div > span span")
        salary = ""

        if len(salary_info) != 0:
            for el in salary_info[:2]:
                salary += el.text + " "
        location = self.wait_for_one("svg + div > span")
        location = self.check_if_null(location)

        type_of = self.safe_xpath("//div[contains(text(), 'Type of work')]/following-sibling::div")
        exp = self.safe_xpath("//div[contains(text(), 'Experience')]/following-sibling::div")
        employment = self.safe_xpath("//div[contains(text(), 'Employment Type')]/following-sibling::div")
        from_where = self.safe_xpath("//div[contains(text(), 'Operating mode')]/following-sibling::div")

        skills = []
        temp = self.wait("ul > div > div")
        if temp:
            for skill in temp:
                skills.append(
                    [skill.find_element(By.CSS_SELECTOR, "h4").text, skill.find_element(By.CSS_SELECTOR, "span").text])
        else:
            skills = []

        paragraphs = self.wait("div > div > div p")
        try:
            paragra = [paragraph.text for paragraph in paragraphs]
        except StaleElementReferenceException as e:
            paragra = []
            self.log_error(f"Problem with .text argument in some of the paragraphs: {e}")

        return dict(Title=title, Company=company, Salary=salary, Location=location, Type_of_work=type_of,
                    Experience=exp, Employment=employment, Operating_mode=from_where, Link = url, Skills=skills, Content=paragra)

    def safe_xpath(self, xpath):
        try:
            return self.driver.find_element(By.XPATH, xpath).text
        except NoSuchElementException as e:
            self.log_error(f"No such element: {e}")
            return ""

    def check_if_null(self, something):
        if something is None:
            self.log_error(f"The value of {something} was None")
            return ""
        else:
            return something.text

    def write_results(self):
        try:
            print(f"Writeing {len(self.job_info)} offers to json file...")
            with open('data.json', 'w', encoding='utf-8') as f:
                json.dump(self.job_info, f, ensure_ascii=False, indent=4)
        except Exception as e:
            self.log_error(e)

    def close(self):
        self.driver.close()

    def log_error(self, message):
        with open("scraper_errors.log", "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")

    def go_somewhere(self, link):
        try:
            self.driver.get(link)
        except WebDriverException as e:
            self.log_error(f"WebDriver error while opening page: {e}")
        except Exception as e:
            self.log_error(f"Unexpected error: {e}")

    def wait(self, string, time = 5, where = None):
        try:
            if where is None:
                where = self.driver
            something = WebDriverWait(where, time).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, string))
            )
            return something
        except StaleElementReferenceException as e:
            self.log_error(f"Problem with element which WebDriverWait has to wait: {e}")
            return None

    def wait_for_one(self, string, time = 5, where = None):
        try:
            if where is None:
                where = self.driver
            something = WebDriverWait(where, time).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, string))
            )
            return something
        except StaleElementReferenceException as e:
            self.log_error(f"Problem with element which WebDriverWait has to wait: {e}")
            return None
        except TimeoutException as e:
            self.log_error(f"Problem with element which WebDriverWait has to wait: {e}")
            return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scraper job offers in JustJoin.it")
    parser.add_argument("--location", type=str, required=True, help="Which city you want")
    parser.add_argument("--job", type=str, required=True, help="Which job position you want")
    args = parser.parse_args()

    scraper = JobOfferScraper(location=args.location, job_name=args.job)
    try:
        scraper.search()
    finally:
        scraper.close()
