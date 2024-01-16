import json

import re
import math
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
import asyncio
from undetected_playwright import stealth_async
from datetime import date


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
        getNumResults = page.locator("header .total-hits")
        numResults = await getNumResults.inner_text()

        return math.ceil(int(numResults)/25)

    except Exception as err:
        print(f"getNumPages error {page.url} {err}")


async def getLinks(page) -> set:
    gemeentenLinks = set()
    try:
        # await page.route("**/*",excludeResources) - Seems to slow down load, but can't figure out why

        # Selects all links within the search-resuls class where the link element contains an element with the class search-result_header-title
        links = await page.query_selector_all(
            ".list-room-title h2 a")
        for link in links:
            source = await link.get_attribute("href")
            if not source:
                source = await link.get_attribute("data-href")

            # print(f"link {source}")
            gemeentenLinks.add("https://www.kamer.nl"+source)

        return gemeentenLinks
    except Exception as err:
        print(f"getLinks error {page.url} {err}")


def combineLinkSets(linksSets) -> list:
    linksList = []
    for links in linksSets:
        for link in links:
            linksList.append(link)

    return linksList


scrapeDate = str(date.today())


def writeToFile(links):
    try:
        with open(f"/app/listings/{scrape_date}Listings.txt", "w") as outfile:
            for link in links:
                outfile.write(link+"\n")
        print("File write successful!")
    except Exception as err:
        print(f"writeToFile error {err}")


async def main():
    dailyLinks = []

    async with async_playwright() as player:
        browser_args = [
            '--window-size=1300,570',
            '--window-position=000,000',
            '--disable-dev-shm-usage',
            '--no-sandbox',
            '--disable-web-security',
            '--disable-features=site-per-process',
            '--disable-setuid-sandbox',
            '--disable-accelerated-2d-canvas',
            '--no-first-run',
            '--no-zygote',
            '--use-gl=egl',
            '--disable-blink-features=AutomationControlled',
            '--disable-background-networking',
            '--enable-features=NetworkService,NetworkServiceInProcess',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-breakpad',
            '--disable-client-side-phishing-detection',
            '--disable-component-extensions-with-background-pages',
            '--disable-default-apps',
            '--disable-extensions',
            '--disable-features=Translate',
            '--disable-hang-monitor',
            '--disable-ipc-flooding-protection',
            '--disable-popup-blocking',
            '--disable-prompt-on-repost',
            '--disable-renderer-backgrounding',
            '--disable-sync',
            '--force-color-profile=srgb',
            '--metrics-recording-only',
            '--enable-automation',
            '--password-store=basic',
            '--use-mock-keychain',
            '--hide-scrollbars',
            '--mute-audio'
      
        browser = await player.chromium.launch(headless=True, args=browser_args)
        # User agent must be set for stealth mode so the captcha isn't triggered in headless mode.
        ua = ("Mozilla/5.0 (X11; Linux x86_64)"
              "AppleWebKit/537.36 (KHTML, like Gecko)"
              "Chrome/111.0.0.0 Safari/537.36")
        page = await browser.new_page(user_agent=ua)
        await stealth_async(page)
        link = "https://www.kamer.nl/huren/?created=0"
        await page.goto(link)
        numPages = await getNumPages(page)
        if numPages:
            dailyLinks.append(await getLinks(page))

            for i in range(2, numPages+1):
                await page.goto(
                    f"https://www.kamer.nl/huren/?created=0$page={i}",
                    referer="https://google.com/")
                dailyLinks.append(await getLinks(page))
    allLinks = combineLinkSets(dailyLinks)

    print(f"{len(allLinks)} links found for {scrapeDate}")

    if len(allLinks) == 0:
        writeToFile([f"No new links found for {scrapeDate}",])
    else:
        writeToFile(allLinks)

if __name__ == "__main__":
    asyncio.run(main())
