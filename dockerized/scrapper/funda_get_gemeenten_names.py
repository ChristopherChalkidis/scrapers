import json
from playwright.async_api import async_playwright
import asyncio
from playwright_stealth import stealth_async
import unicodedata
import re

def writeToFile(urls):
    """ Takes the set of urls created and writes it to a json file

    :param {set} urls - A set of validated strings containing the gemeenten urls

    :return null
    """
    json_object = json.dumps(list(urls), indent=4)
    try:
        with open("gemeenten_links.json", "w") as outfile:
            outfile.write(json_object)
        print("File write successful!")
    except Exception as err:
        print(f"File unable to write {err}")

async def testLinks(placeURLs, page) -> set:
    """ Gets the set of urls to check and the page object to use. It checks each url in the set and if it is valid it adds it to the validURLs set to be returned.

    :param {set} placeURLs - All the urls to test for validity
    :param {page object} page - The browser page displaying a list of all the possible places to search on Funda
    
    :return {set} A set of all the valid urls found in placeURLs
    """
    validURLs = set()
    try:
        for placeURL in placeURLs:
            #print(f"Testing {placeURL}")
            response = await page.goto(placeURL)
            #print(f"Received {response.url}")
            if "zoeksuggestie" not in response.url:
                validURLs.add(placeURL)
        return validURLs
    except Exception as err:
        print(f"Unable to reach url {err}")

def removeAccents(placeName):
    placeName = unicodedata.normalize('NFKD', placeName)
    placeName = placeName.encode("ascii", "ignore")
    placeName = placeName.decode("utf-8")
    return str(placeName)

async def corrected(placeName) -> str:
    """
    Removes special characters
    Replaces spaces with -
    Removes ()
    """
    placeName = removeAccents(placeName)
    #Matches anything that isn't an upper or lowercase letter, a space, or a -.
    pattern = "[^A-Za-z \-]"
    placeName = re.sub(pattern, "", placeName)
    placeName = placeName.replace(" ", "-")
    
    return placeName.lower()

async def getLinks(page) -> set:
    """Visits the page of all areas on funda and finds the names of all the places listed. It loops through this list and adds the rental (huur) and sale (koop) urls to each place.
    
    :param {page object} page - The browser page displaying a list of all the possible places to search on Funda
    
    :return {set} A set containing urls to the rental (huur) and sale (koop) listings for each place
    """
    fundaPlacesURL = "https://www.funda.nl/koop/bladeren/heel-nederland/?actpnl=Plaatsnaam"
    baseURL = "https://funda.nl/"
    gemeentenLinks = set()

    await page.goto(fundaPlacesURL)

    places = await page.query_selector_all(
        ".browse-area>a")
    
    #This only needs to be run a couple times a year if that because the gemeenten are unlikely to change
    for i in range(len(places)):
        placeName = await places[i].inner_text()
        placeName = await corrected(placeName)

        gemeentenLinks.add(f"{baseURL}koop/{placeName}/1-dag")
        gemeentenLinks.add(f"{baseURL}huur/{placeName}/1-dag")

    return gemeentenLinks

async def main():
    """Gets all the urls from https://www.funda.nl/koop/bladeren/heel-nederland/?actpnl=Plaatsnaam (The list on funda of all places to browse. Tests each url and then writes it to a json file
    
    :return {file} cfg["Other"]["gemeenten-links-json-location"]
    """
    async with async_playwright() as player:
        browser = await player.chromium.launch(headless=True)
        #User agent must be set for stealth mode so the captcha isn't triggered in headless mode.
        ua = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/69.0.3497.100 Safari/537.36"
        )
        page = await browser.new_page(user_agent=ua) 

        await stealth_async(page)

        allURLs = await getLinks(page)
        testedLinks = await testLinks(allURLs,page)

        await browser.close() 
    writeToFile(testedLinks)

if __name__ == "__main__":
   asyncio.run(main())