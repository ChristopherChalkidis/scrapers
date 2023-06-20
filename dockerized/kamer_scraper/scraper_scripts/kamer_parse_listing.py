import json
from playwright.async_api import async_playwright
import asyncio
from playwright_stealth import stealth_async
from datetime import date


# *** Methods *** #


def readFile(inputFile: str) -> list:
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
    sections = await page.query_selector_all(".page__details")

    for section in sections:
        heading = await section.query_selector_all(".page__heading")

        if heading:
            heading_title = await heading[0].inner_text()
            allFeatureTitles = await section.query_selector_all(".listing-features__term")
            allFeatureDetails = await section.query_selector_all(".listing-features__description")

            for i in range(len(allFeatureTitles)):
                title = await allFeatureTitles[i].inner_text()
                detail = await allFeatureDetails[i].inner_text()
                allFeatures.append({heading_title+"-"+title: detail})

    return allFeatures


async def getPhotos(page) -> list:
    """Gets all the photos on the page if they are photos of the listing

    :param {page object} page - The browser page displaying a listing

    :return A list containing the src to all the photos of the current listing"""
    photos = set()
    images = await page.query_selector_all("#slider a img")

    for i in range(len(images)):
        photos.add(await images[i].get_attribute("src"))

    return list(photos)


async def getInfo(page) -> dict:
    """Gets all the informatin for the listing that the page is at

    :param {page object} page - The browser page displaying a listing

    :return A dictionary containing the information: title, address, url, features, and photos
    """
    try:

        await page.wait_for_selector("h1", timeout=5000)
        obj = {
            "title": await getDetail(
                "h1", page),
            "address": await getDetail(
                ".room-locatie .list-room-details:nth-child(2)", page),
            "url": page.url,
            # "features": await getFeatures(page),
            "photos": await getPhotos(page)
        }
        print(f"Oject {obj}")
        return obj
    except Exception as err:
        print(f"Couldn't find title {page.url} - {err}")


async def writeJson(fileName, listingInfo):
    """Writes the listing info to a file with the passed in fileName

    :param {string} fileName - The string containing the name the file will receive
    :param {dict} listingInfo - A dictionary containing all the information for each listing
    """
    with open(f"dockerized/kamer_scraper/scraper_scripts/listings/{fileName}", "a") as outfile:
        outfile.write(json.dumps(listingInfo, indent=4))


async def writeToFile(listingInfo):
    """Checks to see if the listing is a rental or a sale and sets the filename accordingly

    :param {dict} listingInfo - A dictionary containing all the information for each listing
    """

    fileName = f"rental--{scrapeDate}--{listingInfo['address']}.json"

    await writeJson(fileName.replace("/", "-"), listingInfo)


async def run(link, page):
    """Runs the program to get information and write to a separate dated file for each listing

    :param {string} link - The url to the listing to scrape
    :param {page object} page - The browser page to use to visit the link
    """
    try:
        await page.goto(link, wait_until="domcontentloaded", referer="https://www.google.com")
        info = await getInfo(page)
        if info:
            await writeToFile(info)
    except Exception as err:
        print(f"Error {link} {err}")

scrapeDate = str(date.today())


async def main():
    """Reads the list of all the sales and rental links for each gemeenten"""
    # Use scrapeDate for live - It is set to today()

    links = readFile(f"{scrapeDate}Listings.txt")
    dailyURLs = links.splitlines()

    async with async_playwright() as player:
        # User agent must be set for stealth mode so the captcha isn't triggered in headless mode.
        ua = ("Mozilla/5.0 (X11; Linux x86_64)"
              "AppleWebKit/537.36 (KHTML, like Gecko)"
              "Chrome/111.0.0.0 Safari/537.36")
        browser = await player.chromium.launch(headless=False, timeout=5000)
        ctx = await browser.new_context(user_agent=ua)
        page = await ctx.new_page()
        await stealth_async(page)

        for link in dailyURLs:
            await run(link, page)
        await ctx.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
