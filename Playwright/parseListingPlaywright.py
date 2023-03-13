import json
import config
from playwright.async_api import async_playwright
import asyncio
from playwright_stealth import stealth_async
from datetime import date

scrapeDate = str(date.today())
cfg = config.read_config()

#URL = "https://www.funda.nl/huur/bleiswijk/huis-88443766-van-kinsbergenstraat-11/" #Dutch URL for testing
#URL = "https://www.funda.nl/en/huur/amsterdam/huis-42085123-cannenburg-15/" #English URL for testing

# *** Methods *** #
def readFile(inputFile) -> list:
    """Tries to open the passed in file
    
    :param {string} inputFile - The name of the file to be opened
    
    :return A list containing the urls of listings contained in the inputFile
    
    :throws exception if unable to find the file to open
    """
    try:
        openedFile = open(inputFile, "r")
        listingURLs = openedFile.read()
        openedFile.close()
        return listingURLs
    except Exception as err:
        print(err)

async def stillAvailable(page) -> bool:
    """Checks to see if the property displayed on the page is still available for rent or sale
    
    :param {page object} page - The browser page displaying a listing
    
    :return True - If definitief is not a classname on the page, 
    False - If definitief is a classname on the page
    """
    #Gets the object that contains the status of the listing: new, not available
    selElement = await page.wait_for_selector(
        ".object-header__labels ul li")
    #Gets the class list of the element found
    selClass = await selElement.get_attribute("class")

    return "definitief" not in str(selClass)

async def getDetail(elSelector, page) -> str:
    """Gets the string of the specified selector
    
    :param {string} elSelector - The selector to find the specified element
    :param {page object} page - The browser page displaying a listing

    :return The text of the element specified
    """ 
    el = page.locator(elSelector)
    return await el.inner_text()

async def getFeatures(page) -> list:
    """Gets the name and specifics of each detail listed on the page
    
    :param {page object} page - The browser page displaying a listing

    :return A list of small dictionaries of strings of all the details {title: name}
    """
    allFeatures = []

    #Selects all dt's that are children of the class
    allFeatureTitles = await page.query_selector_all(
        ".object-kenmerken-list dt")

    #Select all dd's that are immediately following a dt
    allFeatureDetails = await page.query_selector_all(
        ".object-kenmerken-list dt + dd") 
    
    for i in range(len(allFeatureTitles)):
        title = await allFeatureTitles[i].inner_text()
        detail = await allFeatureDetails[i].inner_text()
        allFeatures.append({title: detail})

    return allFeatures

async def getPhotos(page) -> list:
    """Gets all the photos on the page if they are photos of the listing
    
    :param {page object} page - The browser page displaying a listing
    
    :return A list containing the src to all the photos of the current listing"""
    photos = []
    images = await page.query_selector_all("a>img")
    
    for i in range(len(images)):
        imageSRC = await images[i].get_attribute("src")

        #Checks to see if it is one of the listing photos
        if"https://cloud.funda.nl/valentina_media" in imageSRC:
            photos.append(imageSRC)

    return photos

async def getInfo(page) -> dict:
    """Gets all the informatin for the listing that the page is at
    
    :param {page object} page - The browser page displaying a listing
    
    :return A dictionary containing the information: title, address, url, features, and photos
    """

    return {
        "title": await getDetail(
        ".object-header__title",page),
        "address": await getDetail(
        ".object-header__subtitle", page),
        "url": page.url,
        "features": await getFeatures(page),
        "photos": await getPhotos(page)
    }

async def isRental(listingInfo) -> bool:
    """Returns whether or not the listing in a rental
    huur - rent

    :param {dict} listingInfo - A dictionary containing all the information for each listing

    :return {bool} True - is a rental listing, False - is a sale listing
    """
    return "huur" in listingInfo["url"]

async def writeJson(fileName, listingInfo):
    """Writes the listing info to a file with the passed in fileName
    
    :param {string} fileName - The string containing the name the file will receive
    :param {dict} listingInfo - A dictionary containing all the information for each listing
    """
    with open(f"listings/{fileName}", "a") as outfile:
            outfile.write(json.dumps(listingInfo, indent=4))

async def writeToFile(listingInfo):
    """Checks to see if the listing is a rental or a sale and sets the filename accordingly
    
    :param {dict} listingInfo - A dictionary containing all the information for each listing
    """
    if await isRental(listingInfo):
        fileName = f"rental--{scrapeDate}--{listingInfo['address']}.json"
    else:
        fileName = f"sale--{scrapeDate}--{listingInfo['address']}.json"
    
    await writeJson(fileName, listingInfo)
        

async def run(link, page):
    """Runs the program to get information and write to a separate dated file for each listing
    
    :param {string} link - The url to the listing to scrape
    :param {page object} page - The browser page to use to visit the link
    """
    #Link for testing - listing is sold
    #link = "https://www.funda.nl/koop/verkocht/amsterdam/appartement-88459046-retiefstraat-23-3/"

    #Link for testing - listing is rented
    #link = "https://www.funda.nl/huur/verhuurd/amstelveen/appartement-88448601-spurgeonlaan-14/"
    await stealth_async(page)

    try:
        await page.goto(link)
        if await stillAvailable(page):
            await writeToFile(await getInfo(page))
    except Exception as err:
        print(f"Error {link} {err}")
    
testingDate = "2023-02-23"
async def main():
    """Reads the list of all the sales and rental links for each gemeenten"""
    #Use scrapeDate for live - It is set to today()
    links = readFile(f"{scrapeDate}Listings.txt")
    dailyURLs = links.splitlines()

    for link in dailyURLs:
        async with async_playwright() as player:
            #User agent must be set for stealth mode so the captcha isn't triggered in headless mode.
            ua = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/69.0.3497.100 Safari/537.36")
            browser = await player.chromium.launch(headless=True)
            page = await browser.new_page(user_agent=ua)
            await run(link, page)

if __name__ == "__main__":
    asyncio.run(main())