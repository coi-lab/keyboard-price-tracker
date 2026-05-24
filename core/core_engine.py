import sqlite3
from datetime import date
from pathlib import Path
from typing import Optional


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "keyboard_prices.db"


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS Keyboard_Items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    brand TEXT NOT NULL,
    retail_price REAL NOT NULL CHECK (retail_price >= 0)
);

CREATE TABLE IF NOT EXISTS Price_History (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER NOT NULL,
    aftermarket_price REAL NOT NULL CHECK (aftermarket_price >= 0),
    date_recorded TEXT NOT NULL,
    source_url TEXT,

    -- Each history row belongs to one keyboard item.
    -- The foreign key keeps price records linked to valid items.
    FOREIGN KEY (item_id)
        REFERENCES Keyboard_Items (id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_keyboard_items_name_brand
    ON Keyboard_Items (name, brand);

CREATE INDEX IF NOT EXISTS idx_price_history_item_id
    ON Price_History (item_id);

CREATE INDEX IF NOT EXISTS idx_price_history_date_recorded
    ON Price_History (date_recorded);
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


def save_item_data(
    name: str,
    brand: str,
    retail_price: float,
    source_url: str,
    aftermarket_price: Optional[float] = None,
    db_path: Path = DB_PATH,
) -> int:
    """Save one keyboard item and its current price record.

    Returns the item id so scraper scripts can log or reuse it if needed.
    """
    if not name or not brand:
        raise ValueError("name and brand are required")

    recorded_price = retail_price if aftermarket_price is None else aftermarket_price
    if retail_price < 0 or recorded_price < 0:
        raise ValueError("prices cannot be negative")

    try:
        with get_connection(db_path) as connection:
            connection.executescript(SCHEMA)

            item_id = _find_item_id(connection, name, brand)
            if item_id is None:
                item_id = _insert_keyboard_item(connection, name, brand, retail_price)
            else:
                _update_retail_price(connection, item_id, retail_price)

            # Price_History stores one observed price per scrape/source.
            connection.execute(
                """
                INSERT INTO Price_History (
                    item_id,
                    aftermarket_price,
                    date_recorded,
                    source_url
                )
                VALUES (?, ?, ?, ?)
                """,
                (item_id, recorded_price, date.today().isoformat(), source_url),
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
    retail_price: float,
) -> int:
    cursor = connection.execute(
        """
        INSERT INTO Keyboard_Items (name, brand, retail_price)
        VALUES (?, ?, ?)
        """,
        (name, brand, retail_price),
    )
    return int(cursor.lastrowid)


def _update_retail_price(
    connection: sqlite3.Connection,
    item_id: int,
    retail_price: float,
) -> None:
    connection.execute(
        """
        UPDATE Keyboard_Items
        SET retail_price = ?
        WHERE id = ?
        """,
        (retail_price, item_id),
    )


if __name__ == "__main__":
    initialize_database()
    print(f"Database ready at: {DB_PATH}")
