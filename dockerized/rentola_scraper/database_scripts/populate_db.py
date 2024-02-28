import sqlite3
import json
import os
from datetime import datetime
# Establish connection to database
conn = sqlite3.connect('database/properties.db')
cursor = conn.cursor()

# Find today's date
today = datetime.now().date()


# Find the data that scraped today in the folder path
folder_path = "listings/" + str(today)

# Parse the json file and load the data to database
if os.path.exists(folder_path):
  for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)
    if os.path.isfile(file_path):
      with open(file_path, 'r') as json_file:
        data = json.load(json_file)
        photo_urls_str = ','.join(data['photo_urls'])
        cursor.execute('''
            INSERT INTO rentola (listing_url, property_type, city,address, bedrooms, bathrooms, garage , furnished, balcony, elevator, swimming_pool,  area, price, deposit, price_per_sm, case_number, available_from, photo_urls, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (data['url'], data['property_type'], data['city'], data['address'], data['bedrooms'], data['bathrooms'], data['garage'], data['furnished'], data['balcony'], data['elevator'],data['swimming_pool'], data['area'], data['price'], data['deposit'], data['price_per_sm'], data['case_number'], data['available_from'], photo_urls_str, data['created_at']))

        conn.commit()
conn.close()
