import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).with_name("mech_key_watcher.db")


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

    -- Each price history row belongs to one keyboard item.
    -- Deleting a keyboard item also removes its related price records.
    FOREIGN KEY (item_id)
        REFERENCES Keyboard_Items (id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_price_history_item_id
    ON Price_History (item_id);

CREATE INDEX IF NOT EXISTS idx_price_history_date_recorded
    ON Price_History (date_recorded);
"""


def create_database(db_path: Path = DB_PATH) -> None:
    with sqlite3.connect(db_path) as connection:
        connection.executescript(SCHEMA)


if __name__ == "__main__":
    create_database()
    print(f"Database created at: {DB_PATH}")
