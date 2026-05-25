import sqlite3
import re
from datetime import date
from pathlib import Path
from typing import Optional

import requests
from thefuzz import fuzz, process


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "switch_prices.db"
FUZZY_MATCH_THRESHOLD = 85
REQUEST_TIMEOUT = 20
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0 Safari/537.36"
)


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

    -- Each vendor listing belongs to one canonical keyboard item.
    -- Fuzzy matching helps multiple vendors point at the same item row.
    FOREIGN KEY (item_id)
        REFERENCES Keyboard_Items (id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_keyboard_items_name_brand
    ON Keyboard_Items (name, brand);

CREATE INDEX IF NOT EXISTS idx_vendor_listings_item_id
    ON Vendor_Listings (item_id);

CREATE INDEX IF NOT EXISTS idx_vendor_listings_vendor_name
    ON Vendor_Listings (vendor_name);

CREATE INDEX IF NOT EXISTS idx_vendor_listings_date_updated
    ON Vendor_Listings (date_updated);
"""


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path, timeout=10)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database(db_path: Path = DB_PATH) -> None:
    try:
        with get_connection(db_path) as connection:
            connection.executescript(SCHEMA)
    except sqlite3.OperationalError as error:
        raise RuntimeError(f"Could not initialize database at {db_path}: {error}") from error


def fetch_html(url: str, session: requests.Session) -> str:
    try:
        response = session.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.text
    except requests.RequestException as error:
        raise RuntimeError(f"Could not fetch {url}: {error}") from error


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def find_existing_item(scraped_name: str, db_path: Path = DB_PATH) -> Optional[int]:
    if not scraped_name:
        return None

    try:
        with get_connection(db_path) as connection:
            connection.executescript(SCHEMA)
            rows = connection.execute(
                """
                SELECT id, name
                FROM Keyboard_Items
                """
            ).fetchall()
    except sqlite3.OperationalError as error:
        raise RuntimeError(
            f"Could not search existing items. The database may be locked or unavailable: {error}"
        ) from error

    choices = {name: item_id for item_id, name in rows}
    if not choices:
        return None

    match = process.extractOne(
        scraped_name,
        choices.keys(),
        scorer=fuzz.token_set_ratio,
    )
    if match is None:
        return None

    matched_name, score = match
    # Scores are 0-100. At 85+, names are close enough to reuse the existing
    # canonical item row; below that, the scraper creates a new item.
    if score >= FUZZY_MATCH_THRESHOLD:
        return int(choices[matched_name])

    return None


def save_item_data(
    name: str,
    brand: str,
    vendor_name: str,
    retail_price: float,
    source_url: str,
    quantity: int = 1,
    db_path: Path = DB_PATH,
) -> int:
    """Save one keyboard item and one vendor-specific price listing.

    Returns the item id so scraper scripts can log or reuse it if needed.
    """
    if not name or not brand or not vendor_name:
        raise ValueError("name, brand, and vendor_name are required")

    if retail_price < 0:
        raise ValueError("retail_price cannot be negative")
    if quantity < 1:
        raise ValueError("quantity must be at least 1")

    unit_price = retail_price / quantity

    try:
        with get_connection(db_path) as connection:
            connection.executescript(SCHEMA)

            item_id = find_existing_item(name, db_path=db_path)
            if item_id is None:
                item_id = _insert_keyboard_item(connection, name, brand)

            # Vendor_Listings stores one observed vendor price per scrape.
            connection.execute(
                """
                INSERT INTO Vendor_Listings (
                    item_id,
                    vendor_name,
                    retail_price,
                    quantity,
                    unit_price,
                    source_url,
                    date_updated
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item_id,
                    vendor_name,
                    retail_price,
                    quantity,
                    unit_price,
                    source_url,
                    date.today().isoformat(),
                ),
            )

            return item_id
    except sqlite3.OperationalError as error:
        raise RuntimeError(
            f"Could not save item data. The database may be locked or unavailable: {error}"
        ) from error
    except sqlite3.DatabaseError as error:
        raise RuntimeError(f"Database error while saving item data: {error}") from error


def _find_item_id(
    connection: sqlite3.Connection,
    name: str,
    brand: str,
) -> Optional[int]:
    row = connection.execute(
        """
        SELECT id
        FROM Keyboard_Items
        WHERE name = ? AND brand = ?
        LIMIT 1
        """,
        (name, brand),
    ).fetchone()

    return None if row is None else int(row[0])


def _insert_keyboard_item(
    connection: sqlite3.Connection,
    name: str,
    brand: str,
) -> int:
    cursor = connection.execute(
        """
        INSERT INTO Keyboard_Items (name, brand)
        VALUES (?, ?)
        """,
        (name, brand),
    )
    return int(cursor.lastrowid)


if __name__ == "__main__":
    initialize_database()
    print(f"Database ready at: {DB_PATH}")
