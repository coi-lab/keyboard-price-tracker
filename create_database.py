import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).with_name("switch_prices.db")


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS Keyboard_Items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    brand TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Vendor_Listings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,
    vendor_name TEXT NOT NULL,
    retail_price REAL NOT NULL CHECK (retail_price >= 0),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price REAL NOT NULL CHECK (unit_price >= 0),
    source_url TEXT,
    date_updated TEXT NOT NULL,

    -- Each vendor listing row belongs to one keyboard item.
    -- Deleting a keyboard item also removes its related vendor listings.
    FOREIGN KEY (item_id)
        REFERENCES Keyboard_Items (id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_vendor_listings_item_id
    ON Vendor_Listings (item_id);

CREATE INDEX IF NOT EXISTS idx_vendor_listings_date_updated
    ON Vendor_Listings (date_updated);
"""


def create_database(db_path: Path = DB_PATH) -> None:
    with sqlite3.connect(db_path) as connection:
        connection.executescript(SCHEMA)


if __name__ == "__main__":
    create_database()
    print(f"Database created at: {DB_PATH}")
