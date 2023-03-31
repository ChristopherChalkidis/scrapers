CREATE TABLE IF NOT EXISTS property (
	property_id INTEGER PRIMARY KEY NOT NULL,
	address TEXT NOT NULL,
    listed_since TEXT,
    photos TEXT,
    kind_of_house TEXT,
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