from playwright.async_api import async_playwright
import sys
sys.path.append('./rentala_scraper_scripts')
from retry_decorator import apply_retry_logic
import asyncio
import random
import json

#Function returns the randomly selected user agent and sleep duration
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

@apply_retry_logic
async def go_to_page(page,url):
  await page.goto(url, timeout=0)


#return page urls
async def get_pagintation_urls(page):
   urls = ["https://rentola.nl/en/ads-map"]
   href_tags = await page.query_selector_all('//div[@class="pagination"]//a')
   if len(href_tags) > 0:
    hrefs = [await tag.get_attribute("href") for tag in href_tags]
    for href in hrefs:
      urls.append("https://rentola.nl/en/" + href)
    return urls
   else:
    return urls

#return listing urls
async def get_listing_urls(page):
  listing_urls = []
  page_urls = await get_pagintation_urls(page)
  for url in page_urls:
    await asyncio.sleep(1)
    await go_to_page(page,url)
    await asyncio.sleep(1)
    href_tags = await page.query_selector_all('//li//a')  
    urls = ['https://rentola.nl' + await tag.get_attribute('href') for tag in href_tags]
    listing_urls.extend(urls)
  return listing_urls

#put new listings in a json file
async def listings_to_json(page):
  listing_urls = await get_listing_urls(page)
  print(f"{len(listing_urls)} new listings have been found!")
  with open('listing_urls.json', 'w') as json_file:
      json.dump(listing_urls, json_file)
  

async def main(url):
 # Initialize Async Playwright and launch the browser.
 async with async_playwright() as playwright:
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context(user_agent=randomize()[0])
    page = await context.new_page()
    await go_to_page(page,url)
    await listings_to_json(page)
  

#the url guide us to the new added listings for the day
url = "https://rentola.nl/ads-map"
asyncio.run(main(url))    