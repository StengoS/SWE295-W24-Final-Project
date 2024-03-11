import time
import json
import os

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def get_official_name(url, artifact_name):
    # Gets the official name of the artifact listed on the mvnrepository page.
    # Made this as a testing function, so far doesn't actually contribute to the actual data.
    driver = webdriver.Chrome()
    driver.get(url)
    driver.quit()

    soup = BeautifulSoup(driver.page_source, "html.parser")
    html_output = soup.prettify()

    html_file = open("main_page.html", "w")
    html_file.write(html_output)
    html_file.close()

    official_name = soup.find(href=artifact_name)
    return official_name.text


def get_usages(url, desired_html):
    # Selenium opens up a Chrome tab to a 'usages' page of an artifact in mvnrepository, then
    # scrapes the whole page's HTML and stores the HTML in a separate file.
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(7)
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    html_output = soup.prettify()

    html_file = open(desired_html, "w", encoding="utf-8")
    html_file.write(html_output)
    html_file.close()

    driver.quit()


def scrape_usages_from_html(html_file):
    # Parses through a generated HTML file from get_usages() and outputs a list of the 
    # usages on that page.
    usage_list = []

    with open(html_file) as fp:
        soup = BeautifulSoup(fp, "html.parser")

        for href in soup.find_all("a", href=True):
            href_link = href.get("href")
            href_text = href.get_text().strip()
            href_link_split = href_link.split("/")[1:]

            if "/artifact/" in href_link and href_text in href_link_split and len(href_link_split) == 3:
                usage_list.append(href_link_split[1] + "/" + href_link_split[2])
    
    return usage_list


def update_data_json(utilized_artifact, usage_list, data_file):
    # Takes in the usage list from scrape_usages_from_html() and the name of the 
    # artifact that was the target of the data scrape (used by the artifacts in the usage list)
    data = {}
    with open(data_file) as repo_data:
        data = json.load(repo_data)

    for artifact in usage_list:
        if artifact != utilized_artifact and artifact not in data[utilized_artifact]:
            data[utilized_artifact].append(artifact)
        if artifact not in data.keys():
            data[artifact] = []

    with open(data_file, "w") as write_file:
        json.dump(data, write_file, indent=4)

            
            
def main():
    # mock_input = "org.apache.logging.log4j/log4j-core"
    # split_input = mock_input.split("/")
    # group_name = split_input[0]
    # artifact_name = split_input[1]
    # target_url_main = "https://mvnrepository.com/artifact/" + mock_input

    # official_name = get_official_name(target_url_main, artifact_name))
    # print(official_name)

    data_file = "mvn_repo_data.json"
    mock_inputs = ["org.springframework.boot/spring-boot"]

    for artifact in mock_inputs:
        for i in range(2, 6):
            target_url_usages = "https://mvnrepository.com/artifact/" + artifact + "/usages?p=" + str(i)
            usages_pg_html = "usages_page_test.html"
            get_usages(target_url_usages, usages_pg_html)
            time.sleep(3)

            usage_list = scrape_usages_from_html(usages_pg_html)
            print(usage_list)
            update_data_json(artifact, usage_list, data_file)
            if os.path.exists(usages_pg_html):
                os.remove(usages_pg_html)


if __name__ == "__main__":
    main()
