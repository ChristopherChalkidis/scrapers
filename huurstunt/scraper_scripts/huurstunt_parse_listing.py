import json
from playwright.async_api import async_playwright
import asyncio
from playwright_stealth import stealth_async
import datetime
import sys
import time

# URL = "https://www.funda.nl/huur/bleiswijk/huis-88443766-van-kinsbergenstraat-11/" #Dutch URL for testing
# URL = "https://www.funda.nl/en/huur/amsterdam/huis-42085123-cannenburg-15/" #English URL for testing

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


# async def getFeatures(page) -> list:
#     """Gets the name and specifics of each detail listed on the page

#     :param {page object} page - The browser page displaying a listing
#     :return A list of small dictionaries of strings of all the details {title: name}
#     """
#     allFeatures = []

#     # Selects all dt's that are children of the class
#     allFeatureTitles = await page.query_selector_all(
#         ".object-kenmerken-list dt")

#     # Select all dd's that are immediately following a dt
#     allFeatureDetails = await page.query_selector_all(
#         ".object-kenmerken-list dt + dd")

#     for i in range(len(allFeatureTitles)):
#         title = await allFeatureTitles[i].inner_text()
#         detail = await allFeatureDetails[i].inner_text()
#         allFeatures.append({title: detail})

#     return allFeatures

async def get_noscript(txt):
    split_str = await txt.inner_html()
    links = set()
    for i in str(split_str).strip().split(" "):
        if "https://casco-media-prod.global.ssl.fastly.net" in i:
            links.add(i[i.find('http'):])
    return links


async def writeJson(fileName, listingInfo):
    """Writes the listing info to a file with the passed in fileName

    :param {string} fileName - The string containing the name the file will receive
    :param {dict} listingInfo - A dictionary containing all the information for each listing
    """
    with open(f"huurstunt/scraper_scripts/listings/{fileName}", "a") as outfile:
        outfile.write(json.dumps(listingInfo, indent=4))


async def writeToFile(listingInfo):
    """Checks to see if the listing is a rental or a sale and sets the filename accordingly

    :param {dict} listingInfo - A dictionary containing all the information for each listing
    """

    fileName = f"rental--{scrapeDate}--{listingInfo['address']}.json"

    await writeJson(fileName.replace(" / ", "-").strip(), listingInfo)


async def getPhotos(page) -> list:
    """Gets all the photos on the page if they are photos of the listing

    :param {page object} page - The browser page displaying a listing

    :return A list containing the src to all the photos of the current listing"""
    photos = set()
    images = await page.query_selector_all(".rental-image-gallery__link img")

    noscript_links = await page.query_selector("noscript")
    image_links = await get_noscript(noscript_links)
    for image in image_links:
        photos.add(image)
    for i in range(len(images)):
        imageSRC = await images[i].get_attribute("src")
        # Checks to see if it is one of the listing photos
        # if "https://casco-media-prod.global.ssl.fastly.net" in imageSRC:
        photos.add(imageSRC)

    return list(photos)


async def getFeatures(page) -> list:
    """Gets the name and specifics of each detail listed on the page

    :param {page object} page - The browser page displaying a listing
    :return A list of small dictionaries of strings of all the details {title: name}
    """
    allFeatures = []
    sections = await page.query_selector_all(".info-wrapper")

    for section in sections:
        heading_title = await section.query_selector_all(".info-wrapper__header > h5")
        blocks = await section.query_selector_all(".info-wrapper__block")

        for block in blocks:
            allFeatureTitles = await block.query_selector_all(".info-wrapper__key >p")
            allFeatureDetails = await block.query_selector_all(".info-wrapper__value >p")

            for i in range(len(allFeatureTitles)):
                section_heading = await heading_title[i].inner_text()
                title = await allFeatureTitles[i].inner_text()
                detail = await allFeatureDetails[i].inner_text()
                allFeatures.append(f"{section_heading} - {title}: {detail}")

    print(f"Number of features: {len(allFeatures)}")
    return allFeatures


async def getDetail(elSelector, page) -> str:
    """Gets the string of the specified selector

    :param {string} elSelector - The selector to find the specified element
    :param {page object} page - The browser page displaying a listing
    :return The text of the element specified
    """
    el = page.locator(elSelector)
    return await el.inner_text()


async def getInfo(cut_off_date, page) -> dict:
    """Gets all the informatin for the listing that the page is at

    :param {page object} page - The browser page displaying a listing

    :return A dictionary containing the information: title, address, url, features, and photos
    """
    try:

        await page.wait_for_selector(".title__listing", timeout=5000)
        # Get the listed next to "Home active since" text - this is the date the home was listed
        posted_date = await page.query_selector_all(
            ".info-wrapper__value:near(:text('Woning actief sinds'))")
        posted_str = await posted_date[0].inner_text()

        # If the date the house was posted is before the cut_off_date (2 days prior to current) then exit the program
        if posted_str < cut_off_date:
            sys.exit(0)
        else:
            return {
                "title": await getDetail(
                    ".title__listing", page),
                "address": await getDetail(
                    ".first-block p", page),
                "url": page.url,
                "features": await getFeatures(page),
                "photos": await getPhotos(page)
            }
    except Exception as err:
        print(f"Couldn't find detail {page.url} - {err}")


async def run(link, page):
    """Runs the program to get information and write to a separate dated file for each listing

    :param {string} link - The url to the listing to scrape
    :param {page object} page - The browser page to use to visit the link
    """

    today = datetime.date.today().strftime('%d-%m-%Y')
    print(f"Today: {today}")
    cut_off_date = (datetime.datetime.strptime(
        today, "%d-%m-%Y") - datetime.timedelta(days=1)).strftime("%d-%m-%Y")
    print(f"Cut off: {cut_off_date}")

    try:
        await page.goto(link, wait_until="domcontentloaded")
        info = await getInfo(cut_off_date, page)
        if info:
            await writeToFile(info)
    except Exception as err:
        print(f"Error {link} {err}")

scrapeDate = str(datetime.date.today())

test_link = "https://www.huurstunt.nl/huurwoning/huren/in/amsterdam/paul-scholtenstraat/HK5BI"


async def main():
    """Reads the list of all the sales and rental links for each gemeenten"""
    # Use scrapeDate for live - It is set to today()

    """ links = readFile(f"{scrapeDate}Listings.txt")
    dailyURLs = links.splitlines() """

    async with async_playwright() as player:
        # User agent must be set for stealth mode so the captcha isn't triggered in headless mode.
        ua = ("Mozilla/5.0 (X11; Linux x86_64)"
              "AppleWebKit/537.36 (KHTML, like Gecko)"
              "Chrome/111.0.0.0 Safari/537.36")
        browser = await player.chromium.launch(headless=False, timeout=5000)
        ctx = await browser.new_context(user_agent=ua)
        page = await ctx.new_page()
        await stealth_async(page)

        """ main_page = "https://www.huurstunt.nl/huren/nederland/"
        await page.goto(main_page, wait_until="domcontentloaded") """

        """ pages = await page.query_selector_all("a")
        print(f"Pages {len(pages)}") """

        # await run(test_link, page)
        for i in range(15):
            link = f"https://www.huurstunt.nl/huren/nederland/p{i+1}"
            await page.goto(link, wait_until="domcontentloaded")
            print(f"Listings page {i+1}")
            # search_results = page.locator('a[href*="/huren/"]')
            await page.wait_for_selector(".boxed-widget--clean > div a")
            search_results = await page.query_selector_all(
                ".boxed-widget--clean > div a")
            print(f"There were {len(search_results)} links found")

            for result in search_results:
                href = await result.get_attribute("href")
                print(f"link {href}")
                """if "/huren/" in href:
                    await run(f"{href}", page) """
        await ctx.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
