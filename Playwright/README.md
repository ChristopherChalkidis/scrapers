# Scrape funda portal

## A. Getting started

This section helps you get started.
Clone the repo

```text
git clone https://github.com/techadvisory/scrapper.git
```

## B. Running instruction

This uses a virtual environment to ensure that all dependencies are met. To use install pipenv in the folder where your project is `pip install pipenv`.
Once installed open your terminal and type the command `pipenv run {filename}` This should work.

## File information

- `getGemeentenNames.py` -  *Does not need to be run everyday, gemeenten should not change often. Uses places list from Funda "https://www.funda.nl/koop/bladeren/heel-nederland/?actpnl=Plaatsnaam". It writes a validated sales and rental link for each location to `gemeenten_links.json`.

- `getDaily` - *Run everyday before parseListingPlaywright Reads gemeenten_links.json and saves all new listing urls from the past 24 hours for each gemeenten in the file (scrapeDate)Listings.txt
- *Counter implemented due to a noticable slow down around 600ish links visited. Not a new browser opens at the 500 links visited mark. This should necessitate roughly 4 browsers opened total.

- `parseListingPlaywright.py` -
Reads (scrapeDateListings.txt) and scrapes each url contained in the file. Each url is saved to a separate json file in the folder listings. The files are named either Sale or Rental --(scrapeDate)--(listing address)
