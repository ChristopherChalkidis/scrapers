 CREATE TABLE IF NOT EXISTS rentola (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    listing_url TEXT NOT NULL,
    property_type TEXT,
    city TEXT,
    address TEXT,
    bedrooms TEXT,
    bathrooms TEXT,
    garage TEXT,
    furnished TEXT,
    balcony TEXT,
    elevator TEXT,
    swimming_pool TEXT,
    area TEXT,
    price TEXT,
    deposit TEXT,
    price_per_sm TEXT,
    case_number TEXT,
    available_from TEXT,
    photo_urls TEXT, -- String containing URLs separated by some delimiter
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
