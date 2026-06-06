# PROJECT: MechKeyWatcher - Mechanical Keyboard Switch Price Tracker

## 1. Current Tech Stack & Architecture
- **Backend:** Python, SQLite, Flask.
- **Database:** `switch_prices.db` in the project root. Do not use the older `keyboard_prices.db` name.
- **Schema owner:** `core/core_engine.py` is the primary runtime schema and persistence layer; `create_database.py` mirrors/bootstraps the same database for manual setup.
- **Core tables:**
  - `Keyboard_Items`: canonical switch rows with `name` and `brand`.
  - `Vendor_Listings`: SCD Type 2 vendor price history with normalized `price`, `is_in_stock`, `valid_from`, `valid_to`, plus legacy/display fields `retail_price`, `quantity`, `unit_price`, `source_url`, `date_updated`, and `is_available`.
- **Core engine:** `save_item_data()` initializes/migrates schema, fuzzy-matches to an existing canonical item, and only writes a new listing row when the active unit price or stock status changes.
- **Matching:** Uses `thefuzz.fuzz.token_sort_ratio` at threshold `82`, after `clean_switch_name()`, with hard conflicts for protected variants, colors, explicit switch types, and trailing single-letter suffixes.
- **HTTP/parsing:** `requests`, `BeautifulSoup`, JSON parsing where available, and a shared browser-like `USER_AGENT`.
- **Frontend:** Flask + Jinja + vanilla HTML/CSS/JS in `templates/index.html`.
- **Current UI style:** Dense three-column master/detail app with neutral off-white panels, black/white controls, compact 6-8px radii, and a dark purple detail pane. The old "Bubbly Cloud Theme" is no longer the live UI direction.

## 2. Active Commands
- Install dependencies: `pip install -r requirements.txt`
- Initialize/update database schema: `python create_database.py` or `python -m core.core_engine`
- Run the web app: `python app.py`
- Run a scraper: `python scrapers/[filename].py`
- Test a scraper quickly: `python scrapers/[filename].py --max-pages 1 --delay 0`
- Known scrapers:
  - `python scrapers/kbdfans_scraper.py --max-pages 1 --delay 0`
  - `python -m scrapers.kineticlabs_scraper --max-pages 1 --delay 0`
  - `python scrapers/cannonkeys_scraper.py --max-pages 1 --delay 0`
  - `python scrapers/divinikey_scraper.py --max-pages 1 --delay 0`
  - `python scrapers/milktooth_scraper.py --max-pages 1 --delay 0`

## 3. Runtime Behavior To Preserve
- The Flask app calls `initialize_database(DB_PATH)` at startup and serves `switch_prices.db`.
- `/` renders active listings with `valid_to IS NULL`, then orders available switches first.
- `/api/switch/<id>` returns the canonical switch plus latest vendor listings sorted by availability, unit price, pack price, and vendor name.
- `Vendor_Listings` is SCD Type 2 history. UI/live-price queries must filter `valid_to IS NULL`; historical analysis can include closed rows where `valid_to IS NOT NULL`.
- Each switch should have at most one active listing per scraped website/vendor. If a scraper reruns with the same normalized unit price and stock status, `save_item_data()` skips the write. If either changes, it closes the old row with `valid_to = CURRENT_DATE` and inserts a new active row with `valid_from = CURRENT_DATE`.
- Preserve price observations even when a listing is sold out. The long-term product goal is price tracking and prediction, so availability should be stored as both current `is_in_stock`/legacy `is_available`, not used as a reason to discard a valid price row.
- `unit_price` is always `retail_price / quantity`; scrapers should preserve pack quantities so cross-vendor comparison is meaningful.
- `is_available` is an integer boolean (`0` or `1`). Available listings should sort ahead of sold-out listings, but sold-out prices may still be retained for context.

## 4. Scraper Conventions
- Every scraper must call `initialize_database()` before saving and use `save_item_data()` rather than writing SQL directly.
- Each scraper uses a frozen `Product` dataclass with at least `name`, `brand`, `retail_price`, `quantity`, and `source_url`; vendors that expose stock state also include `is_available`.
- Do not skip sold-out products solely because they are unavailable. Save them with `is_available=False` when the vendor still exposes a real price, URL, and quantity.
- Use `Decimal` for parsed prices inside scrapers, then convert to `float` only when calling `save_item_data()`.
- Normalize/deduplicate product URLs before saving. Query strings and variant URLs can create duplicate vendor/source rows if left uncleaned.
- Scraper HTTP helpers should handle `429 Too Many Requests` with exponential backoff before giving up. Respect `Retry-After` when present; otherwise retry with increasing sleeps such as `2.5s`, `5s`, `10s`, capped to a small retry budget.
- Prefer structured JSON/API sources when they are reliable, but keep HTML fallback parsers because vendor storefronts differ.
- Preserve vendor-specific parser quirks instead of forcing a single generic scraper abstraction.

## 5. Vendor-Specific Notes
- **KBDFans:** HTML collection parser. Product links can expose pack-size variant labels like `Switches x 30`; reject those as names and use them only as quantity evidence. Normalize product URLs by removing query strings.
- **Kinetic Labs:** Prefer the `kl-ssr-data` JSON script. Product URLs live under `/switches/{brand-slug}/{handle}`; `/products/{handle}` redirects to `/shop`, and `/switches/{handle}` can render a product title plus `No products found`.
- **CannonKeys:** Prefer embedded Shopify JSON, then `/collections/switches/products.json?limit=250&page=N`, then HTML fallback. Collection JSON currently returns a full page and the scraper stops after using it.
- **Divinikey:** Scrapes both available and out-of-stock filters. Product JSON enrichment via `/products/{handle}.js` is used to recover better quantity/variant data.
- **Milktooth:** Prefer the Meilisearch API at `https://meilisearch.milktooth.com/indexes/products_table/search` with `category_id = 1`. Default quantity is `10` when no pack size is discoverable.

## 6. Frontend Notes
- The list supports search, sorting, sold-out styling, and localStorage-backed pinning.
- Detail data is loaded asynchronously from `/api/switch/<id>`.
- Vendor cards render pack price, unit price, quantity, availability, date, and source links.
- `#price-history-chart` is reserved in the detail pane for future history visualization.
- No product image scraping is currently used; brand/vendor avatars are text initials.

## 7. Agent Learnings Log (AI: UPDATE THIS ACTIVELY)
- [Initial Config] Discovered the "Subset Trap" in fuzzy matching. Use `token_sort_ratio` instead of `set_ratio`/`token_set_ratio` to prevent short names from grouping with longer names.
- [Initial Config] Vendors use identical names for different switch variants. Check explicit color conflicts and variant tags before running fuzzy math.
- [Core Engine] `v1` must be treated as a protected variant alongside `v2` and `v3`; otherwise V1/V2 products compare too generously.
- [Core Engine] Color/variant conflict checks must run on original names before junk-word removal so protected words like `silent`, `box`, `milky`, and colors are not erased before comparison.
- [Core Engine] Packaging cleanup should run before punctuation normalization so patterns like `(10-pack)`, `x36`, `10pcs`, and `35 pcs` disappear cleanly.
- [Core Engine] Windows SQLite connection context managers commit/rollback but do not reliably close handles immediately; use explicit closing helpers around setup/search/save paths.
- [Core Engine] Historical repair is not automatic. Matching changes affect future saves, but existing `Vendor_Listings` rows cannot be safely reassigned unless original scraped names or slug-based migration evidence is available.
- [Core Engine] HMX `Retro J`, `Retro C`, `Retro R`, and `Retro T` need standalone trailing single-letter suffixes treated as protected identifiers.
- [Core Engine] Explicit switch type conflicts matter. Names like `Oil King Silent Tactile` and `Oil King Silent Linear` may score similarly after sanitizer cleanup, so compare explicit `linear`/`tactile`/`clicky` tags before accepting a fuzzy match.
- [Schema] The active database file is `switch_prices.db`; stale instructions naming `keyboard_prices.db` should be ignored.
- [Schema] `Vendor_Listings` uses SCD Type 2 effective dating. Active/live rows have `valid_to IS NULL`; old rows are closed with `valid_to` instead of being overwritten or deleted.
- [Frontend] The live UI is no longer the old pastel cloud theme. Preserve the current compact neutral/purple master-detail style unless the user explicitly asks for a redesign.
- [Scrapers] Scraper parsing is intentionally vendor-specific. Structured JSON should be preferred when present, but each vendor has different endpoints and fallbacks.
- [Kinetic Labs] Scraped product paths can be relative; normalize every extracted path with `urljoin("https://kineticlabs.com", href)` unless it already starts with `http`.
- [Kinetic Labs] Do not build product links as `/products/{handle}` or `/switches/{handle}`. The working canonical route is `/switches/{brand-slug}/{handle}` such as `/switches/gateron/oil-kings`; `/products/{handle}` redirects to `/shop`, and short `/switches/{handle}` can return HTTP 200 while rendering `No products found`.
- [Kinetic Labs] Variant quantities can appear as plain or trailing numbers such as `70`, `Silver 70`, `Black 18`, or in Shopify metafield JSON. Parse variant title/metafield quantity before falling back to product-name quantity inference; otherwise pack prices look like single-switch prices.
- [Scrapers] Apply the global non-switch blacklist before saving product rows: sample pack, tester pack, stem, spring, housing, lube, film, puller, opener, and accessory. These are valid keyboard products but not switch price observations.
- [Scrapers] When vendor page/JSON text exposes a native price-per-switch string like `$0.65 / switch`, prefer that unit price signal over title/spec quantity inference. Preserve the schema contract by deriving the pack quantity from `retail_price / native_unit_price` so `unit_price` remains computed consistently.
- [CannonKeys] Shopify JSON and HTML fallback both expose stock state. Preserve sold-out products with `is_available=0` instead of saving them as normal available listings.
- [KBDFans] Collection cards may expose pack prices without obvious quantities. Use card/name pack patterns first, then product-page variant labels/scripts to recover quantity; skip listings whose unit price remains outside `$0.15-$1.50`.
- [Core Engine] Variant matching now uses a mutually exclusive category dictionary for switch types, versions, materials/themes, and colors. Version terms conflict when one side differs or lacks the version; other categories conflict when both names contain different leftover terms after shared category terms are removed.
- [CannonKeys] Do not skip sold-out products. JSON variants with `available == false` and HTML cards containing `Sold Out`, `Out of Stock`, or `Unavailable` should still be saved with `is_available=0` so price history remains complete.
- [CannonKeys] Quantity can be embedded in SKU-like strings, e.g. `OA_SWITCH_110`; include `sku`/`barcode` fields in variant quantity inference before defaulting to one.
- [CannonKeys] `scrape_switch_collection()` works through a `ParseResult`; when logging collection JSON counts, use `len(parse_result.products)` rather than an out-of-scope `products` variable.
- [Divinikey] Product `.js` JSON can omit pack size even when the product page HTML/title contains it, e.g. `(18 Pack)` or `18 included in each pack`. If JSON enrichment still leaves quantity at `1`, fetch the product page HTML and infer quantity from the page text/native unit price.
- [Divinikey] Collection pagination is sensitive to rapid requests. Keep a fixed `2.5` second sleep at the end of each pagination loop even when test commands pass `--delay 0`, or the site may kick off the scraper.
- [Scrapers] Treat HTTP `429 Too Many Requests` as a retryable client error. Use exponential backoff and honor `Retry-After` headers before failing, especially for hosted daily automation where a single fast pagination loop can poison the run.
- [KBDFans] The scraper now performs a secondary product-page fetch for each collection product, with `time.sleep(1)` before the request. Quantity should come from product-page specs text using `extract_quantity_from_specs()`, default to `1`, and save only if computed unit price is within `$0.15-$1.50`.
- [KBDFans] Product specs can express pack size as `35 per unit` rather than `pcs`, `pieces`, or `pack`. Treat `unit` as quantity context and parse `(\d+) per unit`; otherwise the scraper can accidentally pick noisy quantity dropdown values like `8`.
- [Product Philosophy] The website is meant to build historical price intelligence and future price prediction. Scrapers should preserve unavailable/sold-out listings as observations whenever the price data is trustworthy; filtering should happen in the UI/query layer, not by dropping history at scrape time.
- [Code Quality] Core and scraper functions should follow the master directive's anti-slop rules: explicit type hints, guard clauses, descriptive boolean names, and small single-responsibility functions. Use typed helpers for repeated scrape-loop work such as page fetch, URL dedupe, normalization, and saving.
- [Schema] A switch should not show multiple active links from the same vendor. `Vendor_Listings` has a partial unique index on active `(item_id, vendor_name)` rows where `valid_to IS NULL`; app queries filter active rows rather than collapsing by date/source URL.
- [Database Automation] The SCD `price` column stores normalized unit price (`retail_price / quantity`) for change detection and forecasting. Keep `retail_price`, `quantity`, and `unit_price` populated for display/backward compatibility while automation transitions to `price`, `is_in_stock`, `valid_from`, and `valid_to`.
- [GitHub Actions] Daily scraper automation must run `scrapers/kbdfans_scraper.py` and commit `switch_prices.db`; the old names `kdbfans_scraper.py` and `keyboard_prices.db` are stale and will break or noop automation.
