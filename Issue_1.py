from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import config

"""
Issue #1

The goal is to use the attached file and verify if the gemeenten (i.e. municipalities) are valid.
Base URL: https://www.funda.nl/koop/heerhugowaard/1-dag/

replace heerhugowaard with all the entries in the file and verify of the response is 200
"""
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


def isFirstUrlValid(gemeenten):
    '''
        Function to validate if the first URL is valid.
        :param gemeenten: Municipalitie to validate.
        :return:True is returned if the url works.
        :return:False is returned if the url doesn't work.
    '''
    base_url = "http://www.funda.nl/koop/%s"
    linkToPage = base_url % gemeenten.replace(" ", "-").lower()
    extract_of_error_message = getErrorMessage(linkToPage)
    if len(extract_of_error_message) != 0 and extract_of_error_message[0].text.__contains__("We kunnen"):
        return False
    else:
        return True

def isSecondURLValid(gemeenten):
    '''
        Function to validate if the second URL is valid.
        :param gemeenten: Municipalitie to validate.
        :return:True is returned if the url works.
        :return:False is returned if the url doesn't work.
    '''
    base_url_gemeenten = "https://www.funda.nl/koop/gemeente-%s"
    new_link = base_url_gemeenten % gemeenten.replace(" ", "-").lower()
    extract_of_error_message = getErrorMessage(new_link)
    if len(extract_of_error_message) != 0 and extract_of_error_message[0].text.__contains__("We kunnen"):
        return False
    else:
        return True


def main():
    '''
    Main method.
    '''
    gemeenten_list = readGemeentenFromFile() # Starting my reading the municipalities.
    for gemeenten in gemeenten_list:
        if (isFirstUrlValid(gemeenten)):  # Reading the first url.
            print("Website found successfully for first URL - ", gemeenten)  # If the first url works.
        else:
            print("First URL did not work for - ", gemeenten)  # If both urls don't work.

        if (isSecondURLValid(gemeenten)): # Reading the second url.
            print("Website found successfully for second URL - ", gemeenten)  # If the first url works.
        else:
            print("Second URL did not work for - ", gemeenten)  # If both urls don't work.

if __name__ == "__main__":
    main()


