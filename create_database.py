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

CREATE INDEX IF NOT EXISTS idx_vendor_listings_valid_window
    ON Vendor_Listings (item_id, vendor_name, valid_from, valid_to);

"""
ACTIVE_UNIQUE_LISTING_INDEX_SQL = """
CREATE UNIQUE INDEX IF NOT EXISTS idx_vendor_listings_active_unique
    ON Vendor_Listings (item_id, vendor_name)
    WHERE valid_to IS NULL
"""
DROP_ACTIVE_UNIQUE_LISTING_INDEX_SQL = "DROP INDEX IF EXISTS idx_vendor_listings_active_unique"


def create_database(db_path: Path = DB_PATH) -> None:
    with closing(sqlite3.connect(db_path)) as connection:
        apply_schema(connection)
        connection.commit()


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


if __name__ == "__main__":
    create_database()
    print(f"Database created at: {DB_PATH}")
