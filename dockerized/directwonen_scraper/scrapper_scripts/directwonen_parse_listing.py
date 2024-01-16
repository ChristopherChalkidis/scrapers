import json
from playwright.async_api import async_playwright
import asyncio
from playwright_stealth import stealth_async
from datetime import date

def cleanString(str_):
    return str_.strip().lower().replace(' ', '_')

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

async def getDetail(elSelector, page) -> str:
    """Gets the string of the specified selector

    :param {string} elSelector - The selector to find the specified element
    :param {page object} page - The browser page displaying a listing
    :return The text of the element specified
    """
    el = page.locator(elSelector)
    return await el.inner_text()

async def getAddress(page):
    try:
        address = await getDetail('[class="listing-detail-summary__title"]', page)
        address = address.replace(' in ', ', ')
        address = address.split(' ', 1)[1]

        postalCode = await getDetail('[class="listing-detail-summary__location"]', page)
        postalCode = postalCode.split('(')[0]
        postalCode = postalCode.strip()

        return address, postalCode
    except Exception as err:
        print(f"Error fetching rental address {page.url} - {err}")

renameFeatures =  {'for_rent_price': "rental_price",
                 'offered_since': "listed_since",
                 'status': 'Te huur',
                 'surface_area': "living_area",
                 'construction_period': "year_of_construction",
                 'number_of_floors': "number_of_stories"}
async def getFeatures(page):
    """Gets the name and specifics of each detail listed on the page

    :param {page object} page - The browser page displaying a listing
    :return A list of small dictionaries of strings of all the details {title: name}
    """
    all_features = []

    allFeatureTitles = await page.query_selector_all('[class^="listing-features__description"]')

    allFeatureDetails = await page.query_selector_all('[class^="listing-features__main-description"]')

    for i in range(len(allFeatureTitles)):
        title = await allFeatureTitles[i].get_attribute('class')
        title = cleanString(title.split("--")[1])
        if title in renameFeatures:
            title= renameFeatures[title]
        detail = await allFeatureDetails[i].inner_text()
        all_features.append({title: detail})

    return all_features

async def getPhotos(page):
    """Gets all the photos on the page if they are photos of the listing

    :param {page object} page - The browser page displaying a listing

    :return A list containing the src to all the photos of the current listing"""
    photos = set()
    images = await page.query_selector_all('[class="picture picture--media-carrousel"]')
    for image in images:
        # getting links to photos in the carrousel which are NOT displayed
        noScriptLinks = await image.query_selector_all('noscript')
        if len(noScriptLinks) > 0:
            noScriptHTML = await noScriptLinks[0].inner_html()
            imageSRC = noScriptHTML.split("<img")[1].split("src=")[1].split("\"")[1]
            photos.add(imageSRC)
        else:
            # getting links to photos in the carrousel which are displayed
            imgElement = await image.query_selector_all('img')
            imageSRC = await imgElement[0].get_attribute('src')
            photos.add(imageSRC)

    return list(photos)

async def getInfo(page):
    """Gets all the informatin for the listing that the page is at

    :param {page object} page - The browser page displaying a listing

    :return A dictionary containing the information: title, address, url, features, and photos
    """
    try:
        await page.wait_for_selector('[class="page__content"]', timeout=5000)

        address, postalCode = await getAddress(page)

        return { 
            "address": address,
            "postal_code": postalCode,
            "url": page.url,
            "features": await getFeatures(page),
            "photos": await getPhotos(page)
            }
    except Exception as err:
        print(f"Couldn't find title {page.url} - {err}")

async def writeJson(fileName, listingInfo):
    """Writes the listing info to a file with the passed in fileName

    :param {string} fileName - The string containing the name the file will receive
    :param {dict} listingInfo - A dictionary containing all the information for each listing
    """
    with open(f"/app/listings/{fileName}", "a") as outfile:
    #with open(f"{fileName}", "a") as outfile: #needed for testing
        outfile.write(json.dumps(listingInfo, indent=4))

scrapeDate = str(date.today())
async def writeToFile(listingInfo):
    """Writes listing info to a json file

    :param {dict} listingInfo - A dictionary containing all the information for each listing
    """
    fileName = f"rental--{scrapeDate}--{listingInfo['address']}.json"
    await writeJson(fileName.replace("/", "-"), listingInfo)

async def run(link, page):
    try:
        await page.goto(link, wait_until="domcontentloaded")
        info = await getInfo(page)
        if info:
            await writeToFile(info)
    except Exception as err:
        print(f"Error {link} {err}")

async def main():
    """Reads the list of all the rental links for today's listings"""

    links = readFile(f"/app/listings/{scrapeDate}Listings.txt")
    #links = readFile(f"{scrapeDate}Listings.txt")# Needed for testing
    dailyURLs = links.splitlines()

    async with async_playwright() as player:
        ua = ("Mozilla/5.0 (X11; Linux x86_64)"
            "AppleWebKit/537.36 (KHTML, like Gecko)"
            "Chrome/113.0.0.0 Safari/537.36")
        browser = await player.chromium.launch(headless=True, timeout=10000)
        ctx = await browser.new_context(user_agent=ua)
        page = await ctx.new_page()
        await stealth_async(page)

        for link in dailyURLs:
            await run(link, page)

        await ctx.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())