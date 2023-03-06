import json

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import config
"""
Issue #5
Convert municipality into a json file FOR PARARIUS.
"""

# Reading config file.
cfg = config.read_config()


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


def getWebPageSource(link):
    '''
        Function to retrieve the web page source.
        :param link: link to the webpage.
        :return:  HTML source of the webpage.
    '''
    options = Options()
    # Enables faster scraping
    #options.add_argument("--headless")  # Don't show browser
    # images aren't rendered
    # Starts driver for Chrome once before get the pages
    s = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=s, options=options)

    driver.get(link)
    # Wait until an element with id='myNewInput' has class 'myCSSClass'
    page_source = ""

    try:
        element = WebDriverWait(driver, 5).until(EC.title_contains(("Pararius")))
        page_source = driver.page_source
    except Exception as e:
        print(e.__class__)

    return page_source


def getErrorMessage(linkToPage):
    '''
        Function to retrieve the error message from the webpage.
        :param linkToPage: link to the webpage to extract the source.
        :return:  If the municipality is not found, the extract_of_error_message will be empty.
        :return:  If the municipality is found, the error message will have the text.
    '''
    soup = BeautifulSoup(getWebPageSource(linkToPage), 'html.parser')
    extract_of_error_message = soup.find_all("div", {"class": "notification__title"})
    return extract_of_error_message


def getLink(gemeenten):
    '''
        Function get normal link for gementeen.
        :param gemeenten: municipality to append to the link.
        :param propertyType: Rent or for sale (Koop or Huur).
        :return:  a link with the municipality and property type appended.
    '''
    base_url = "https://www.pararius.com/apartments/%s/"
    linkToPage = base_url % (gemeenten.replace(" ", "-").lower())
    return linkToPage


def isUrlValid(link):
    '''
        Function to validate the first url.
        :param link: link to be tested.
        :return:True is returned if the url works.
        :return:False is returned if the url doesn't work.
    '''
    extract_of_error_message = getErrorMessage(link)
    if len(extract_of_error_message) != 0 and extract_of_error_message[0].text.__contains__("Unfortunately this location cannot be found"):
        return False
    else:
        return True


def writeToJSONFile(muncipalities):
    """
        Function to write the json to the Json file.
        :param muncipalities: dictionary of all the municipalities and their links.
    """
    json_object = json.dumps(muncipalities, indent=4)
    with open(cfg["Other"]["gemeenten-json-names-pararius"], "w") as outfile:
        outfile.write(json_object)
    print("File write successful!")


def main():
    '''
        Main method.
    '''
    gemeenten_list = readGemeentenFromFile()  # Starting by reading the municipalities.
    muncipalities = {}  # Dictionary to store the municipalities.
    for gemeenten in gemeenten_list:
        municipalityLinks = {}  # Dictionary to store the links related to the municipality.
        if (isUrlValid(getLink(gemeenten))):  # Reading the first url.
            print("Website found successfully for URL - ", gemeenten)  # If the first url works.
            municipalityLinks["Pararius_Apartment"] = getLink(gemeenten).removeprefix("https://www.pararius.com")
        else:
            print("URL did not work for - ", gemeenten)  # If the first url doesn't work.

        muncipalities[gemeenten] = municipalityLinks  # Appending the links to the main dictionary.
    # Writing the data to the JSON file.
    writeToJSONFile(muncipalities)


if __name__ == "__main__":
    main()
