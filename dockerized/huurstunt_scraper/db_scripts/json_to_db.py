import sqlite3
import json
import os
from urllib.parse import urlparse

#is the title same with address?
#scrapped_at form?
#listed since today?
#country

# # For portability, we obtain the absolute path to the script
# dirname = os.path.dirname(os.path.abspath(__file__))

# Set the path to the directory containing the JSON files
json_path = "/app/listings"

# Set the path to the SQLite database
db_path = "/app/database/properties.db"

# Create a connection to the database
conn = sqlite3.connect(db_path)

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

def get_feature_value(features, key):
    for feature in features:
        if key in feature:
            return feature[key]
    return "Unknown"

def is_rental_listing(url):
    print(f"Checking URL: {url}")
    site = urlparse(url)
    if site.netloc == 'www.funda.nl':
        path = site.path.split('/')
        #print(f"Path: {path}")
        #print(100* "#")
        if path[2] == 'huur':
            return True
    return False

def main():
    # Iterate over the JSON files in the listings directory
    for file in os.listdir(json_path):
        if file.endswith(".json"):
            with open(os.path.join(json_path, file), 'r') as f:
                data = json.load(f)
                #print(data)
                # Extract the relevant information from the JSON data
                address = data["address"]
                postal_code = data["postal_code"]
                url = data["url"]

                #features
                listed_since = get_feature_value(data["features"], "listed_since")
                year_of_construction = get_feature_value(data["features"], "year_of_construction")
                living_area = get_feature_value(data["features"], "living_area")
                number_of_rooms = get_feature_value(data["features"], "number_of_rooms")
                number_of_bath_rooms = get_feature_value(data["features"], "number_of_bath_rooms")
                number_of_stories = get_feature_value(data["features"], "number_of_stories")
                photos = ", ".join(data["photos"])
                rental_price = get_feature_value(data["features"], "rental_price")
                deposit = get_feature_value(data["features"], "deposit")
                rental_aggrement = get_feature_value(data["features"], "rental_agreement")
                asking_price = get_feature_value(data["features"], "asking_price")
                kind_of_house = get_feature_value(data["features"], "kind_of_house")
                type_apartment = get_feature_value(data["features"], "type_apartment")
                scrapped_at = file[:19]
                site = urlparse(url)
                site = site.netloc.split(".")[1]
                city = url.split("/")[5].replace("-", " ")
                country = "nl"

                #Insert data into property table
                cursor.execute('INSERT INTO property (address, listed_since, photos, kind_of_house, type_apartment, living_area, number_of_rooms, number_of_bath_rooms, number_of_stories, url, title, postal_code, year_of_construction, site, scrapped_at, city, country) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                                (address, listed_since, photos, kind_of_house, type_apartment, living_area, number_of_rooms, number_of_bath_rooms, number_of_stories, url, address, postal_code, year_of_construction, site, scrapped_at, city, country))
                
                # Get the property ID of the property just inserted
                cursor.execute('SELECT property_id FROM property WHERE url = ?', (url,))
                property_id = cursor.fetchone()[0]

                #Insert data into property_for_rent table
                if is_rental_listing(url):
                    cursor.execute('INSERT INTO property_for_rent (property_id, rental_price, deposit, rental_aggrement) VALUES(?,?,?,?)',
                                (property_id, rental_price, deposit, rental_aggrement))
  
                #Insert data into property_for_sale table
                else:
                    cursor.execute('INSERT INTO property_for_sale (property_id, asking_price) VALUES(?,?)',
                                (property_id, asking_price))

                
                conn.commit()
if __name__ == "__main__":
    main()