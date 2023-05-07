# Scrape Pararius Website

## A. Getting started

This section helps you get started.
Clone the repo

```
git clone https://github.com/techadvisory/scrapper.git
```

## B. How to Run

- I believe these are the steps for a new computer

1. docker build -t scrapers:v1.0 .
2. docker create --name run-scrapers scrapers:v1.0
3. docker compose up

- Once the compose up is run it should immediately start running funda_get_daily.py this is it's current starting point
