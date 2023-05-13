import json
import re
import math
from playwright.async_api import async_playwright
import asyncio
from undetected_playwright import stealth_async
from datetime import date
# import os


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
        getNumResults = page.locator(".search-output-result-count span")
        txt = await getNumResults.inner_text()
        pat = "\\d+"
        numResults = re.findall(pat, txt)
        numResults = int(numResults[0])
        # print(f"Number is {numResults}")

        if numResults == 0:
            return 0
        else:
            return math.ceil(numResults % 15)
    except Exception as err:
        print(f"getNumPages error {page.url} {err}")


async def getLinks(link, page) -> set:
    gemeentenLinks = set()
    # print(f"Checking {link}")
    try:
        # await page.route("**/*",excludeResources)
        await page.goto(link)

        numPages = await getNumPages(page)
        # print(type(numPages))
        # print(numPages)
        if numPages != 0:
            # Selects all links within the search-resuls class where the link element contains an element with the class search-result_header-title
            links = await page.query_selector_all(
                ".search-results a:has(.search-result__header-title)")

            for i in range(len(links)):
                el = links[i]
                source = await el.get_attribute("href")
                if "navigateSource=resultlist" in source:
                    # print(f"Adding {source}")
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
    try:
        # filename = os.path.join(dirname, "funda_gemeenten_links.json")
        links = await readFile("/app/scrapper_scripts/funda_gemeenten_links.json")
    except Exception as err:
        print(f"readFile error: {err}")

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
        counter = 0  # See README.md
        for link in links[:10]:
           # print(link)
            if counter == 500:
                await browser.close()
                browser = await player.chromium.launch(headless=True)
                ctx = await browser.new_context(user_agent=ua)
                await stealth_async(ctx)
                page = await ctx.new_page()
                counter = 0
            dailyLinks.append(await getLinks(link, page))
            counter += 1
    allLinks = combineLinkSets(dailyLinks)
    writeToFile(allLinks)
    # print(allLinks)

if __name__ == "__main__":
    asyncio.run(main())
