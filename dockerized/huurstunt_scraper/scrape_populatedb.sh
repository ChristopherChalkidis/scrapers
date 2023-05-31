#!/bin/bash

xvfb-run --auto-servernum --server-num=1 python3 scraper_scripts/huurstunt_parse_listing.py
echo "daily scraping script has run!"
python3 db_scripts/db.py
echo "db was created"
python3 db_scripts/json_to_db.py
echo "db was populated"