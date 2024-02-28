import asyncio
from playwright.async_api import async_playwright
from tqdm import tqdm
import sys
sys.path.append('./rentola_scraper_scripts')
from retry_decorator import apply_retry_logic
from datetime import datetime
from datetime import date
import random
import json
import os

#create the path if not exists where we going to store the data
directory_path = "./listings/"+ str(date.today())
os.makedirs(directory_path, exist_ok=True)

# produces a random user agent and a random sleep duration
def randomize():
    user_agents = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
    )
    random_user = random.choice(user_agents)
    sleep_duration = random.uniform(1,3)
    return random_user, sleep_duration
 
 #go to page with with rety logic 
@apply_retry_logic
async def go_to_page(page,url):
    await page.goto(url, timeout=0)
    await asyncio.sleep(randomize()[1])
    await decline_cookies(page)
      

#decline cookies
async def decline_cookies(page):
    try:
        await page.click('text=Decline all')
    except Exception:
        pass

# #get page object
# async def get_page(page,url,attempts = 3,delay= 6):
#     for attempt in range(attempts):
#      try: 
#          await page.goto(url, wait_until='load')
#          await decline_cookies(page)
#          await asyncio.sleep(3)
#          break
#      except Exception as e:
#          print(f"Attempt:{attempt}.Error navigating to {url}.Retry again in {delay} seconds.")
#          await asyncio.sleep(delay)
#     else:
#          print(f"The maximum attempts have been reached.Skip url:{url}")
#          return 0 #page condition if page object is not loaded
#     return 1 #page condition if page object is loaded
    
#count how many photos exists for the listing 
async def photo_exists(page):
    exists = await page.query_selector('div.fotorama__stage__frame.fotorama__loaded.fotorama__loaded--img.fotorama__active') is not None
    return exists

#click next button in the photo carousel   
async def click_next(browser,page):
    if await page.query_selector('div.fotorama__arr.fotorama__arr--next') is not None:
        await page.click('div.fotorama__arr.fotorama__arr--next')
        await asyncio.sleep(1)

#check if the next button exists    
async def next_button_exists(page):
    disabled = await page.query_selector('div.fotorama__arr.fotorama__arr--next.fotorama__arr--disabled')
    return disabled is None
       
#get the photo on foreground because it gives the url with the normal size   
async def get_active_photo(page):
    try:
        active_photo_src_tag = await page.wait_for_selector('div.fotorama__stage__frame.fotorama__loaded.fotorama__loaded--img.fotorama__active img', timeout=100000)
        src = await active_photo_src_tag.get_attribute('src')
        return src
    except (AttributeError, TimeoutError):
        return 
    
#since photos exists  and next button exists rotate carousel and get the active photo, if photo exists but not next button get the photo, else return empty list      
async def get_photos(browser,page,url):
    url = url
    try:
        photos_exists = await photo_exists(page)
        photo_sources = [] 
        while photos_exists and await next_button_exists(page)== True:
            photo_sources.append(await get_active_photo(page))
            await click_next(browser, page) 
        if photos_exists == False:
            return []     
        else:  
            photo_sources.append(await get_active_photo(page))    
            return photo_sources
    except Exception as e:
        print(f'{e} at {url}')
        return []
        


 #get the data that describe the listing   
async def get_data(browser,page,url):
    data = {}
    data['url'] = url
    try:
        property_type_element = await page.query_selector('//span[text()="Property type:" and @class="about-label"]//following-sibling::span')
        data['property_type'] = await property_type_element.inner_text()
    except AttributeError:
        data['property_type'] = None   

    try:
        city_element = await page.query_selector('//span[text()="City:" and @class="about-label"]//following-sibling::span')
        data['city'] = await city_element.inner_text()
    except AttributeError:
        data['city'] = None
    
    try:
        area_element = await page.query_selector('//span[text()="Area:" and @class="about-label"]//following-sibling::span')
        data['area'] = await area_element.inner_text()
    except AttributeError:
        data['area'] = None

    try:
        bedrooms_element = await page.query_selector('//span[text()="Bedrooms:" and @class="about-label"]//following-sibling::span')
        data['bedrooms'] = await bedrooms_element.inner_text()
    except AttributeError:
        data['bedrooms'] = None

    try:
        bathrooms_element = await page.query_selector('//span[text()="Bathrooms:" and @class="about-label"]//following-sibling::span')
        data['bathrooms'] = await bathrooms_element.inner_text()
    except AttributeError:
        data['bathrooms'] = None

    try:
        garage_element = await page.query_selector('//span[text()="Garage:" and @class="about-label"]//following-sibling::span')
        data['garage'] = await garage_element.inner_text()
    except AttributeError:
        data['garage'] = None        
    
    try:
        furnished_element = await page.query_selector('//span[text()="Furnished:" and @class="about-label"]//following-sibling::span')
        data['furnished'] = await furnished_element.inner_text()
    except AttributeError:
        data['furnished'] = None

    try:
        balcony_element = await page.query_selector('//span[text()="Balcony:" and @class="about-label"]//following-sibling::span')
        data['balcony'] = await balcony_element.inner_text()
    except AttributeError:
        data['balcony'] = None

    try:
        elevator_element = await page.query_selector('//span[text()="Balcony:" and @class="about-label"]//following-sibling::span')
        data['elevator'] = await elevator_element.inner_text()
    except AttributeError:
        data['elevator'] = None    

    try:
        swimming_pool_element = await page.query_selector('//span[text()="Swimming pool:" and @class="about-label"]//following-sibling::span')
        data['swimming_pool'] = await swimming_pool_element.inner_text()
    except AttributeError:
        data['swimming_pool'] = None    

    try:
        price_element = await page.query_selector('//span[text()="Price:" and @class="about-label"]//following-sibling::span')
        data['price'] = await price_element.inner_text()
    except AttributeError:
        data['price'] = None

    try:
        deposit_element = await page.query_selector('//span[text()="Deposit:" and @class="about-label"]//following-sibling::span')
        data['deposit'] = await deposit_element.inner_text()
    except AttributeError:
        data['deposit'] = None        
    
    try:
        price_per_sm_element = await page.query_selector('//span[text()="Price per m²:" and @class="about-label"]//following-sibling::span')
        data['price_per_sm'] = await price_per_sm_element.inner_text()
    except AttributeError:
        data['price_per_sm'] = None
    
    try:
        address_element = await page.query_selector('//p[@class="location"]')
        data['address'] = await address_element.inner_text()
    except AttributeError:
        data['address'] = None 

    try:
        available_from_element = await page.query_selector('//span[text()="Available from:" and @class="about-label"]//following-sibling::span')
        data['available_from'] = await available_from_element.inner_text()
    except AttributeError:
        data['available_from'] = "now"    

    try:
        case_number_element = await page.query_selector('//div[text()="Case number:" and @class="f-column"]//following-sibling::div')
        data['case_number'] = await case_number_element.inner_text()
    except AttributeError:
        data['case_number'] = None      

    data['photo_urls'] = await get_photos(browser,page,url)

    data['created_at']= datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    with open("./listings/"+ str(date.today()) + "/" +str(data['case_number']) + '.json', 'w') as json_file:
        json.dump(data,json_file, indent=2)


    

         

 #orchestrate the functions       
async def main(url):
    url = url
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=randomize()[0])
        page = await context.new_page()
        page_condition = await go_to_page(page, url)

        if page_condition == 1:#if page object has content scrape the data
         await get_data(browser, page, url)

#the script could stop here
#next is for scraping urls concurrently
def listing_to_list():#load the listings urls in list 
    with open('listing_urls.json', "r") as json_file:
       listings =  json.load(json_file)
       return listings

#create sublists in the list so we can easily create workers with asyncio and scrape all the urls in the sublist at once
#by changing the chunk_size variable in the next function we changing the lenght of sublist so that depending on our system we can scrape more or less urls concurrently
def chunk_list(ls,chunk_size):
    chunked = [ ls[i:i + chunk_size] for i in range(0,len(ls),chunk_size)]
    return chunked

async def concurrent_scrape():
    workers = []
    chunked_listings = chunk_list(listing_to_list(),3)#<-- here we can change the number of urls we scrape concurrently, default 1
    for chunk in tqdm(chunked_listings):
            for url in chunk:
                workers.append(asyncio.create_task(main(url)))#here we create the workers which will run the main function at the same as many times as we have defined above
            await asyncio.gather(*workers)
asyncio.run(concurrent_scrape())
