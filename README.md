# MechKeyWatcher

A Python and Flask project for tracking mechanical keyboard switch prices across multiple vendors.

## Status

Active development

## Overview

MechKeyWatcher collects keyboard switch listings from vendor websites, normalizes product names, stores current and historical prices in SQLite, and presents the data through a local Flask dashboard.

The project was built to explore web scraping, data cleaning, price normalization, fuzzy matching, database design, and lightweight web visualization. It is currently a prototype that focuses on mechanical keyboard switches, especially the challenge of comparing listings that use different names, pack quantities, vendors, and stock states.

## Features

- Vendor scrapers for keyboard switch product pages
- SQLite database for canonical switch items and vendor listings
- Fuzzy matching to merge similar switch names across vendors
- Unit price calculation from retail price and pack quantity
- Historical price windows using `valid_from` and `valid_to`
- Local Flask dashboard for browsing switches and vendor listings
- API endpoints for switch details and price history
- Chart.js-based frontend for visualizing historical listing data
- GitHub Actions workflow for scheduled scraper runs

## Tech Stack

- Language: Python
- Frameworks/Libraries: Flask, Beautiful Soup, Requests, thefuzz, Chart.js
- Database: SQLite
- Tools: GitHub Actions, argparse, npm-free Flask templates

## Folder Structure

```txt
MechKeyWatcher/
|-- .github/
|   `-- workflows/
|       `-- daily-scraper.yml
|-- core/
|   |-- __init__.py
|   `-- core_engine.py
|-- scrapers/
|   |-- cannonkeys_scraper.py
|   |-- divinikey_scraper.py
|   |-- kbdfans_scraper.py
|   |-- kineticlabs_scraper.py
|   |-- milktooth_scraper.py
|   `-- __init__.py
|-- templates/
|   `-- index.html
|-- app.py
|-- create_database.py
|-- requirements.txt
|-- switch_prices.db
`-- README.md
```

The `prompts/` folder contains project planning and AI prompt history. Local backup database files are present in the workspace but are not part of the core application structure.

## Setup

Create and activate a Python virtual environment:

```bash
python -m venv .venv
```

On Windows PowerShell:

```bash
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Create or migrate the SQLite database:

```bash
python create_database.py
```

## Usage

Run the local Flask dashboard:

```bash
python app.py
```

The app starts on:

```txt
http://127.0.0.1:5000
```

Run an individual scraper:

```bash
python scrapers/kbdfans_scraper.py
```

Some scrapers support test-friendly options:

```bash
python scrapers/kbdfans_scraper.py --max-pages 1 --delay 0
python scrapers/kineticlabs_scraper.py --max-pages 1 --delay 0
```

Other vendor scrapers use the same general direct-script pattern:

```bash
python scrapers/divinikey_scraper.py
python scrapers/cannonkeys_scraper.py
python scrapers/milktooth_scraper.py
```

## Results or Current Progress

The project currently includes working application structure for:

- Initializing and migrating the SQLite schema
- Saving keyboard item records
- Saving current vendor listings
- Closing old listings when price or stock state changes
- Calculating unit prices from pack quantities
- Serving a local dashboard from Flask
- Returning switch details through `/api/switch/<item_id>`
- Returning historical vendor price data through `/api/history/<item_id>`
- Running scheduled scraper jobs through GitHub Actions

The database file `switch_prices.db` is included in the project workspace and is used by the local app.

## Roadmap

- [ ] Continue improving vendor-specific scraping reliability
- [ ] Add stronger validation for scraped prices, quantities, and stock status
- [ ] Improve matching rules for similarly named switch variants
- [ ] Add tests for core matching, normalization, and database update behavior
- [ ] Add clearer logging for scraper failures and skipped products
- [ ] Review whether database files should be committed or generated locally
- [ ] Expand dashboard filtering, sorting, and historical trend views

## Lessons Learned

This project shows that scraping is only one part of a price tracker. The harder work is making messy product data comparable across vendors.

Important lessons include:

- Vendor pages often expose product data differently.
- Product names need normalization before comparison.
- Similar switch names can refer to different products, so fuzzy matching needs conflict rules.
- Pack quantities must be extracted carefully before comparing prices.
- Historical price tracking needs effective date windows, not just overwriting rows.
- Automated scraping should use delays and tolerate individual vendor failures.

## Notes

- This is a prototype and should not be treated as a guaranteed source of live pricing.
- Vendor websites can change structure, which may break individual scrapers.
- Scrapers should be run respectfully with delays to avoid unnecessary traffic.
- The GitHub Actions workflow runs several scrapers independently and continues if one vendor fails.
- Local database backups may exist in the folder but are not required for normal setup.
