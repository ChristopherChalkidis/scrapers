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

async def getFeatures(page):
    """Gets the name and specifics of each detail listed on the page

    :param {page object} page - The browser page displaying a listing
    :return A list of small dictionaries of strings of all the details {title: name}
    """
    all_features = []

    furnishing = await getDetail('[class="furnishing"]', page)
    furnishing = furnishing.split(':')
    all_features.append({cleanString(furnishing[0]): cleanString(furnishing[1])})

    availability = await getDetail('[class="availability"]', page)
    availability = availability.split(':')
    all_features.append({cleanString(availability[0]): availability[1].strip()})

    details_section = page.locator('[class$="room-details-info"]')
    details_info = await details_section.inner_text()
    details_info = details_info.split('\n')
    i=1
    while i < len(details_info):
        title = cleanString(details_info[i])
        detail = cleanString(details_info[i+1])
        all_features.append({title: detail})
        i+=2

    return all_features

async def getPhotos(page):
    """Gets all the photos on the page if they are photos of the listing

    :param {page object} page - The browser page displaying a listing

    :return A list containing the src to all the photos of the current listing"""
    photos = set()
    images = await page.query_selector_all('[class="item gallery-item"]')
    for image in images:
        imageSRC = await image.get_attribute('href')
        photos.add(imageSRC)

    return list(photos)

async def getTypeAddress(page):
    try:
        type_address = await getDetail('[id="streetCityName"]', page)
        rentalType, street, city = type_address.split('\n')
        rentalType = rentalType[:-9] # It comes as "Type for rent", we drop " for rent" at the end
        address = street + ',' + city[2:] #city comes as "in city", we drom "in " at the start
        return cleanString(rentalType), address.strip()
    except Exception as err:
        print(f"Error fetching rental type and address {page.url} - {err}")

async def getInfo(page):
    """Gets all the informatin for the listing that the page is at

    :param {page object} page - The browser page displaying a listing

    :return A dictionary containing the information: title, address, url, features, and photos
    """
    try:
        await page.wait_for_selector('[class="row room-details"]', timeout=5000)

        rentalType, address = await getTypeAddress(page)
        area = await getDetail('[class="surface"]', page)
        roomsNumber = '1'
        if rentalType != "room":
            roomsNumber = await getDetail('[class="rooms-numbers"]', page)
        rentPrice = await getDetail('[class="price"]', page)
        deposit = await getDetail('[class~="costs-overview"] table tr:last-child td:last-child', page)

        return {
            "type_of_rental": rentalType, 
            "address": address,
            "url": page.url,
            "area": area.strip(),
            "number_of_rooms": roomsNumber.strip(),
            "rental_price": rentPrice.strip(),
            "deposit": deposit.strip(),
            "features": await getFeatures(page),
            "photos": await getPhotos(page)
            }
    except Exception as err:
        print(f"Couldn't find title {page.url} - {err}")

scrapeDate = str(date.today())
async def writeJson(fileName, listingInfo):
    """Writes the listing info to a file with the passed in fileName

    :param {string} fileName - The string containing the name the file will receive
    :param {dict} listingInfo - A dictionary containing all the information for each listing
    """
    with open(f"/app/listings/{fileName}", "a") as outfile:
        outfile.write(json.dumps(listingInfo, indent=4))

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
        #for link in dailyURLs[:10]: #test
            await run(link, page)

        await ctx.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())