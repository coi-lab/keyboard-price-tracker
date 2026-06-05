import sqlite3
import re
from contextlib import closing
from datetime import date
from pathlib import Path
from typing import Optional

import requests
from thefuzz import fuzz


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "switch_prices.db"
FUZZY_MATCH_THRESHOLD = 82
REQUEST_TIMEOUT = 20
JUNK_NAME_WORDS = [
    "switch",
    "switches",
    "mechanical",
    "keyboard",
    "custom",
    "linear",
    "tactile",
    "clicky",
    "smd",
    "rgb",
    "5-pin",
    "3-pin",
]
PROTECTED_VARIANTS = [
    "v1",
    "v2",
    "v3",
    "pro",
    "silent",
    "box",
    "ink",
    "milky",
    "u4t",
    "ks-3",
]
PROTECTED_COLORS = [
    "red",
    "blue",
    "brown",
    "black",
    "white",
    "yellow",
    "green",
    "orange",
    "clear",
    "silver",
    "pink",
    "purple",
    "cyan",
    "navy",
]
PROTECTED_SWITCH_TYPES = ["linear", "tactile", "clicky"]
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
    is_available INTEGER NOT NULL DEFAULT 1 CHECK (is_available IN (0, 1)),

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
        with closing(get_connection(db_path)) as connection:
            apply_schema(connection)
            connection.commit()
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


def clean_switch_name(name: str) -> str:
    normalized = name.lower()
    normalized = re.sub(r"\([^)]*\b(?:pack|pcs?|pieces?|switches?)\b[^)]*\)", " ", normalized)
    normalized = re.sub(r"\b\d+\s*[- ]?\s*(?:pack|pcs?|pieces?|switches?)\b", " ", normalized)
    normalized = re.sub(r"\bx\s*\d+\b|\b\d+\s*x\b", " ", normalized)

    for word in JUNK_NAME_WORDS:
        pattern = rf"(?<![a-z0-9]){re.escape(word)}(?![a-z0-9])"
        normalized = re.sub(pattern, " ", normalized)

    normalized = re.sub(r"[^a-z0-9+-]+", " ", normalized)
    return clean_text(normalized)


def has_variant_conflict(name1: str, name2: str) -> bool:
    identifiers = PROTECTED_VARIANTS + PROTECTED_COLORS
    for identifier in identifiers:
        in_name1 = has_identifier(name1, identifier)
        in_name2 = has_identifier(name2, identifier)
        if in_name1 != in_name2:
            return True

    types1 = find_switch_types(name1)
    types2 = find_switch_types(name2)
    if types1 and types2 and types1 != types2:
        return True

    suffix1 = trailing_single_letter_suffix(clean_switch_name(name1))
    suffix2 = trailing_single_letter_suffix(clean_switch_name(name2))
    if suffix1 != suffix2 and (suffix1 is not None or suffix2 is not None):
        return True

    return False


def has_identifier(name: str, identifier: str) -> bool:
    normalized = name.lower()
    token_pattern = re.escape(identifier).replace(r"\-", r"[-\s]?")
    return bool(re.search(rf"(?<![a-z0-9]){token_pattern}(?![a-z0-9])", normalized))


def find_switch_types(name: str) -> set[str]:
    return {
        switch_type
        for switch_type in PROTECTED_SWITCH_TYPES
        if has_identifier(name, switch_type)
    }


def trailing_single_letter_suffix(cleaned_name: str) -> Optional[str]:
    tokens = cleaned_name.split()
    if tokens and re.fullmatch(r"[a-z]", tokens[-1]):
        return tokens[-1]
    return None


def find_existing_item(scraped_name: str, db_path: Path = DB_PATH) -> Optional[int]:
    if not scraped_name:
        return None

    cleaned_scraped_name = clean_switch_name(scraped_name)
    if not cleaned_scraped_name:
        return None

    try:
        with closing(get_connection(db_path)) as connection:
            apply_schema(connection)
            rows = connection.execute(
                """
                SELECT id, name
                FROM Keyboard_Items
                """
            ).fetchall()
            connection.commit()
    except sqlite3.OperationalError as error:
        raise RuntimeError(
            f"Could not search existing items. The database may be locked or unavailable: {error}"
        ) from error

    best_item_id = None
    best_score = 0

    for item_id, item_name in rows:
        if has_variant_conflict(scraped_name, item_name):
            continue

        cleaned_item_name = clean_switch_name(item_name)
        if not cleaned_item_name:
            continue

        score = fuzz.token_sort_ratio(cleaned_scraped_name, cleaned_item_name)
        if score > best_score:
            best_score = score
            best_item_id = int(item_id)

    if best_score >= FUZZY_MATCH_THRESHOLD:
        return best_item_id

    return None


def save_item_data(
    name: str,
    brand: str,
    vendor_name: str,
    retail_price: float,
    source_url: str,
    quantity: int = 1,
    is_available: bool = True,
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
        with closing(get_connection(db_path)) as connection:
            apply_schema(connection)

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
                    date_updated,
                    is_available
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item_id,
                    vendor_name,
                    retail_price,
                    quantity,
                    unit_price,
                    source_url,
                    date.today().isoformat(),
                    int(is_available),
                ),
            )

            connection.commit()
            return item_id
    except sqlite3.OperationalError as error:
        raise RuntimeError(
            f"Could not save item data. The database may be locked or unavailable: {error}"
        ) from error
    except sqlite3.DatabaseError as error:
        raise RuntimeError(f"Database error while saving item data: {error}") from error


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
