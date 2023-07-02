import json
from playwright.async_api import async_playwright
import asyncio
from playwright_stealth import stealth_async
from datetime import date
import os.path


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


""" async def stillAvailable(page) -> bool:
    Checks to see if the property displayed on the page is still available for rent or sale

    :param {page object} page - The browser page displaying a listing

    :return True - If definitief is not a classname on the page, 
    False - If definitief is a classname on the page
    
    # Gets the object that contains the status of the listing: new, not available
    selElement = await page.wait_for_selector(
        ".object-header__labels ul li")
    # Gets the class list of the element found
    selClass = await selElement.get_attribute("class")

    return "definitief" not in str(selClass) """


async def getDetail(elSelector, page) -> str:
    """Gets the string of the specified selector

    :param {string} elSelector - The selector to find the specified element
    :param {page object} page - The browser page displaying a listing
    :return The text of the element specified
    """
    el = page.locator(elSelector)
    return await el.inner_text()


async def getAddress(elSelector, page) -> str:
    """ Gets the address string and cleans it

    :param {string} elSelector - The selector to find the specified element
    :param {page object} page - The browser page displaying a listing
    :return The text of the element specified
    """

    el = page.locator(elSelector)
    txt = await el.inner_text()
    tmp = txt.split("\n")
    return f"{tmp[3]} {tmp[1]} {tmp[5]}"

# TODO Second section of details under main details.


async def getFeatures(page) -> list:
    """Gets the name and specifics of each detail listed on the page

    :param {page object} page - The browser page displaying a listing
    :return A list of small dictionaries of strings of all the details {title: name}
    """
    allFeatures = {}
    inner = await page.query_selector(".content-inner-wrap")
    main_details = await inner.query_selector_all(".list-room-details-iconized")
    extra_details = await inner.query_selector_all(".list-room-details-iconized + .list-room-details li")
    prop_details = await inner.query_selector_all(".list-room-details-wrap ul li")
    all_details = extra_details + prop_details

    for detail in main_details:
        txt = await detail.inner_text()
        tmp = txt.split("\n")
        allFeatures["Price"] = tmp[0]
        allFeatures["Size"] = tmp[1]

    for detail in all_details:
        txt = await detail.inner_text()
        tmp = txt.split(":\n")
        allFeatures[tmp[0]] = tmp[1]

    return allFeatures


async def getDescription(page):
    """Checks to see if there is a description available on the page and returns it if there is

    :param {page object} page - The browser page displaying a listing

    :return A string containing the description of the house or "N/A" if no description available
"""
    try:
        desc = page.locator(".room-description")
        return await desc.inner_text()
    except Exception as err:
        return f"Description {err}"


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
            "address": await getAddress(
                ".room-locatie .list-room-details:has-text('Straat: ')", page),
            "url": page.url,
            "features": await getFeatures(page),
            "description": await getDescription(page),
            "photos": await getPhotos(page)
        }
        return obj
    except Exception as err:
        print(f"Couldn't find title {page.url} - {err}")


async def writeJson(fileName, listingInfo):
    """Writes the listing info to a file with the passed in fileName

    :param {string} fileName - The string containing the name the file will receive
    :param {dict} listingInfo - A dictionary containing all the information for each listing
    """
    with open(f"dockerized/kamer_scraper/scraper_scripts/listings/{fileName}", "w") as outfile:
        outfile.write(json.dumps(listingInfo, indent=4))


async def writeToFile(listingInfo):
    """Checks to see if the listing is a duplicate name and sets the filename accordingly

    :param {dict} listingInfo - A dictionary containing all the information for each listing
    """
    fileName = f"rental--{scrapeDate}--{listingInfo['address']}".replace(
        ' ', '-')
    if os.path.isfile(f"dockerized/kamer_scraper/scraper_scripts/listings/{fileName}.json"):
        fileName = fileName + " (1)"

    await writeJson(f"{fileName}.json", listingInfo)


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
