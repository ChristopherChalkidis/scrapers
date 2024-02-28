#!/bin/bash
python3 rentola_scraper_scripts/rentola_get_daily.py
if [ $? -eq 0 ]; then
    echo "Script 1 out of 4 has run!"
else
    echo "Error: Script 1 failed to run."
    exit 1
fi

python3 rentola_scraper_scripts/rentola_parse_listing.py
if [ $? -eq 0 ]; then
    echo "Script 2 out of 4 has run!"
else
    echo "Error: Script 2 failed to run."
    exit 1
fi

python3 database_scripts/db_init.py
if [ $? -eq 0 ]; then
    echo "Script 3 out of 4 has run!"
else
    echo "Error: Script 3 failed to run."
    exit 1
fi

python3 database_scripts/populate_db.py
if [ $? -eq 0 ]; then
    echo "Script 4 out of 4 has run!"
else
    echo "Error: Script 4 failed to run."
    exit 1
fi
