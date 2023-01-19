import json
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


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

source = getPageSource(URL)
soup = BeautifulSoup(source, "html.parser")
mainStats = soup.find(class_="object-header__details")
features = soup.find(class_="object-kenmerken")
""" print(mainStats.prettify())
print(features.prettify()) """

details = mainStats.find_all("div")

# TODO isolate header details from code
for detail in details:
    print(detail.prettify())

""" address = soup.find(class_="fd-m-top-none").text.strip()
stats = soup.find(class_="kenmerken-highlighted").text.strip().split(" ")
#print(stats)

for info in stats :
    j = json.loads(info)
    print(j)

print(address)

def createJSON(): """

