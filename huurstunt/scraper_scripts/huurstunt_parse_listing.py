import json
from playwright.async_api import async_playwright
import asyncio
from playwright_stealth import stealth_async
import datetime
import sys


# *** Methods *** #


async def write_file(fileName, listingInfo):
    """Writes the listing info to a file with the passed in fileName

    :param {string} fileName - The string containing the name the file will receive
    :param {dict} listingInfo - A dictionary containing all the information for each listing
    """
    with open(f"huurstunt/scraper_scripts/listings/{fileName}", "a") as outfile:
        outfile.write(json.dumps(listingInfo, indent=4))

scrapeDate = str(datetime.date.today())


async def set_file_name(listingInfo):
    """Sets the filename and passes the name and information to be written to file

    :param {dict} listingInfo - A dictionary containing all the information for each listing
    """

    fileName = f"rental--{scrapeDate}--{listingInfo['address']}.json"

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


async def getInfo(cut_off_date, page) -> dict:
    """Gets all the informatin for the listing that the page is at prior to the cut off date

    :param {date} cut_off_date - The listed date must be this day or after
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
    cut_off_date = (datetime.datetime.strptime(
        today, "%d-%m-%Y") - datetime.timedelta(days=1)).strftime("%d-%m-%Y")

    try:
        await page.goto(link)
        info = await getInfo(cut_off_date, page)
        if info:
            await set_file_name(info)
    except Exception as err:
        print(f"Error {link} {err}")


async def main():
    """
    Visits the Huurstunt all listings for the Netherlands and iterates through the listings
    getting their details until the cut off date is passed
    """

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

        for i in range(15):
            link = f"https://www.huurstunt.nl/huren/nederland/p{i+1}"
            await page.goto(link, wait_until="domcontentloaded")

            # Waits until the listing details are fully loaded
            await page.wait_for_selector(".boxed-widget--clean > div a")
            search_results = await page.query_selector_all(
                ".boxed-widget--clean > div a")

            links = []
            # Saves each listing link found to the links list for iteration after listing page is left
            for result in search_results:
                href = await result.get_attribute("href")
                links.append(href)
            # All the links found on the current page
            for link in links:
                if "/huren/" in href and "contact" not in href:
                    await run(f"{main_page}{link}", page)

        await ctx.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
