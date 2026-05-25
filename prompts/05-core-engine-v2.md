# Project Context
Upgrade our `core_engine.py` to handle relational vendor pricing and fuzzy string matching for a mechanical keyboard price tracker.

# Tech Stack
Python, SQLite, thefuzz (for fuzzy matching)

# Core Requirements
1. **Database Schema Update:**
   - Update `Keyboard_Items` table to: `(id, name, brand)`
   - Create a new `Vendor_Listings` table: `(id, item_id, vendor_name, retail_price, source_url, date_updated)`

2. **Fuzzy Name Matching:**
   - Import `process` and `fuzz` from `thefuzz`.
   - Create a function `find_existing_item(scraped_name)` that queries the `Keyboard_Items` table.
   - Use `fuzz.token_set_ratio` to compare `scraped_name` against existing database items.
   - If a match is found with a score of **85 or higher**, return the existing `item_id`.
   - If no match reaches the 85 threshold, return `None`.

3. **Update the Save Logic:**
   - Update the `save_item_data(name, brand, vendor_name, retail_price, source_url)` function.
   - First, call `find_existing_item(name)`. 
   - If the item doesn't exist, insert it into `Keyboard_Items` to generate a new `item_id`.
   - Finally, insert the pricing data into the `Vendor_Listings` table using that `item_id` and the `vendor_name`.

# Instructions for Codex
Generate the updated `core_engine.py` script. Include brief comments explaining how the fuzzy matching threshold works.