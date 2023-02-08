import json

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
from selenium_stealth import stealth

import config

"""
Issue #3

scrapper: save new URLs in JSON
"""
cfg = config.read_config()


def getNumberOfPages(link):
    """
        Function to retrieve the number of web pages for a given link.
        :param link: Link to webpage to extract the number of pages from.
        :return: List of links.
    """
    source = getPageSource(link)
    soup = BeautifulSoup(source, 'html.parser')
    pageNumbers = soup.find_all("div", {"class": "pagination-pages"})
    list_of_links = []
    for page in pageNumbers:
        for a in page.findAll('a'):
            print(a.get("href"))
            list_of_links.append(a.get("href"))
    return list_of_links


def getLinksFromWebPage(link):
    '''
        Function to retrieve the links from the web page.
        :param link: link to the webpage to extract the links from.

    '''
    source = getPageSource(link)
    soup = BeautifulSoup(source, 'html.parser')
    links = soup.find_all("a", {"data-object-url-tracking": "resultlist"})
    return links


def getListOfListingLinks(list_of_page_links, url):
    """
        Function to get the listing links from a web page.
        :param list_of_page_links: The paginated links.
        :param url: The base url to be used.
        :return: List of listing links
    """
    list_of_listing_links = []
    for link in list_of_page_links:  # Iterating through the links
        links = getLinksFromWebPage(url % link)  # Retrieving the listing links.
        new_link = (url % link).removesuffix("1-dag/")
        for sub_link in links:
            if new_link in sub_link.get("href"):
                print(sub_link.get("href"))
                list_of_listing_links.append(sub_link.get("href"))  # Extracting the links which are in href.
    return list_of_listing_links


def getPageSource(link):
    """
        Function to get the page source using selenium web driver.
        :param link: Link to web page.
        :return: page_source as a string
    """
    options = Options()
    # Enables faster scraping
    options.add_argument("--headless")  # Don't show browser
    # images aren't rendered
    options.add_argument("--blink-settings=imagesEnabled=false")
    # Starts driver for Chrome once before get the pages
    s = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=s, options=options)
    # Mimics real user so captcha isn't triggered
    stealth(driver,
            user_agent="Chrome/109.0.0.0 Safari/537.36",
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )
    driver.get(link)
    page_source = driver.page_source
    return page_source


def readGemeentenFromFile():
    '''
        Function to read the municipalities from the file.
        :return:  list of gemeenten.
    '''
    # Opening municipalities file for reading.
    gemeenten_file = open(cfg["Other"]["gemeenten-text-location"], "r")
    # Assigning all municipalities to a list.
    gemeenten_contents = gemeenten_file.read()
    gemeenten_list = gemeenten_contents.split("\n")
    gemeenten_file.close()
    return gemeenten_list


def getListOfGemeenten(gemeenten_list):
    list_of_gemeenten = []
    with open(cfg["Other"]["gemeenten-json-location"], 'r') as fcc_file:
        fcc_data = json.load(fcc_file)
    for gemeenten in gemeenten_list:
        try:
            list_of_gemeenten.append(fcc_data[gemeenten]['Funda_sale'])
            list_of_gemeenten.append(fcc_data[gemeenten]['Funda_rent'])
            list_of_gemeenten.append(fcc_data[gemeenten]['Funda-Gemeenten_sale'])
            list_of_gemeenten.append(fcc_data[gemeenten]['Funda-Gemeenten_rent'])
        except:
            try:
                list_of_gemeenten.append(fcc_data[gemeenten]['Funda-Gemeenten_sale'])
                list_of_gemeenten.append(fcc_data[gemeenten]['Funda-Gemeenten_rent'])
            except:
                print("No link for the following gemeenten - ", gemeenten)
    return list_of_gemeenten

def writeToJsonFile(set_of_listing_links):
    dt_string = str(datetime.now().strftime("%Y%m%d-%H%M%S"))
    print("Current Date time -", dt_string)
    json_object = json.dumps([{dt_string: link} for link in set_of_listing_links], indent=4)
    with open(cfg["Other"]["gemeenten-links-json-location"], "w") as outfile:
        outfile.write(json_object)
    print("File write successful!")


def main():
    """
        Main function.
    """
    url = 'https://www.funda.nl%s'  # Base url for funda.nl
    list_of_listing_links = []
    gemeenten_list = readGemeentenFromFile()
    list_of_gemeenten = getListOfGemeenten(gemeenten_list)
    for gemeenten in list_of_gemeenten:
        print("Currently scrapping - " + gemeenten)
        list_of_page_links = getNumberOfPages(url % gemeenten + "1-dag/")  # Generating the list of pages to scrape.
        list_of_links_by_gemeenten = getListOfListingLinks(list_of_page_links, url)
        if len(list_of_links_by_gemeenten) != 0:
            for link in list_of_links_by_gemeenten:
                list_of_listing_links.append(link)  # Getting the listing links.
        else:
            print("No listings for - " + gemeenten)
    set_of_listing_links = dict.fromkeys(list_of_listing_links)  # Removing duplicate listing links.
    # Displaying the listing links on the console.
    print(len(set_of_listing_links))
    for link in set_of_listing_links:
        print(link)
    writeToJsonFile(set_of_listing_links)

if __name__ == "__main__":
    main()
