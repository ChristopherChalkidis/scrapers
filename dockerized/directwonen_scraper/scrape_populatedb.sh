#!/bin/bash

python3 scrapper_scripts/directwonen_get_listings.py
echo "get_listings script has run!"
python3 db_scripts/db.py
echo "db was created"
python3 db_scripts/json_to_db.py
echo "db was populated"