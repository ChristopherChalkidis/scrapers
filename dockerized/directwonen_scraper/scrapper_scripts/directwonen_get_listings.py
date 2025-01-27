import re
import json
from playwright.async_api import async_playwright
import asyncio
from undetected_playwright import stealth_async
from datetime import date

def extractNumerical(txt):
    """
    Extracts a number from a text
    parameters:
        - txt (str) string that include a least one number
    returns:  (int) the first number in the string 
    """
    num = re.findall("\\d+", txt)
    return int(num[0])

async def getNumPages(page) -> int:
    try:
        numResultsLocator=".pager a:nth-last-child(2)"

        getNumResults = page.locator(numResultsLocator)
        txt = await getNumResults.inner_text()
        numResults = extractNumerical(txt)
        return numResults

    except Exception as err:
        print(f"getNumPages error {page.url} {err}")

async def getDetail(elSelector, page) -> str:
    """Gets the string of the specified selector

    :param {string} elSelector - The selector to find the specified element
    :param {page object} page - The browser page displaying a listing
    :return The text of the element specified
    """
    el = await page.query_selector(elSelector)
    return await el.inner_text()

async def getFeatures(page):
    """Gets the name and specifics of each detail listed on the page

    :param {page object} page - The browser page displaying a listing
    :return A list of small dictionaries of strings of all the details {title: name}
    """
    all_features = []

    number_of_rooms = await getDetail('[class*="advert-roomno"]', page)
    all_features.append({"number_of_rooms": number_of_rooms})

    living_area = await getDetail('[class*="advert-surface"]', page)
    all_features.append({"living_area": living_area})

    # furnishing = await getDetail('[class*="advert-unfurnished"]', page)
    # all_features.append({"furnishing": furnishing})

    available_from = await getDetail('[class*="available-date"]', page)
    all_features.append({"available_from": available_from})

    rental_price = await getDetail('[class*="price-wrapper"]', page)
    rental_price = extractNumerical(rental_price)
    all_features.append({"rental_price": rental_price})

    return all_features

async def isSmartOnly(page):
    """Return whether the listing is Smart Only (i.e. reserved to view by subscribers)
    :parm {page object} page - The browser page displaying a listing
    """
    label=  await page.query_selector('[class="label-premium"]')
    if label:
        return True
    return False

async def getPhotos(page, isRestricted= True):
    """Gets all the photos on the page if they are photos of the listing

    :param {page object} page - The browser page displaying a listing

    :return A list containing the src to all the photos of the current listing"""
    photos = set()
    if isRestricted:
        image = await page.query_selector('[class*="search-photo"] img')
        imageSRC = await image.get_attribute('src')
        photos.add(imageSRC)
    else:
        images = await page.query_selector_all('[class*="apartment-slider slider"] div img')
        for image in images:
            imageSRC = await image.get_attribute('src')
            photos.add(imageSRC)

    return list(photos)


async def getAddress(page):
    address_txt = await page.query_selector('[class*="inner-content"]')
    address_txt = await address_txt.get_attribute('title')
    address_txt = address_txt.split(': ')[1].split(' ', 1)
    type = address_txt[0]
    address = address_txt[1]
    return type, address


async def getInfo(page, link):
    """Gets all the informatin for the listing

    :param {page object} page - The browser page displaying a listing
    :return A dictionary containing the information: title, address, url, features, and photos
    """
    try:
        type_apartment, address = await getAddress(page)

        return { 
            "address": address,
            "url": link,
            "type_apartment": type_apartment,
            "features": await getFeatures(page),
            "photos": await getPhotos(page)
            }
    except Exception as err:
        print(f"Couldn't find title {link} - {err}")

async def writeJson(fileName, listingInfo):
    """Writes the listing info to a file with the passed in fileName
    :param {string} fileName - The string containing the name the file will receive
    :param {dict} listingInfo - A dictionary containing all the information for each listing
    """
    with open(f"/app/listings/{fileName}", "a") as outfile:
    # with open(f"{fileName}", "a") as outfile: #needed for testing
        outfile.write(json.dumps(listingInfo, indent=4))

scrapeDate = str(date.today())
async def writeToFile(listingInfo):
    """Writes listing info to a json file

    :param {dict} listingInfo - A dictionary containing all the information for each listing
    """
    fileName = f"rental--{scrapeDate}--{listingInfo['address']}.json"
    await writeJson(fileName.replace("/", "-"), listingInfo)

async def parseUnrestrictedListings(page, non_restricted_links, non_restricted_info):
    """
    Gets more photos from listings when access is available.
    parameters:
        - page (page object): The browser page displaying search results
        - non_restricted_links (list): list of links to unrestricted listings
        - non_restricted_info (list): info scraped from first page of results corresponding to each listing
    returns: 
        None. Function writes results to file. 
    """
    for i, url in enumerate(non_restricted_links):
        info = non_restricted_info[i]
        await page.goto(url, wait_until="domcontentloaded")
        try:
            photos = await getPhotos(page, False)
            info["photos"] = photos
            await writeToFile(info)
        except Exception as err:
            print(f"Error in getting info of non restricted {url}: {err}")

async def getListings(page, prope_unrestricted= True):
    """
    Scrape info about listings and writes it to files.
    parameters:
        - page (page object): The browser page displaying search results
        - prope_unrestricted (boolean): Get more info from listings when access is available.
    returns: 
        None. Function writes results to file. 
    """
    listings = await page.query_selector_all('[class*="rowSearchResultRoom"]')
    non_restricted_links = []
    non_restricted_info = []

    for listing in listings:
        link = await listing.get_attribute('href')
        resctriced = await isSmartOnly(listing)

        info = await getInfo(listing, link)
        if not resctriced & prope_unrestricted:
            non_restricted_links.append(link)
            non_restricted_info.append(info)
            continue
        if info:
            await writeToFile(info)

    if prope_unrestricted:
        await parseUnrestrictedListings(page, non_restricted_links, non_restricted_info)


async def main():
    async with async_playwright() as player:
        browser = await player.chromium.launch(headless=False)
        ua = ("Mozilla/5.0 (X11; Linux x86_64)"
            "AppleWebKit/537.36 (KHTML, like Gecko)"
            "Chrome/113.0.0.0 Safari/537.36")
        
        page = await browser.new_page(user_agent=ua)
        await stealth_async(page)
        link = "https://directwonen.nl/en/rentals-for-rent/nederland"
        await page.goto(link, wait_until="domcontentloaded")
        await page.locator('[onclick="setTilesView(false);"]').click()
        await page.locator("[name='AdvertRecencyId']").select_option("1")
        await page.locator("[id='btnSearchInId']").click()
        await page.wait_for_url('https://directwonen.nl/en/rentals-for-rent/nederland?Recency=today')
        numPages = await getNumPages(page)

        await getListings(page, prope_unrestricted=True)

        for i in range(2, numPages+1):
            link = f"https://directwonen.nl/en/rentals-for-rent/nederland?pageno={i}"

            await page.goto(link)
            await getListings(page, prope_unrestricted=True)

if __name__ == "__main__":
    asyncio.run(main())
