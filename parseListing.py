import json
import re
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

mainDetails = {} #Holds information about the listing
mainDetails["photos"] = [] #Holds list of photo srcs
detailsNeeded =["photos", "Address","Rental price", "Deposit", "Rental Agreement", "Kind of house", "Living area", "Number of rooms", "Number of bath rooms", "Number of stories"]
detailsNeededDutch = ["photos", "Address", "Huurprijs", "Waarborgsom", "Huurovereenkomst", "Soort woonhuis", "Wonen", "Slaapkamers", "Aantal badkamers", "Aantal woonlagen"]

#URL = "https://www.funda.nl/huur/bleiswijk/huis-88443766-van-kinsbergenstraat-11/" #Dutch URL for testing
#URL = "https://www.funda.nl/en/huur/amsterdam/huis-42085123-cannenburg-15/" #English URL for testing






#COMPLETE Get images for listing (3?)
#COMPLETE Read-in listings json
#COMPLETE Test with list of listings - Doesn't work if in Dutch
#COMPLETE Alter detailsNeeded to include Dutch names (Translate to English?)



# *** Methods *** #
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

def addPhotos(images):
    for image in images:
        if"https://cloud.funda.nl/valentina_media" in image["src"]:
            mainDetails["photos"].append(image["src"])

data = open("gemternten_links_20.json")
URLlist = json.load(data)
allListings = []
for url in URLlist:
    #print(f"URL: {url}")
    #print(url['20230117-151731'])

    page = requests.get(url['20230117-151731'])

    source = getPageSource(url['20230117-151731'])
    soup = BeautifulSoup(source, "html.parser")
    featureBody = soup.find(class_="object-kenmerken-body")

    #Enters address as first entry for listing
    mainDetails["Address"] = soup.find(class_="fd-m-top-none").text.strip()

    #Gets list of all feature names in the HTML
    features = getFeatures(featureBody.find_all("dt"))
    #Gets list of all details in the HTML
    details = getDetails(featureBody.find_all("dd"))
    #Get list of images
    photos = soup.find_all("img", class_="w-full")
    addPhotos(photos)

    removeNames(features, details)

    #Adds feature with detail entry to mainDetails
    for f, d in zip(features, details):
        #print(f"Feature: {f}: {d}")
        mainDetails[f] = d

    #Checks if listing is in English or Dutch
    if features[0] == "Rental price":
        toRemove = [key for key in mainDetails if key not in detailsNeeded]
    else:
        toRemove = [key for key in mainDetails if key not in detailsNeededDutch]

    removeUnneeded(toRemove)

    allListings.append(json.dumps(mainDetails, indent=4))

#Writes mainDetails as json to a file
#Currently appends, this could be changed to a new file for each day
#TODO proper formatting for mutliple dictionaries as json
with open("listing.json", "a") as outfile:
    outfile.write(allListings)

#print(jsonOutput)