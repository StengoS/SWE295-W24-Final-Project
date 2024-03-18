import time
import json
import os

from bs4 import BeautifulSoup
from selenium import webdriver


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
        if artifact != utilized_artifact and artifact not in data[utilized_artifact]["used_by"]:
            data[utilized_artifact]["used_by"].append(artifact)
        if artifact not in data.keys():
            data[artifact] = {
                "used_by": [],
                "has_associated_CVE": False
            }

    with open(data_file, "w") as write_file:
        json.dump(data, write_file, indent=4)


def update_data_vulns_exist(data_file):
    data = {}
    with open(data_file) as repo_data:
        data = json.load(repo_data)

    artifacts_list = list(data.keys())
    for artifact in artifacts_list:
        if data[artifact]["has_associated_CVE"] is None:
            print("Currently checking " + artifact + "...")

            driver = webdriver.Chrome()
            target_url = "https://mvnrepository.com/artifact/" + artifact
            driver.get(target_url)
            
        
            soup = BeautifulSoup(driver.page_source, "html.parser")
            html_output = soup.prettify()

            if "vulnerability" in html_output or "vulnerabilities" in html_output:
                data[artifact]["has_associated_CVE"] = True
            else:
                data[artifact]["has_associated_CVE"] = False
            
            driver.quit()

            with open(data_file, "w") as write_file:
                json.dump(data, write_file, indent=4)


def main():
    data_file = "mvn_repo_data.json"
    # mock_inputs = ["org.springframework.boot/spring-boot"]

    # for artifact in mock_inputs:
    #     for i in range(2, 6):
    #         target_url_usages = "https://mvnrepository.com/artifact/" + artifact + "/usages?p=" + str(i)
    #         usages_pg_html = "usages_page_test.html"
    #         get_usages(target_url_usages, usages_pg_html)
    #         time.sleep(3)

    #         usage_list = scrape_usages_from_html(usages_pg_html)
    #         print(usage_list)
    #         update_data_json(artifact, usage_list, data_file)
    #         if os.path.exists(usages_pg_html):
    #             os.remove(usages_pg_html)

    update_data_vulns_exist(data_file)


if __name__ == "__main__":
    main()
