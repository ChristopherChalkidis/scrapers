import json
import re
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

mainDetails = {} #Holds information about the listing
detailsNeeded ={"Address","Rental price", "Deposit", "Rental Agreement", "Kind of house", "Living area", "Number of rooms", "Number of bath rooms", "Number of stories"}

URL = "https://www.funda.nl/en/huur/amsterdam/huis-42085123-cannenburg-15/" #URL for testing
page = requests.get(URL)

def getPageSource(URL):
    """Examines URL to return HTML for processing.

    Args:
        URL (string): The address of the website to parse

    Returns:
        HTML: The source HTML of the webpage passed in
    """
    s = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=s)
    driver.maximize_window()
    driver.get(URL)
    driver.implicitly_wait(10)
    page_source = driver.page_source

    driver.quit()
    return page_source

#TODO Get images for listing (3?)
#TODO Read-in listings json
#TODO Test with list of listings

source = getPageSource(URL)
soup = BeautifulSoup(source, "html.parser")
featureBody = soup.find(class_="object-kenmerken-body")

#Enters address as first entry for listing
mainDetails["Address"] = soup.find(class_="fd-m-top-none").text.strip()

def removeHTML(str):
    """Removes any HTML tags from each entry.
    
    Args:
        str (string): The entry details

    Returns:
        string: The original entry with no HTML tags
    """
    return re.sub("([\(\[]).*?([\)\]])", "", str)

def removeNames(features, details):
    """If the details list contains any of the feature names in features they are removed.
    
    Args:
        features (list): The name of every feature for the listing
        details (list): The detail for each feature for the listing

    Returns:
        list: The original list with all feature names removed
    """
    for feature in features:
        if feature in details:
            details.remove(feature)
    return details

def getDetails(items):
    """Processes each detail to remove HTML and duplicates
    
    Args:
        items (list): The detail for each feature for the listing

    Returns:
        list: The original list with all HTML and duplicate entries removed
    """
    details = []
    for detail in items:
        det = detail.text.strip().split("\n")
        for d in det:
            details.append(removeHTML(d))

    strippedDetails = []
    [strippedDetails.append(x) for x in details if x not in strippedDetails]
    return strippedDetails

def getFeatures(featName):
    """Removes the HTML and leading and trailing whitespace for each feature name.
    
    Args:
        features (list): The name of every feature for the listing

    Returns:
        list: The original list with all HTML and extraneous white space removed
    """
    features = []
    for feature in featName:
        features.append(removeHTML(feature.text.strip()))
    return features

def removeUnneeded(info):
    """Removes the entries from mainDetails that are not wanted. mainDetails is operated on directly.
    
    Args:
        info (list): A list of all the entries that aren't wanted

    Returns:
    """
    for key in info:
        del mainDetails[key]

#Gets list of all feature names in the HTML
features = getFeatures(featureBody.find_all("dt"))
#Gets list of all details in the HTML
details = getDetails(featureBody.find_all("dd"))

removeNames(features, details)

#Adds feature with detail entry to mainDetails
for f, d in zip(features, details):
    mainDetails[f] = d

#List of unneeded entries to remove
toRemove = [key for key in mainDetails if key not in detailsNeeded]
removeUnneeded(toRemove)

jsonOutput = json.dumps(mainDetails, indent=4)

#Writes mainDetails as json to a file
with open("listing.json", "w") as outfile:
    outfile.write(jsonOutput)

print(jsonOutput)