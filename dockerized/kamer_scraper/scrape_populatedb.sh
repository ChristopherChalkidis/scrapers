#!/bin/bash

python3 scraper_scripts/kamer_get_daily.py
echo "get_daily script has run!"

echo "parse_listing script has run!"
python3 db_scripts/db.py
echo "db was created"
python3 db_scripts/json_to_db.py
echo "db was populated"