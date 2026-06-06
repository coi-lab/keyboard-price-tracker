# Project Context
We are executing a massive data normalization update. We need to fix broken scraping logic across three vendors AND upgrade our core matching engine to perfectly sort enthusiast switch variants using mutually exclusive keywords.

# Files to Update
`core/core_engine.py`
`scrapers/kineticlabs_scraper.py`
`scrapers/cannonkeys_scraper.py`
`scrapers/kbdfans_scraper.py`

# Instructions for Codex

## 1. Core Engine Update (Mutually Exclusive Variants)
Rewrite the `has_variant_conflict(name1, name2)` function in `core_engine.py` to use a "Mutually Exclusive Categories" system before running fuzzy math.
- Create dictionaries/sets of conflicting terms. If `name1` contains a word from a category, and `name2` contains a *different* word from that *same* category (or lacks it entirely for version modifiers), immediately return `True` (conflict).
- **Categories to implement:**
  - **Switch Types:** `["linear", "tactile", "clicky", "silent"]`
  - **Versions:** `["1.0", "v1", "2.0", "v2", "3.0", "v3", "pro", "plus", "v2.5"]`
  - **Materials/Themes:** `["milky", "ink", "box", "jelly", "crystal", "oil", "water", "gaming", "speed"]`
  - **Colors:** `["red", "blue", "brown", "black", "white", "yellow", "green", "orange", "clear", "silver", "pink", "purple", "cyan", "navy", "latte", "matcha"]`

## 2. Kinetic Labs Update (Broken Links & New Layout)
- The product cards on the website have changed. Update the HTML fallback parser to accurately target the new `<a>` tags and title elements on the collection page.
- **URL Normalization:** Ensure the URL construction strictly builds absolute URLs (e.g., `https://kineticlabs.com/switches/[brand]/[handle]`). Do not save relative links to the database.

## 3. CannonKeys Update (Out-of-Stock Filter)
- The scraper is pulling in sold-out items. Update both the JSON-first logic and the HTML fallback to verify stock status.
- If an item has `available == false` in the JSON, or the HTML tag contains "Sold Out", skip the item entirely and do not pass it to `save_item_data`.

## 4. KBDFans Update (Deep-Dive Quantity & Sanity Check)
- KBDFans hides switch pack quantities in the "Specs" section of individual product pages. 
- Update the loop: After finding a product on the main collection page, make a secondary `fetch_html()` request to that specific `source_url`.
- **Rate Limiting:** You MUST add `time.sleep(1)` before this secondary request to avoid IP bans.
- Create `extract_quantity_from_specs(html)` that looks for terms like "Quantity", "pcs", "pieces", or "pack" inside the product page.
- Divide the `raw_price` by this extracted quantity to get the true price-per-switch. Default to 1 if no quantity is found.
- **Sanity Check Filter:** Before calling `save_item_data`, check the final calculated price-per-switch. If it is `> $1.50` or `< $0.15`, log it as an anomaly and SKIP saving it.

## 5. Self-Improvement Mandate
Once you have successfully updated all four files, autonomously update the `project-skills.md` file in the root directory. Log the new KBDFans secondary-fetch architecture, the price sanity check parameters, and the Mutually Exclusive Conflict Dictionary system.