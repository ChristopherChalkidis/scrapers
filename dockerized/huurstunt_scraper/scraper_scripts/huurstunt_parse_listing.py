import json
from playwright.async_api import async_playwright
import asyncio
from playwright_stealth import stealth_async
import datetime
import re
import sys


# *** Methods *** #

""" def readFile(inputFile: str) -> str:
    Tries to open the passed in file

    :param {string} inputFile - The name of the file to be opened

    :return A list containing the urls of listings contained in the inputFile

    :throws exception if unable to find the file to open
    
    try:
        openedFile = open(inputFile, "r")
        listingURLs = openedFile.read()
        openedFile.close()
        return listingURLs
    except Exception as err:
        print(err) """

async def write_file(fileName, listingInfo):
    """Writes the listing info to a file with the passed in fileName

    :param {string} fileName - The string containing the name the file will receive
    :param {dict} listingInfo - A dictionary containing all the information for each listing
    """
    #with open(f"dockerized/huurstunt_scraper/listings/{fileName}", "a") as outfile:
    with open(f"/app/listings/{fileName}", "a") as outfile:
        outfile.write(json.dumps(listingInfo, indent=4))

scrape_date = str(datetime.date.today())


async def set_file_name(listingInfo):
    """Sets the filename and passes the name and information to be written to file

    :param {dict} listingInfo - A dictionary containing all the information for each listing
    """

    fileName = f"rental--{scrape_date}--{listingInfo['address']}.json"

    await write_file(fileName.replace(" / ", "-").strip(), listingInfo)


async def getPhotos(page) -> list:
    """Gets all the photos on the page if they are photos of the listing

    :param {page object} page - The browser page displaying a listing

    :return A list containing the src to all the photos of the current listing
    """

    photos = set()
    images = await page.query_selector_all(".rental-image-gallery__link img")

    for i in range(len(images)):
        imageSRC = await images[i].get_attribute("src")
        photos.add(imageSRC)

    return list(photos)


async def getFeatures(page) -> list:
    """Gets the name and specifics of each detail listed on the page

    :param {page object} page - The browser page displaying a listing
    :return A list of small dictionaries of strings of all the details {title: detail}
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

    return allFeatures


async def getDetail(elSelector, page) -> str:
    """Gets the string of the specified selector

    :param {string} elSelector - The selector to find the specified element
    :param {page object} page - The browser page displaying a listing
    :return The text of the element specified
    """
    el = page.locator(elSelector)
    return await el.inner_text()


async def is_too_old(posted)-> bool:
    today = datetime.date.today().strftime('%d-%m-%Y')
    cut_off_date = (datetime.datetime.strptime(
        today, "%d-%m-%Y") - datetime.timedelta(days=1)).strftime("%d-%m-%Y")
    posted_str = await posted[0].inner_text()
    date_ddmmyyy = r"(\d{2})-(\d{2})-(\d{4})"

    searched = re.search(date_ddmmyyy, posted_str)
    converted_date = ""
    if searched:
        searched = searched.group()
        converted_date = datetime.datetime.strptime(searched, "%d-%m-%Y").date().strftime("%d-%m-%Y")
        return converted_date < cut_off_date
    
    return False

async def getInfo(page):
    """Gets all the informatin for the listing that the page is at prior to the cut off date

    :param {date} cut_off_date - The listed date must be this day or after
    :param {page object} page - The browser page displaying a listing

    :return A dictionary containing the information: title, address, url, features, and photos
    """
    try:
        await page.wait_for_selector(".title__listing", timeout=10000)
        
        # Get the listed next to "Home active since" text - this is the date the home was listed
        posted_date = await page.query_selector_all(
            ".info-wrapper__block:near(:text('Woning actief sinds'))")

        # If the date the house was posted is before the cut_off_date (2 days prior to current) then exit the program
        if await is_too_old(posted_date):
            print(f"All new listings have been checked")
            sys.exit(0)
        else:
            return {
                "title": await getDetail(
                    ".title__listing", page),
                "address": await getDetail(
                    ".title__sub", page),
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


    try:
        await page.goto(link)
        info = await getInfo(page)
        if info:
            await set_file_name(info)
    except Exception as err:
        print(f"Error {link} {err}")

def valid_link(link) -> bool:
    return "/huren/" in link and "contact" not in link

def is_rented(html) -> bool:
    #Check if it's already been rented
    return "property-type property--red" in html

def is_restricted(html) -> bool:
    #Check if the property details are behind a login
    return "link-container__greenlist__overlay" in html

async def main():
    """
    Visits the Huurstunt all listings for the Netherlands and iterates through the listings
    getting their details until the cut off date is passed
    """
    print("running")


    async with async_playwright() as player:
        # User agent must be set for stealth mode so the captcha isn't triggered in headless mode.
        ua = ("Mozilla/5.0 (X11; Linux x86_64)"
              "AppleWebKit/537.36 (KHTML, like Gecko)"
              "Chrome/111.0.0.0 Safari/537.36")
        browser = await player.chromium.launch(headless=True, timeout=5000)
        ctx = await browser.new_context(user_agent=ua)
        page = await ctx.new_page()
        await stealth_async(page)

        main_page = "https://www.huurstunt.nl"
        links = []

        main_link = f"https://www.huurstunt.nl/huren/nederland/"
        await page.goto(main_link, wait_until="domcontentloaded")
        check_next = page.locator(".fa fa-chevron-right")
        page_num = 2
        
        while check_next != 0:

            #Checks if it's made it to the last page or not
            if check_next == 0:
                sys.exit(0)

            # Waits until the listing details are fully loaded
            await page.wait_for_selector(".boxed-widget--clean > div")
            search_results = await page.locator(".boxed-widget--clean > div").all()

            # Saves each listing link found to the links list for iteration after listing page is left
            for result in search_results:
                html = await result.inner_html()

                if not is_restricted(html) and not is_rented(html):
                    link_el = result.get_by_role("link").first
                    href = await link_el.get_attribute("href")
                    if valid_link(href):
                        links.append(f"{main_page}{href}")
            
            for link in links:
                await run(link, page)

            await page.goto(f"{main_link}p{page_num}")
            page_num+=1
    

        await ctx.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
