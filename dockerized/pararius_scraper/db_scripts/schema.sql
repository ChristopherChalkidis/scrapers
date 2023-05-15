CREATE TABLE IF NOT EXISTS property (
	property_id INTEGER PRIMARY KEY NOT NULL,
	address TEXT NOT NULL,
    listed_since TEXT,
    photos TEXT,
    kind_of_house TEXT,
    type_apartment TEXT,
    living_area TEXT,
    number_of_rooms TEXT,
    number_of_bath_rooms TEXT,
    number_of_stories TEXT,
    url TEXT NOT NULL,
    title TEXT,
    postal_code TEXT,
    year_of_construction TEXT,
    site TEXT NOT NULL,
    scrapped_at TEXT NOT NULL,
    city TEXT NOT NULL,
    country TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS property_for_rent (
    rent_id INTEGER PRIMARY KEY NOT NULL,
    property_id INTEGER NOT NULL,
    rental_price INTEGER NOT NULL,
    deposit INTEGER,
    rental_aggrement TEXT,
    FOREIGN KEY (property_id) REFERENCES property (property_id)
);

CREATE TABLE IF NOT EXISTS property_for_sale (
    sale_id INTEGER PRIMARY KEY NOT NULL,
    property_id INTEGER NOT NULL,
    asking_price INTEGER NOT NULL,
    FOREIGN KEY (property_id) REFERENCES property (property_id)
);

CREATE TABLE IF NOT EXISTS user_preferences (
    user_id INTEGER PRIMARY KEY NOT NULL,
    sub_start TEXT NOT NULL,
    sub_ends INTEGER NOT NULL,
    email TEXT NOT NULL,
    number_of_rooms INTEGER,
    city TEXT NOT NULL,
    country TEXT NOT NULL
);