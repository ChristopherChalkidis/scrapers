#!/bin/bash

python3 /app/scrapper_scripts/funda_get_daily.py
python3 /app/scrapper_scripts/funda_parse_listing.py
python3 /app/db_scripts/db.py
python3 /app/db_scripts/json_to_db.py