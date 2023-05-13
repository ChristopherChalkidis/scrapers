import json
from playwright.async_api import async_playwright
import asyncio
from playwright_stealth import stealth_async
from datetime import date, datetime


# URL = "https://www.funda.nl/huur/bleiswijk/huis-88443766-van-kinsbergenstraat-11/" #Dutch URL for testing
# URL = "https://www.funda.nl/en/huur/amsterdam/huis-42085123-cannenburg-15/" #English URL for testing

featuresNeeded = ["Listed since", "Type apartment", "Kind of house", "Living area", "Number of rooms", "Number of bath rooms",
                  "Number of stories", "Year of construction", "Asking price", "Rental price", "Rental agreement", "Deposit"]

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
    # Gets the object that contains the status of the listing: new, not available
    selElement = await page.wait_for_selector(
        ".object-header__labels ul li")
    # Gets the class list of the element found
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

    # Selects all dt's that are children of the class
    allFeatureTitles = await page.query_selector_all(
        ".object-kenmerken-list dt")

    # Select all dd's that are immediately following a dt
    allFeatureDetails = await page.query_selector_all(
        ".object-kenmerken-list dt + dd")

    for i in range(len(allFeatureTitles)):
        title = await allFeatureTitles[i].inner_text()
        if title.strip() in featuresNeeded:
            title = title.strip().lower().replace(" ", "_")
            detail = await allFeatureDetails[i].inner_text()
            allFeatures.append({title: detail})

    return allFeatures


async def getPhotos(page) -> list:
    """Gets all the photos on the page if they are photos of the listing

    :param {page object} page - The browser page displaying a listing

    :return A list containing the src to all the photos of the current listing"""
    photos = []
    images = await page.query_selector_all(".object-media-fotos a>img")

    for i in range(len(images)):
        imageSRC = await images[i].get_attribute("src")

        # Checks to see if it is one of the listing photos
        if "https://cloud.funda.nl/valentina_media" in imageSRC:
            photos.append(imageSRC)

    return photos


async def getInfo(page) -> dict:
    """Gets all the informatin for the listing that the page is at

    :param {page object} page - The browser page displaying a listing

    :return A dictionary containing the information: title, address, url, features, and photos
    """
    try:
        await page.wait_for_selector(".object-header__title", timeout=2000)
        return {
            "address": await getDetail(
                ".object-header__title", page),
            "postal_code": await getDetail(
                ".object-header__subtitle", page),
            "url": page.url,
            "features": await getFeatures(page),
            "photos": await getPhotos(page)
        }
    except Exception:
        return {"apartment-complex": page.url}
        print(f"Couldn't find title {page.url} - {err}")


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
    with open(f"../listings/{fileName}", "a") as outfile:
        outfile.write(json.dumps(listingInfo, indent=4))


async def normaliseURL(URL):
    """ This function takes in a URL string and returns a normalized URL string.

    :param {string} URL - The input URL string to be normalized
    """
    return URL[8:].replace("/", "%2F")


async def enURL(URL):
    """Returns a modified URL string that points to the English version of the current page.

    :param {string} URL - The input URL string to be modified.
    """
    return URL[:21] + "en" + URL[20:]

scrapeDate = str(date.today())


async def writeToFile(listingInfo):
    """Checks to see if the listing is a rental or a sale and sets the filename accordingly

    :param {dict} listingInfo - A dictionary containing all the information for each listing
    """
    url_final = await normaliseURL(listingInfo["url"])

    now = datetime.now()
    current_time = now.strftime("%H-%M-%S")

    fileName = f"{scrapeDate}_{current_time}_{url_final}.json"

    await writeJson(fileName.replace("/", "-"), listingInfo)


async def run(link, page):
    """Runs the program to get information and write to a separate dated file for each listing

    :param {string} link - The url to the listing to scrape
    :param {page object} page - The browser page to use to visit the link
    """
    # Link for testing - listing is sold
    # link = "https://www.funda.nl/koop/verkocht/amsterdam/appartement-88459046-retiefstraat-23-3/"

    # Link for testing - listing is rented
    # link = "https://www.funda.nl/huur/verhuurd/amstelveen/appartement-88448601-spurgeonlaan-14/"

    try:
        await page.goto(link, wait_until="domcontentloaded")
        # if await stillAvailable(page):
        info = await getInfo(page)
        if info:
            await writeToFile(info)
    except Exception as err:
        print(f"Error {link} {err}")

async def main():
    """Reads the list of all the sales and rental links for each gemeenten"""
    # Use scrapeDate for live - It is set to today()

    links = readFile(f"../listings/{scrapeDate}Listings.txt")
    dailyURLs = links.splitlines()

    async with async_playwright() as player:
        # User agent must be set for stealth mode so the captcha isn't triggered in headless mode.
        # ua = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        #       "AppleWebKit/537.36 (KHTML, like Gecko) "
        #       "Chrome/69.0.3497.100 Safari/537.36")
        ua = ("Mozilla/5.0 (X11; Linux x86_64)"
            "AppleWebKit/537.36 (KHTML, like Gecko)"
            "Chrome/113.0.0.0 Safari/537.36")
        browser = await player.chromium.launch(headless=True, timeout=5000)
        ctx = await browser.new_context(user_agent=ua)
        page = await ctx.new_page()
        await stealth_async(page)

        for link in dailyURLs:
            enlink = await enURL(link)
            # await page.goto(link,wait_until="domcontentloaded")

            await run(enlink, page)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
