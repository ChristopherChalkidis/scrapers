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
        #with open(f"/app/listings/{scrapeDate}Listings.txt", "w") as outfile:
        with open(f"{scrapeDate}Listings.txt", "w") as outfile: # Needed for testing
            for link in links:
                outfile.write(link+"\n")
        print("File write successful!")
    except Exception as err:
        print(f"writeToFile error {err}")

async def getNumPages(page) -> int:
    try:
        numResultsLocator=".h2-search-button"
        resultsPerPage=18

        getNumResults = page.locator(numResultsLocator)
        txt = await getNumResults.inner_text()
        pat = "\\d+"
        numResults = re.findall(pat, txt)
        numResults = int(numResults[0])
        return math.ceil(numResults/resultsPerPage)

    except Exception as err:
        print(f"getNumPages error {page.url} {err}")


async def postedRecently(listing):
    '''
        Returns True if the listing was posted < 24h ago.
    '''
    listing = await listing.query_selector('[class="right tile-dateplaced"]')
    stamp = await listing.inner_text()
    if stamp == "New!":
        return True
    if stamp[-1] == "h":
        return True
    return False

async def getURL(listing):
    listing = await listing.query_selector('[class="tile-title truncate"]')
    link = await listing.get_attribute('href')
    return link


async def getLinks(page) -> tuple:
    gemeentenLinks = set()
    count = 0
    try:
        listings = await page.query_selector_all('[id^="roomAdvert"]')
        for listing in listings:
            wasPostedRecently = await postedRecently(listing)
            count += 1
            if wasPostedRecently:
                link = await getURL(listing)
                gemeentenLinks.add(link)
                count = 0
        return gemeentenLinks, count
    except Exception as err:
        print(f"getLinks error {page.url()} {err}")


async def main():
    dailyLinks = []

    async with async_playwright() as player:
        browser = await player.chromium.launch(headless=False)
        ua = ("Mozilla/5.0 (X11; Linux x86_64)"
            "AppleWebKit/537.36 (KHTML, like Gecko)"
            "Chrome/113.0.0.0 Safari/537.36")
        
        page = await browser.new_page(user_agent=ua)
        await stealth_async(page)
        # numPages = await getNumPages(page)
        # print(numPages)
        # numPages will range 110 - 120 pages.
        # Kamernet adds ~250 new listings everyday. Source: https://kamernet.nl/en/how-does-it-work/a 
        # Instead we grab the first 20 pages * 18 listings = 360 newest listings 
        numPages = 20 
        
        # Once our scraper grabs this number of old listings, it should stop:
        threshold = 3

        for i in range(1, numPages+1):
            link = "https://kamernet.nl/en/for-rent/rooms-netherlands"
            if i > 1:
                link = link + f"?pageno={i}"

            await page.goto(link)
            listingsURLs, count = await getLinks(page)
            dailyLinks.append(listingsURLs)

            # If number of old listing on the page is above a threshold, stop the loop:
            if count > threshold:
                print(f"On page {i} there were {count} listings older than one day.")
                break

    allLinks = combineLinkSets(dailyLinks)
    writeToFile(allLinks)

if __name__ == "__main__":
    asyncio.run(main())
