#!/bin/bash

xvfb-run --auto-servernum --server-num=1 python3 scraper_scripts/pararius_get_daily.py
echo "get_daily script has run!"
xvfb-run --auto-servernum --server-num=1 python3 scraper_scripts/pararius_parse_listing.py
echo "parse_listing script has run!"
python3 db_scripts/db.py
echo "db was created"
python3 db_scripts/json_to_db.py
echo "db was populated"