# Project Context
Build the core database manager for a mechanical keyboard price tracker.

# Tech Stack
Python, SQLite

# Core Requirements
- Connect to the local `keyboard_prices.db` file.
- Create a reusable function named `save_item_data(name, brand, retail_price, source_url, aftermarket_price=None)` that inserts the data appropriately into the `Keyboard_Items` and `Price_History` tables.
- Include basic `try/except` blocks to handle database connection errors or locked files.

# Instructions for Codex
Generate the Python script (e.g., `core_engine.py`). Keep it modular so that external web scraper scripts can import and use the `save_item_data` function without needing to write their own SQL commands.