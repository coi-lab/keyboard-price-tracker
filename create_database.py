import sqlite3
from contextlib import closing
from datetime import date
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
    is_available INTEGER NOT NULL DEFAULT 1 CHECK (is_available IN (0, 1)),

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
    with closing(sqlite3.connect(db_path)) as connection:
        apply_schema(connection)
        connection.commit()


def apply_schema(connection: sqlite3.Connection) -> None:
    try:
        connection.executescript(SCHEMA)
    except sqlite3.OperationalError as error:
        if "date_updated" not in str(error) and "is_available" not in str(error):
            raise

        ensure_vendor_listing_columns(connection)
        connection.executescript(SCHEMA)
    else:
        ensure_vendor_listing_columns(connection)


def ensure_vendor_listing_columns(connection: sqlite3.Connection) -> None:
    table = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table' AND name = 'Vendor_Listings'
        """
    ).fetchone()
    if table is None:
        return

    columns = {
        row[1]
        for row in connection.execute("PRAGMA table_info(Vendor_Listings)").fetchall()
    }

    if "date_updated" not in columns:
        today = date.today().isoformat()
        connection.execute(
            f"ALTER TABLE Vendor_Listings ADD COLUMN date_updated TEXT NOT NULL DEFAULT '{today}'"
        )

    if "is_available" not in columns:
        connection.execute(
            "ALTER TABLE Vendor_Listings ADD COLUMN is_available INTEGER NOT NULL DEFAULT 1"
        )


if __name__ == "__main__":
    create_database()
    print(f"Database created at: {DB_PATH}")
