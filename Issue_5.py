import json

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import config
"""
Issue #5
Convert municipality into a json file #5
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
    s = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=s)
    driver.maximize_window()
    driver.get(link)
    page_source = driver.page_source
    driver.quit()
    return page_source


def getErrorMessage(linkToPage):
    '''
        Function to retrieve the error message from the webpage.
        :param linkToPage: link to the webpage to extract the source.
        :return:  If the municipality is not found, the extract_of_error_message will be empty.
        :return:  If the municipality is found, the error message will have the text.
    '''
    soup = BeautifulSoup(getWebPageSource(linkToPage), 'html.parser')
    extract_of_error_message = soup.find_all("span", {"class": "location-suggestions-header-content"})
    return extract_of_error_message


def getLink(gemeenten, propertyType):
    '''
        Function get normal link for gementeen.
        :param gemeenten: municipality to append to the link.
        :param propertyType: Rent or for sale (Koop or Huur).
        :return:  a link with the municipality and property type appended.
    '''
    base_url = "https://www.funda.nl/%s/%s/"
    linkToPage = base_url % (propertyType, gemeenten.replace(" ", "-").lower())
    return linkToPage


def getLinkForGementee(gemeenten, propertyType):
    '''
        Function get appended link for gementeen.
        :param gemeenten: municipality to append to the link.
        :param propertyType: Rent or for sale (Koop or Huur).
        :return:a link with the municipality and property type appended.
    '''
    base_url_gemeenten = "https://www.funda.nl/%s/gemeente-%s/"
    new_link = base_url_gemeenten % (propertyType, gemeenten.replace(" ", "-").lower())
    return new_link


def isUrlValid(link):
    '''
        Function to validate the first url.
        :param link: link to be tested.
        :return:True is returned if the url works.
        :return:False is returned if the url doesn't work.
    '''
    extract_of_error_message = getErrorMessage(link)
    if len(extract_of_error_message) != 0 and extract_of_error_message[0].text.__contains__("We kunnen"):
        return False
    else:
        return True


def writeToJSONFile(muncipalities):
    """
        Function to write the json to the Json file.
        :param muncipalities: dictionary of all the municipalities and their links.
    """
    json_object = json.dumps(muncipalities, indent=4)
    with open(cfg["Other"]["gemeenten-json-location"], "w") as outfile:
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
        if (isUrlValid(getLink(gemeenten, "koop"))):  # Reading the first url.
            print("Website found successfully for first URL - ", gemeenten)  # If the first url works.
            municipalityLinks["Funda_sale"] = getLink(gemeenten, "koop").removeprefix("https://www.funda.nl")
        else:
            print("First URL did not work for - ", gemeenten)  # If the first url doesn't work.

        if (isUrlValid(getLink(gemeenten, "huur"))):  # Reading the second url.
            print("Website found successfully for second URL - ", gemeenten)  # If the second url works.
            municipalityLinks["Funda_rent"] = getLink(gemeenten, "huur").removeprefix("https://www.funda.nl")
        else:
            print("Second URL did not work for - ", gemeenten)  # If the second url doesn't work.

        if (isUrlValid(getLinkForGementee(gemeenten, "koop"))):  # Reading the third url.
            print("Website found successfully for third URL - ", gemeenten)  # If the third url works.
            municipalityLinks["Funda-Gemeenten_sale"] = getLinkForGementee(gemeenten, "koop").removeprefix("https://www.funda.nl")
        else:
            print("Third URL did not work for - ", gemeenten)  # If the third url doesn't work.

        if (isUrlValid(getLinkForGementee(gemeenten, "huur"))):  # Reading the fourth url.
            print("Website found successfully for fourth URL - ", gemeenten)  # If the fourth url works.
            municipalityLinks["Funda-Gemeenten_rent"] = getLinkForGementee(gemeenten, "huur").removeprefix("https://www.funda.nl")
        else:
            print("Fourth URL did not work for - ", gemeenten)  # If the fourth url doesn't work.

        muncipalities[gemeenten] = municipalityLinks  # Appending the links to the main dictionary.
    # Writing the data to the JSON file.
    writeToJSONFile(muncipalities)


if __name__ == "__main__":
    main()
