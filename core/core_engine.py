import sqlite3
import re
from contextlib import closing
from datetime import date
from pathlib import Path
from typing import Optional
import time
import requests
from requests.exceptions import RequestException

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
    price REAL NOT NULL DEFAULT 0 CHECK (price >= 0),
    retail_price REAL NOT NULL CHECK (retail_price >= 0),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price REAL NOT NULL CHECK (unit_price >= 0),
    source_url TEXT,
    valid_from TEXT NOT NULL DEFAULT (CURRENT_DATE),
    valid_to TEXT,
    is_in_stock INTEGER NOT NULL DEFAULT 1 CHECK (is_in_stock IN (0, 1)),
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

CREATE INDEX IF NOT EXISTS idx_vendor_listings_valid_window
    ON Vendor_Listings (item_id, vendor_name, valid_from, valid_to);
"""
ACTIVE_UNIQUE_LISTING_INDEX_SQL = """
CREATE UNIQUE INDEX IF NOT EXISTS idx_vendor_listings_active_unique
    ON Vendor_Listings (item_id, vendor_name)
    WHERE valid_to IS NULL
"""
DROP_DAILY_UNIQUE_LISTING_INDEX_SQL = "DROP INDEX IF EXISTS idx_vendor_listings_daily_unique"
DROP_ACTIVE_UNIQUE_LISTING_INDEX_SQL = "DROP INDEX IF EXISTS idx_vendor_listings_active_unique"
INSERT_VENDOR_LISTING_SQL = """
INSERT INTO Vendor_Listings (
    item_id,
    vendor_name,
    price,
    retail_price,
    quantity,
    unit_price,
    source_url,
    valid_from,
    valid_to,
    is_in_stock,
    date_updated,
    is_available
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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


def fetch_html(url: str, session: requests.Session, max_retries: int = 3) -> str | None:
    """Fetches HTML with exponential backoff for 429 Too Many Requests errors."""
    if not url:
        return None

    base_delay = 3.0  # Start with a 3-second delay on failure

    for attempt in range(max_retries):
        try:
            response = session.get(url, timeout=10)
            
            # If successful, return the text immediately
            if response.status_code == 200:
                return response.text
                
            # If rate-limited, trigger exponential backoff
            if response.status_code == 429:
                wait_time = base_delay * (2 ** attempt)
                print(f"[429 Rate Limit] Pausing for {wait_time}s before retrying {url}...")
                time.sleep(wait_time)
                continue
                
            # Handle other HTTP errors (e.g., 404 Not Found)
            response.raise_for_status()

        except RequestException as e:
            print(f"[Fetch Error] Attempt {attempt + 1}/{max_retries} failed for {url}: {e}")
            time.sleep(base_delay)
            
    print(f"❌ Failed to fetch {url} after {max_retries} attempts.")
    return None


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
    unit_price = retail_price / quantity
    active_listing = find_active_listing(connection, item_id, vendor_name)
    if active_listing is None:
        insert_vendor_listing(connection, item_id, vendor_name, retail_price, quantity, source_url, is_available)
        return

    if not has_listing_state_changed(active_listing, unit_price, is_available):
        return

    close_active_listing(connection, int(active_listing["id"]))
    insert_vendor_listing(connection, item_id, vendor_name, retail_price, quantity, source_url, is_available)


def find_active_listing(
    connection: sqlite3.Connection,
    item_id: int,
    vendor_name: str,
) -> Optional[sqlite3.Row]:
    connection.row_factory = sqlite3.Row
    row = connection.execute(
        """
        SELECT id, price, is_in_stock
        FROM Vendor_Listings
        WHERE item_id = ?
          AND vendor_name = ?
          AND valid_to IS NULL
        ORDER BY id DESC
        LIMIT 1
        """,
        (item_id, vendor_name),
    ).fetchone()
    return row


def has_listing_state_changed(
    active_listing: sqlite3.Row,
    unit_price: float,
    is_available: bool,
) -> bool:
    has_price_changed = round(float(active_listing["price"]), 6) != round(unit_price, 6)
    has_stock_changed = int(active_listing["is_in_stock"]) != int(is_available)
    return has_price_changed or has_stock_changed


def close_active_listing(
    connection: sqlite3.Connection,
    listing_id: int,
) -> None:
    connection.execute(
        """
        UPDATE Vendor_Listings
        SET valid_to = ?
        WHERE id = ?
        """,
        (date.today().isoformat(), listing_id),
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
    scraped_date: Optional[str] = None,
) -> tuple[int, str, float, float, int, float, str, str, Optional[str], int, str, int]:
    unit_price = retail_price / quantity
    valid_from = scraped_date or date.today().isoformat()
    return (
        item_id,
        vendor_name,
        unit_price,
        retail_price,
        quantity,
        unit_price,
        source_url,
        valid_from,
        None,
        int(is_available),
        valid_from,
        int(is_available),
    )


def apply_schema(connection: sqlite3.Connection) -> None:
    try:
        connection.executescript(SCHEMA)
    except sqlite3.OperationalError as error:
        if not is_recoverable_schema_error(error):
            raise

        ensure_vendor_listing_columns(connection)
        connection.executescript(SCHEMA)
    else:
        ensure_vendor_listing_columns(connection)

    connection.execute(DROP_DAILY_UNIQUE_LISTING_INDEX_SQL)
    connection.execute(DROP_ACTIVE_UNIQUE_LISTING_INDEX_SQL)
    migrate_vendor_listing_effective_dates(connection)
    connection.execute(ACTIVE_UNIQUE_LISTING_INDEX_SQL)


def is_recoverable_schema_error(error: sqlite3.OperationalError) -> bool:
    message = str(error)
    return any(
        column_name in message
        for column_name in ["date_updated", "is_available", "price", "is_in_stock", "valid_from", "valid_to"]
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

    if "price" not in columns:
        connection.execute(
            "ALTER TABLE Vendor_Listings ADD COLUMN price REAL NOT NULL DEFAULT 0"
        )

    if "is_in_stock" not in columns:
        connection.execute(
            "ALTER TABLE Vendor_Listings ADD COLUMN is_in_stock INTEGER NOT NULL DEFAULT 1"
        )

    if "valid_from" not in columns:
        today = date.today().isoformat()
        connection.execute(
            f"ALTER TABLE Vendor_Listings ADD COLUMN valid_from TEXT NOT NULL DEFAULT '{today}'"
        )

    if "valid_to" not in columns:
        connection.execute("ALTER TABLE Vendor_Listings ADD COLUMN valid_to TEXT")


def migrate_vendor_listing_effective_dates(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        UPDATE Vendor_Listings
        SET
            unit_price = retail_price / quantity,
            price = retail_price / quantity,
            is_in_stock = is_available,
            valid_from = COALESCE(NULLIF(valid_from, ''), date_updated)
        """
    )
    connection.execute(
        """
        UPDATE Vendor_Listings
        SET valid_to = valid_from
        WHERE id NOT IN (
            SELECT id
            FROM (
                SELECT
                    id,
                    ROW_NUMBER() OVER (
                        PARTITION BY item_id, vendor_name
                        ORDER BY valid_from DESC, date_updated DESC, id DESC
                    ) AS active_rank
                FROM Vendor_Listings
            )
            WHERE active_rank = 1
        )
        """
    )
    connection.execute(
        """
        UPDATE Vendor_Listings
        SET valid_to = NULL
        WHERE id IN (
            SELECT id
            FROM (
                SELECT
                    id,
                    ROW_NUMBER() OVER (
                        PARTITION BY item_id, vendor_name
                        ORDER BY valid_from DESC, date_updated DESC, id DESC
                    ) AS active_rank
                FROM Vendor_Listings
            )
            WHERE active_rank = 1
        )
        """
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
