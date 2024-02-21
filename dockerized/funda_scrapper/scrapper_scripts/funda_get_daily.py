import json
import re
import math
from playwright.async_api import async_playwright
import asyncio
from undetected_playwright import stealth_async
from datetime import date

# TODO page routing to exclude resources slows down the program significantly. Why?

# For portablity of the script
# dirname = os.path.dirname(os.path.abspath(__file__))


async def excludeResources(route):
    """ Takes in the route of the page being visited and prevents the loading of images, fonts, and media

    :param {route} route - The path the page is taking to get to the destination

    :return null
    """
    toExclude = ["image", "font", "media", "script"]
    if route.request.resource_type in toExclude:
        route.abort
    else:
        await route.continue_()


""" async def readFile(file) -> list:
    Gets all the links for each gemeenten from the file and returns a list of them

    :param {file} file - The file containing the links to the past days rentals and sales listings for each gemeenten

    :return {list} - The list of links to check
    

    with open(file, "r") as file:
        dat a = json.load(file)
    return data"""


async def getNumPages(page) -> int:
    try:
        pages = page.locator(".pagination li")
        # subtracting two to account for back and next links
        return await pages.count()-2

    except Exception as err:
        print(f"getNumPages error {page.url} {err}")


async def getLinks(link, page) -> set:
    gemeentenLinks = set()
    try:
        # await page.route("**/*",excludeResources)
        await page.goto(link)

        links = await page.query_selector_all("css=a")

        for link in links:
            source = await link.get_attribute("href")
            if source and len(source) > 50 and "https://www.funda.nl/koop/" in source:
                gemeentenLinks.add(source)

        return gemeentenLinks
    except Exception as err:
        print(f"getLinks error {link} {err}")


def combineLinkSets(linksSets) -> list:
    linksList = []
    for links in linksSets:
        for link in links:
            linksList.append(link)

    return linksList


scrapeDate = str(date.today())


def writeToFile(links):
    # filename = os.path.join(dirname, f"../listings/{scrapeDate}Listings.txt")
    try:
        with open(f"/app/listings/{scrapeDate}Listings.txt", "w") as outfile:
            for link in links:
                outfile.write(link+"\n")
        print("File write successful!")
    except Exception as err:
        print(f"writeToFile error {err}")


async def main():
    dailyLinks = []

    async with async_playwright() as player:
        browser = await player.chromium.launch(headless=True)
        # User agent must be set for stealth mode so the captcha isn't triggered in headless mode.
        # ua = (
        #     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        #     "AppleWebKit/537.36 (KHTML, like Gecko) "
        #     "Chrome/86.0.4240.198 Safari/537.36")
        ua = (
            "Mozilla/5.0 (X11; Linux x86_64)"
            "AppleWebKit/537.36 (KHTML, like Gecko)"
            "Chrome/113.0.0.0 Safari/537.36"
        )

        ctx = await browser.new_context(user_agent=ua)
        await stealth_async(ctx)
        page = await ctx.new_page()
        link = "https://www.funda.nl/zoeken/koop?selected_area=%5B%22nl%22%5D&publication_date=%221%22"
        await page.goto(link)
        numPages = await getNumPages(page)
        for pg in range(numPages):
            link = f"https://www.funda.nl/zoeken/koop?selected_area=%5B%22nl%22%5D&publication_date=%221%22&search_result={pg+1}"
            dailyLinks.append(await getLinks(link, page))
    allLinks = combineLinkSets(dailyLinks)
    writeToFile(allLinks)

if __name__ == "__main__":
    asyncio.run(main())
