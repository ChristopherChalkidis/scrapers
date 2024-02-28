import asyncio
def apply_retry_logic(func):
  async def wrapper(page, url, max_attempts=3, delay=6):
    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
      try:
        await func(page,url)
        await asyncio.sleep(3)
        break
      except Exception as e:
        print(f"Attempt {attempt}. Error: {e}. Retry in {delay} seconds.")
        await asyncio.sleep(delay)
    else:
      print(f"The maximum attempts have been reached.Skip url: {url}")   
      return 0 #page condition if page object is not loaded
    return 1 #page condition if page object is loaded
  return wrapper