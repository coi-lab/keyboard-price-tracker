# Project Context
We are executing a data accuracy and pricing normalization overhaul across our scrapers. We need to fix broken Kinetic Labs link paths, eliminate non-switch clutter (stems, sample packs), implement vendor-specific quantity parsing, and prioritize native "price per switch" values.

# Files to Update
`scrapers/kineticlabs_scraper.py`
`scrapers/kbdfans_scraper.py`
`scrapers/divinikey_scraper.py`

# Anti-Slop & Token Rules
- Follow guard clauses: Exit early on errors or non-switch items.
- Output ONLY the modified code blocks or functions (Diffs Only). No full-file rewrites.

# Instructions for Codex

## 1. Kinetic Labs: Absolute URL Path Fix
- The scraper is defaulting links to the homepage. Inspect the parsed elements and ensure the link builder strictly constructs the absolute URL pattern: `https://kineticlabs.com/switches/[brand]/[switch-handle]`. 
- If the brand or handle cannot be extracted cleanly, fall back to parsing the exact `href` attribute from the primary product card anchor tag and join it with the absolute domain. Do not save raw relative or truncated links.

## 2. All Scrapers: Global Blacklist Filter
To stop parts and sample packs from messing up the "Highest Price" sorting, add a strict title filter before parsing any listing.
- **Action:** If the product title contains any of these blacklisted terms, SKIP the item entirely: `["sample pack", "tester pack", "stem", "spring", "housing", "lube", "film", "puller", "opener", "accessory"]`.
- This will instantly block items like "Lichicx Raw Silent Switches - Sample Pack" or separate "Switch Stems" from polluting the database.

## 3. Data Extraction: Native Price Per Switch Priority
Before executing any manual regex math on the title or specs, search the page source/JSON metadata for a native "price per switch" display.
- **Logic:** If a text string matching `$[0-9.]+ / switch` or similar pattern exists natively on the product page, parse that float directly as the `unit_price` and bypass manual quantity division.

## 4. Vendor-Specific Quantity & Pricing Adjustments
If no native price-per-switch is found, apply these strict fallback rules:
- **KBDFans Pre-lubed Switches:** These are bulk variants. Ensure the deep-dive specs parser extracts the exact multi-pack count (e.g., 70, 90, or 110 pieces) and divides the total price correctly.
- **Gateron Switches:** Standardize a fallback rule where if the vendor is selling a bulk box (common with Gateron 35-packs), the engine must find the "35" modifier in the title, tags, or variant dropdown JSON to compute the correct per-switch cost.
- **Divinikey Card Quantities:** Divinikey frequently lists quantities directly on the product grid card (e.g., "36-pack", "10-pack"). Update the collection parser to scrub the card text for package quantities before evaluating the price.

## 5. Self-Improvement Mandate
Autonomously update the `project-skills.md` file to document the global blacklist filter keywords and the native "price-per-switch" parsing optimization.