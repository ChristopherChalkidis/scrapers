import re
import math
from playwright.async_api import async_playwright
import asyncio
from undetected_playwright import stealth_async
from datetime import date


def combineLinkSets(linksSets):
    linksList = []
    for links in linksSets:
        for link in links:
            linksList.append(link)
    return linksList

scrapeDate = str(date.today())
def writeToFile(links):
    try:
        with open(f"/app/listings/{scrapeDate}Listings.txt", "w") as outfile:
        # with open(f"{scrapeDate}Listings.txt", "w") as outfile: # Needed for testing
            for link in links:
                outfile.write(link+"\n")
        print("File write successful!")
    except Exception as err:
        print(f"writeToFile error {err}")

async def getNumPages(page) -> int:
    try:
        numResultsLocator=".search-list-header__count"
        resultsPerPage=30

        getNumResults = page.locator(numResultsLocator)
        txt = await getNumResults.inner_text()
        pat = "\\d+"
        numResults = re.findall(pat, txt)
        numResults = int(numResults[0])
        return math.ceil(numResults/resultsPerPage)

    except Exception as err:
        print(f"getNumPages error {page.url} {err}")


async def getURL(listing):
    listing = await listing.query_selector('[class*="listing-search-item__link--title"]')
    link = await listing.get_attribute('href')
    return link


async def getLinks(page) -> tuple:
    gemeentenLinks = set()
    
    try:
        listings = await page.query_selector_all('[class*="search-list__item--listing"]')
        for listing in listings:            
            link = await getURL(listing)
            gemeentenLinks.add(link)

        return gemeentenLinks
    except Exception as err:
        print(f"getLinks error {page.url()} {err}")


async def main():
    dailyLinks = []

    async with async_playwright() as player:
        browser = await player.chromium.launch(headless=True)
        ua = ("Mozilla/5.0 (X11; Linux x86_64)"
            "AppleWebKit/537.36 (KHTML, like Gecko)"
            "Chrome/113.0.0.0 Safari/537.36")
        
        page = await browser.new_page(user_agent=ua)
        await stealth_async(page)
        #link = "https://www.huurwoningen.com/aanbod-huurwoningen/?since=1"
        link = "https://directwonen.nl/en/rentals-for-rent/nederland"
        await page.goto(link)
        numPages = await getNumPages(page)

        # for i in range(1, numPages+1):
        #     link = "https://www.huurwoningen.com/aanbod-huurwoningen/?since=1"
        #     if i > 1:
        #         link = link + f"&page={i}"

        #     await page.goto(link)
        #     listingsURLs = await getLinks(page)
        #     dailyLinks.append(listingsURLs)

    allLinks = combineLinkSets(dailyLinks)
    writeToFile(allLinks)

if __name__ == "__main__":
    asyncio.run(main())
