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
    s = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=s)
    driver.maximize_window()
    driver.get(URL)
    driver.implicitly_wait(10)
    page_source = driver.page_source

    driver.quit()
    return page_source

#TODO Better commenting
#TODO Get images for listing (3?)
#TODO Readin listings json
#TODO Test with list of listings

source = getPageSource(URL)
soup = BeautifulSoup(source, "html.parser")
featureBody = soup.find(class_="object-kenmerken-body")

mainDetails["Address"] = soup.find(class_="fd-m-top-none").text.strip()

def removeHTML(str):
    return re.sub("([\(\[]).*?([\)\]])", "", str)

#Get address
details = soup.find_all(class_="kenmerken-highlighted__value")

def removeNames(features, details):
    for feature in features:
        if feature in details:
            details.remove(feature)
    return details

def getDetails(items):
    details = []
    for detail in items:
        det = detail.text.strip().split("\n")
        for d in det:
            details.append(removeHTML(d))

    strippedDetails = []
    [strippedDetails.append(x) for x in details if x not in strippedDetails]
    return strippedDetails

def getFeatures(featName):
    features = []
    for feature in featName:
        features.append(removeHTML(feature.text.strip()))
    return features

def removeUnneeded(info):
    for key in info:
        del mainDetails[key]

features = getFeatures(featureBody.find_all("dt"))
details = getDetails(featureBody.find_all("dd"))

removeNames(features, details)

for f, d in zip(features, details):
    mainDetails[f] = d

toRemove = [key for key in mainDetails if key not in detailsNeeded]
removeUnneeded(toRemove)

jsonOutput = json.dumps(mainDetails, indent=4)

with open("listing.json", "w") as outfile:
    outfile.write(jsonOutput)

print(jsonOutput)