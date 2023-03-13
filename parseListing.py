import json
import re
import requests
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime

mainDetails = {} #Holds information about the listing
mainDetails["Photos"] = [] #Holds list of photo srcs
detailsNeeded =["Photos", "Address","Rental price", "Deposit", "Rental Agreement", "Kind of house", "Living area", "Number of rooms", "Number of bath rooms", "Number of stories", "URL", "Title", "Postal_code", "Asking price", "Listed since", "Year of construction", "Number of rooms", "Rental agreement", "Construction period"]
detailsNeededDutch = ["Photos", "Address", "Huurprijs", "Waarborgsom", "Huurovereenkomst", "Soort woonhuis", "Wonen", "Slaapkamers", "Aantal badkamers", "Aantal woonlagen", "URL", "Title", "Postal_code", "Vraagprijs", "Aangeboden sinds", "Bouwjaar", "Aantal kamers", "Huurovereenkomst", "Bouwperiode"]

#URL = "https://www.funda.nl/huur/bleiswijk/huis-88443766-van-kinsbergenstraat-11/" #Dutch URL for testing
#URL = "https://www.funda.nl/en/huur/amsterdam/huis-42085123-cannenburg-15/" #English URL for testing


#COMPLETE Get images for listing (3?)
#COMPLETE Read-in listings json
#COMPLETE Test with list of listings - Doesn't work if in Dutch
#COMPLETE Alter detailsNeeded to include Dutch names (Translate to English?)
#COMPLETE Needs debuging, etails are stored along with the wrong feats
#Maybe check if english or dutch by url
#Maybe store both english and dutch versions at the same time
#Edit config_adder so it creates a folder for the json files
#COMPLETE Remove all listings and create a json for each page
#COMPLETE URLs with variable references eg ?navigateSourve=resultlist return an error when creating a file. Should strip those refs
"""
#COMPLETE
Some listings fail to collect data. eg https://www.funda.nl/koop/verkocht/apeldoorn/appartement-42083357-ravelijn-350/
It seems that some pages have more than one div of class object-kenmerken-body
Those pages are the ones that are no longer available
"""
#COMPLETE Funda properties that no longer exist, crush the scrapper, need to check if available or continue

"""
#COMPLETE
Rent deposit data fetch fails
Must create a function that gets a url and returns "dutch or en" and "huur or koop"
If the page is about rent, then get the deposit manually and insert it in deposit list counterpart of Waarborgsom of the feature list
"""

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
            if d.__contains__("wordt berekend door de") or d == "" :
                continue
            if d.__contains__("is calculated by dividing") or d == "" :
                continue
            else:
                details.append(removeHTML(d))

    strippedDetails = []
    [strippedDetails.append(x) for x in details if x not in strippedDetails]
    return details

def getFeatures(featName):
    """Removes the HTML and leading and trailing whitespace for each feature name.
    
    Args:
        features (list): The name of every feature for the listing

    Returns:
        list: The original list with all HTML and extraneous white space removed
    """
    features = []
    for feature in featName:
        if feature.text.__contains__("Gebruiksoppervlakten"):
            continue
        else:
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
            mainDetails["Photos"].append(image["src"])

def stripURL(url):
    #Removes the variable reference from the URL
    for index, char in enumerate(url):
        if char == "?":
            return url[:index]
    return url

def checkEDRS(url):
    """Checks the language of the page and if its about sale or rent

    Args:
        URL: Just the full url of a page

    Returns:
     A list with 2 items:  [0] for en or nl, [1] for sale or koop
    """
    dt = url.split("/")
    info = []
    if "en" in dt:
        info.append("en")
    else:
        info.append("nl")
    if "koop" in dt:
        info.append("koop")
    elif "huur" in dt:
        info.append("huur")
    return info

def norm_dict(dict):
    #Capitalizes and replaces spaces with underscores in a dictionary's keys
    new_dict = {}
    for item in dict:
        new_item = item.replace(" ", "_")
        new_item = new_item.capitalize()
        new_dict[new_item] = dict[item]
    return new_dict

data = open("gemeenten_links_lite.json")
URLlist = json.load(data)
allListings = []
for url in URLlist:
    #print(f"URL: {url}")
    
    page = requests.get(url['20230117-151731'])

    source = getPageSource(url['20230117-151731'])
    soup = BeautifulSoup(source, "html.parser")
    featureBody = soup.find(class_="object-kenmerken-body")
    mainDetails ={}

    #Checks if the property is still available
    warning = soup.find(class_="notification-message-content")
    warning = str(warning)
    if warning.__contains__("Woning niet gevonden"):
        continue

    #Enters address as first entry for listing
    mainDetails["Address"] = soup.find(class_="fd-m-top-none").text.strip()
    mainDetails["URL"] = url['20230117-151731']
    mainDetails["Title"] = soup.find(class_="object-header__title").text.strip()
    mainDetails["Postal_code"] = soup.find(class_="object-header__subtitle fd-color-dark-3").text.strip()

    #Gets list of all feature names in the HTML
    features = getFeatures(featureBody.find_all("dt"))

    #If the property is rented or sold, then skip
    if "Verhuurdatum"in features:
        continue
    if "Verkoopdatum" in features:
        continue

    #Gets list of all details in the HTML
    details = getDetails(featureBody.find_all("dd", class_="fd-align-items-center"))
    
    #Get list of images
    photos = soup.find_all("img", class_="w-full")
    mainDetails["Photos"] = []
    addPhotos(photos)

    #Fetches the rental deposit and inserts it in the correct spot of the details list
    if checkEDRS(url['20230117-151731'])[1]  == "huur":
        depo = soup.find(class_="object-kenmerken-group-list")
        depo2 = depo.find("dd").text.strip()
        if checkEDRS(url['20230117-151731'])[0] == "nl":
            rr = "Waarborgsom"
        else:
            rr = "Deposit"
        details.insert(features.index(rr), depo2)

    removeNames(features, details)

    #Adds feature with detail entry to mainDetails
    for f, d in zip(features, details):
        #print(f"Feature: {f}: {d}")
        mainDetails[f] = d

    #Checks if listing is in English or Dutch
    if checkEDRS(url['20230117-151731'])[0] == "en":
        toRemove = [key for key in mainDetails if key not in detailsNeeded]
    else:
        toRemove = [key for key in mainDetails if key not in detailsNeededDutch]

    removeUnneeded(toRemove)
    #allListings.append(mainDetails)
    mainDetails = norm_dict(mainDetails)

    #Creates the name of the file
    url_name = str(url["20230117-151731"]).replace("https://", "")
    url_name = url_name.replace("/", "%2F")
    url_name = stripURL(url_name)
    x = time.time()
    date_time = datetime.fromtimestamp(x)
    str_date_time = date_time.strftime("%d-%m-%Y_%H-%M-%S")
    json_name = "listings/" +str_date_time + "_" + url_name + ".json"

    with open(json_name, "a") as outfile:
        outfile.write(json.dumps(mainDetails, indent=4))


#Writes allListings as json to a file
#Currently appends, this could be changed to a new file for each day
#with open("listing.json", "a") as outfile:
    #outfile.write(json.dumps(allListings, indent=4))