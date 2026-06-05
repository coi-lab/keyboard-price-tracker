# Project Context
Overhaul the string matching logic in `core_engine.py` to fix the "Subset Trap," implement strict color/variant conflict checking, and remove junk words for mechanical keyboard switches.

# Tech Stack
Python, SQLite, thefuzz, re (RegEx)

# Step 1: The Sanitizer Function
Create a function `clean_switch_name(name)` that uses RegEx to lower the string and remove junk words.
- Remove words: "switch", "switches", "mechanical", "keyboard", "custom", "linear", "tactile", "clicky", "smd", "rgb", "5-pin", "3-pin".
- Remove packaging text: (e.g., "(10-pack)", "x36", "10pcs", "35 pcs").
- Strip extra whitespace.

# Step 2: The Variant & Color Hard-Check Function
Create `has_variant_conflict(name1, name2)` to prevent mismatched identifiers.
- **Variants:** `["v2", "v3", "pro", "silent", "box", "ink", "milky", "u4t", "ks-3"]`.
- **Colors:** `["red", "blue", "brown", "black", "white", "yellow", "green", "orange", "clear", "silver", "pink", "purple", "cyan", "navy"]`.
- **Logic:** Check which variants/colors exist in `name1` and `name2`. If one string contains a specific variant or color that the other does *not*, return `True` (conflict). Otherwise, return `False`.

# Step 3: Overhaul `find_existing_item(scraped_name)`
1. Pass the `scraped_name` through `clean_switch_name()`.
2. Query the `Keyboard_Items` table.
3. Loop through database items. For each item:
   a. Clean the database item name.
   b. Call `has_variant_conflict()`. If `True`, `continue` (skip this iteration).
   c. If no conflict, calculate `fuzz.token_sort_ratio` of the cleaned names.
4. If the highest score is **>= 82**, return the `item_id`.
5. If no match reaches the threshold, return `None`.

# Instructions for Codex
Rewrite the relevant matching functions in `core_engine.py`. Ensure the engine correctly aborts matches between "Gateron Black" and "Gateron Milky Yellow Black", prevents "V1" and "V2" merges, and correctly separates similarly named HMX switches.

# Implementation Findings
- `token_set_ratio` caused the subset trap because names like "Gateron Black" can score as a perfect subset of "Gateron Milky Yellow Black". The matcher now loops manually and uses `fuzz.token_sort_ratio` after sanitizing names.
- `v1` must be treated as a protected variant even though the initial variant list only named `v2` and `v3`; otherwise "V1" and "V2" products can still be compared too generously.
- Color/variant conflict checks need to run on the original names before junk-word removal so protected words like `silent`, `box`, `milky`, and colors are not accidentally removed before comparison.
- Packaging cleanup should run before punctuation normalization. This lets patterns like `(10-pack)`, `x36`, `10pcs`, and `35 pcs` disappear without leaving noisy fragments.
- Windows SQLite tests exposed that connection context managers commit/rollback but do not reliably close the database handle immediately. Core database setup/search/save paths now explicitly close connections after use.
- This matcher change affects future saves. It does not automatically reassign old `Vendor_Listings` rows that were already merged under the wrong `Keyboard_Items` id, because the listings table currently stores vendor URL/price but not the original scraped product name. A safe historical repair needs either the original scraped names or a slug-based migration pass.
- A clean rescrape showed HMX `Retro J`, `Retro C`, `Retro R`, and `Retro T` still merged because their only distinguishing token is a trailing single letter. The matcher now treats standalone trailing single-letter suffixes as protected identifiers.
- The clean rescrape also showed scraper-side junk listings such as KBDFans `Switches x 30/50/70/90/100`; this is a scraper parsing quality issue rather than a fuzzy matching issue.
- Another clean rescrape showed names with explicit different switch types can merge after sanitizer removal, e.g. `Oil King Silent Tactile` vs `Oil King Silent Linear`, `Milky Pro Silent Tactile` vs `Milky Pro Silent Linear`, and `Ice King Tactile` vs `Ice King Linear`. The matcher now allows type words to be removed for scoring, but treats them as a conflict when both compared names explicitly include different switch types.
- KBDFans product cards can expose pack-size variant labels through product links, including `Switches x 30` and descriptor variants like `Magnetic Switches x 65`. The KBDFans scraper now rejects those labels as product names, normalizes product URLs by dropping query strings, and keeps pack-size text only as quantity evidence.
