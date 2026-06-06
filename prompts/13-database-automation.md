# Project Context
We are preparing the project for daily cloud automation. To prevent the SQLite database from exploding in size with duplicate daily entries, we are implementing "Effective Dating" (SCD Type 2) and tracking out-of-stock items rather than deleting them.

# Files to Update
`core/database_setup.py` (or your DB initialization script)
`core/core_engine.py` (specifically the `save_item_data` function)

# Instructions for Codex

## 1. Schema Update (Effective Dating & Stock Status)
Update the SQL creation tables for the pricing/vendor listings. 
- Ensure the listings table has these columns: `price` (REAL), `is_in_stock` (BOOLEAN), `valid_from` (DATE), and `valid_to` (DATE).
- Remove any old "snapshot date" columns if they exist.

## 2. Core Logic Update: `save_item_data`
Rewrite the saving logic to strictly follow this Effective Dating flow:
- When a scraped item is passed to the function, query the database for the *currently active* listing for this specific switch and vendor (where `valid_to` IS NULL).
- **Condition A (No Change):** If the active listing exists, AND the scraped `price` equals the active `price`, AND the scraped `is_in_stock` equals the active `is_in_stock`, DO NOTHING. Skip the database write entirely.
- **Condition B (State Change):** If the price or stock status is different (or if the item has never been seen before):
  1. Update the old active row: SET `valid_to` = `CURRENT_DATE`.
  2. Insert the new scraped data as a new row: SET `valid_from` = `CURRENT_DATE` and `valid_to` = `NULL`.

## 3. Self-Improvement Mandate
Autonomously update the `project-skills.md` file to document the new SCD Type 2 (Effective Dating) database architecture. Explain that scripts must filter by `valid_to IS NULL` to get live prices, and note that stock status is now preserved historically.