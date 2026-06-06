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
MUTUALLY_EXCLUSIVE_CATEGORIES = {
    "switch_types": ["linear", "tactile", "clicky", "silent"],
    "versions": ["1.0", "v1", "2.0", "v2", "3.0", "v3", "pro", "plus", "v2.5"],
    "materials_themes": ["milky", "ink", "box", "jelly", "crystal", "oil", "water", "gaming", "speed"],
    "colors": [
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
        "latte",
        "matcha",
    ],
}
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
DAILY_UNIQUE_LISTING_INDEX_SQL = """
CREATE UNIQUE INDEX IF NOT EXISTS idx_vendor_listings_daily_unique
    ON Vendor_Listings (
        item_id,
        vendor_name,
        date_updated
    )
"""
DROP_DAILY_UNIQUE_LISTING_INDEX_SQL = "DROP INDEX IF EXISTS idx_vendor_listings_daily_unique"
INSERT_VENDOR_LISTING_SQL = """
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
"""
UPDATE_VENDOR_LISTING_SQL = """
UPDATE Vendor_Listings
SET
    retail_price = ?,
    quantity = ?,
    unit_price = ?,
    source_url = ?,
    is_available = ?
WHERE id = ?
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
    for category_name, terms in MUTUALLY_EXCLUSIVE_CATEGORIES.items():
        terms1 = find_category_terms(name1, terms)
        terms2 = find_category_terms(name2, terms)

        if category_name == "versions":
            if terms1 != terms2 and (terms1 or terms2):
                return True
            continue

        if terms1 and terms2 and (terms1 - terms2) and (terms2 - terms1):
            return True

    suffix1 = trailing_single_letter_suffix(clean_switch_name(name1))
    suffix2 = trailing_single_letter_suffix(clean_switch_name(name2))
    if suffix1 != suffix2 and (suffix1 is not None or suffix2 is not None):
        return True

    return False


def find_category_terms(name: str, terms: list[str]) -> set[str]:
    return {term for term in terms if has_identifier(name, term)}


def has_identifier(name: str, identifier: str) -> bool:
    normalized = name.lower()
    token_pattern = re.escape(identifier).replace(r"\-", r"[-\s]?").replace(r"\.", r"[\.\s-]?")
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

    rows = load_existing_items(db_path)
    best_item_id, best_score = find_best_item_match(scraped_name, cleaned_scraped_name, rows)
    if best_score >= FUZZY_MATCH_THRESHOLD:
        return best_item_id

    return None


def load_existing_items(db_path: Path = DB_PATH) -> list[tuple[int, str]]:
    try:
        with closing(get_connection(db_path)) as connection:
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

    return [(int(item_id), str(item_name)) for item_id, item_name in rows]


def find_best_item_match(
    scraped_name: str,
    cleaned_scraped_name: str,
    rows: list[tuple[int, str]],
) -> tuple[Optional[int], int]:
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

    return best_item_id, best_score


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
    validate_item_data(name, brand, vendor_name, retail_price, quantity)
    try:
        return persist_item_listing(
            name, brand, vendor_name, retail_price, source_url, quantity, is_available, db_path
        )
    except sqlite3.OperationalError as error:
        raise RuntimeError(
            f"Could not save item data. The database may be locked or unavailable: {error}"
        ) from error
    except sqlite3.DatabaseError as error:
        raise RuntimeError(f"Database error while saving item data: {error}") from error


def persist_item_listing(
    name: str,
    brand: str,
    vendor_name: str,
    retail_price: float,
    source_url: str,
    quantity: int,
    is_available: bool,
    db_path: Path,
) -> int:
    with closing(get_connection(db_path)) as connection:
        apply_schema(connection)

        item_id = find_existing_item(name, db_path=db_path)
        if item_id is None:
            item_id = _insert_keyboard_item(connection, name, brand)

        save_vendor_listing(
            connection=connection,
            item_id=item_id,
            vendor_name=vendor_name,
            retail_price=retail_price,
            quantity=quantity,
            source_url=source_url,
            is_available=is_available,
        )
        connection.commit()
        return item_id


def validate_item_data(
    name: str,
    brand: str,
    vendor_name: str,
    retail_price: float,
    quantity: int,
) -> None:
    if not name or not brand or not vendor_name:
        raise ValueError("name, brand, and vendor_name are required")

    if retail_price < 0:
        raise ValueError("retail_price cannot be negative")
    if quantity < 1:
        raise ValueError("quantity must be at least 1")


def save_vendor_listing(
    connection: sqlite3.Connection,
    item_id: int,
    vendor_name: str,
    retail_price: float,
    quantity: int,
    source_url: str,
    is_available: bool,
) -> None:
    listing_id = find_daily_listing_id(connection, item_id, vendor_name)
    if listing_id is not None:
        update_vendor_listing(connection, listing_id, retail_price, quantity, source_url, is_available)
        return

    insert_vendor_listing(connection, item_id, vendor_name, retail_price, quantity, source_url, is_available)


def find_daily_listing_id(
    connection: sqlite3.Connection,
    item_id: int,
    vendor_name: str,
) -> Optional[int]:
    row = connection.execute(
        """
        SELECT id
        FROM Vendor_Listings
        WHERE item_id = ?
          AND vendor_name = ?
          AND date_updated = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (item_id, vendor_name, date.today().isoformat()),
    ).fetchone()
    return None if row is None else int(row[0])


def update_vendor_listing(
    connection: sqlite3.Connection,
    listing_id: int,
    retail_price: float,
    quantity: int,
    source_url: str,
    is_available: bool,
) -> None:
    connection.execute(
        UPDATE_VENDOR_LISTING_SQL,
        (retail_price, quantity, retail_price / quantity, source_url, int(is_available), listing_id),
    )


def insert_vendor_listing(
    connection: sqlite3.Connection,
    item_id: int,
    vendor_name: str,
    retail_price: float,
    quantity: int,
    source_url: str,
    is_available: bool,
) -> None:
    connection.execute(
        INSERT_VENDOR_LISTING_SQL,
        vendor_listing_values(
            item_id=item_id,
            vendor_name=vendor_name,
            retail_price=retail_price,
            quantity=quantity,
            source_url=source_url,
            is_available=is_available,
        ),
    )


def vendor_listing_values(
    item_id: int,
    vendor_name: str,
    retail_price: float,
    quantity: int,
    source_url: str,
    is_available: bool,
) -> tuple[int, str, float, int, float, str, str, int]:
    return (
        item_id,
        vendor_name,
        retail_price,
        quantity,
        retail_price / quantity,
        source_url,
        date.today().isoformat(),
        int(is_available),
    )


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

    ensure_daily_listing_uniqueness(connection)
    connection.execute(DROP_DAILY_UNIQUE_LISTING_INDEX_SQL)
    connection.execute(DAILY_UNIQUE_LISTING_INDEX_SQL)


def ensure_daily_listing_uniqueness(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        DELETE FROM Vendor_Listings
        WHERE id NOT IN (
            SELECT MAX(id)
            FROM Vendor_Listings
            GROUP BY item_id, vendor_name, date_updated
        )
        """
    )


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
