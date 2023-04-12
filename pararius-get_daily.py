import json
import config
import re
import math
from playwright.async_api import async_playwright
import asyncio
from undetected_playwright import stealth_async
from datetime import date

cfg = config.read_config()

# TODO page routing to exclude resources slows down the program significantly. Why?


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


async def readFile(file) -> list:
    """ Gets all the links for each gemeenten from the file and returns a list of them

    :param {file} file - The file containing the links to the past days rentals and sales listings for each gemeenten

    :return {list} - The list of links to check
    """

    with open(file, "r") as file:
        data = json.load(file)
    return data


async def getNumPages(page) -> int:
    try:
        getNumResults = page.locator(".search-list-header__count")
        txt = await getNumResults.inner_text()
        pat = "\\d+"
        numResults = re.findall(pat, txt)
        numResults = int(numResults[0])
        return math.ceil(numResults/30)

    except Exception as err:
        print(f"getNumPages error {page.url} {err}")


async def getLinks(page) -> set:
    gemeentenLinks = set()
    try:
        # await page.route("**/*",excludeResources) - Seems to slow down load, but can't figure out why

        # Selects all links within the search-resuls class where the link element contains an element with the class search-result_header-title
        links = await page.query_selector_all(
            ".listing-search-item__link--title")
        for i in range(len(links)):
            el = links[i]
            source = await el.get_attribute("href")

            gemeentenLinks.add("https://www.pararius.com"+source)

        return gemeentenLinks
    except Exception as err:
        print(f"getLinks error {page.url()} {err}")


def combineLinkSets(linksSets) -> list:
    linksList = []
    for links in linksSets:
        for link in links:
            linksList.append(link)

    return linksList


scrapeDate = str(date.today())


def writeToFile(links):
    try:
        with open(f"{scrapeDate}Listings.txt", "w") as outfile:
            for link in links:
                outfile.write(link+"\n")
        print("File write successful!")
    except Exception as err:
        print(f"writeToFile error {err}")


async def main():
    dailyLinks = []

    async with async_playwright() as player:
        browser = await player.chromium.launch(headless=False)
        # User agent must be set for stealth mode so the captcha isn't triggered in headless mode.
        ua = ("Mozilla/5.0 (X11; Linux x86_64)"
              "AppleWebKit/537.36 (KHTML, like Gecko)"
              "Chrome/111.0.0.0 Safari/537.36")
        page = await browser.new_page(user_agent=ua)
        await stealth_async(page)
        link = "https://www.pararius.com/apartments/nederland/since-1"
        await page.goto(link)
        numPages = await getNumPages(page)
        dailyLinks.append(await getLinks(page))

        for i in range(2, numPages+1):
            await page.goto(
                f"https://www.pararius.com/apartments/nederland/since-1/page-{i}",
                referer="https://google.com/")
            dailyLinks.append(await getLinks(page))
    allLinks = combineLinkSets(dailyLinks)
    writeToFile(allLinks)

if __name__ == "__main__":
    asyncio.run(main())
