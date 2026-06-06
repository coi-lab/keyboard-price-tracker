# Project Context
Build a three-column master-detail web application for our mechanical keyboard price tracker.

# Tech Stack
Python, Flask, SQLite, HTML, CSS, JavaScript (Vanilla)

# Design Language (Cloud Theme)
- Background: Soft off-white.
- Containers & Sidebar: Soft matte cloud blues with significant padding.
- Accents & Buttons: Pastel pinks and soft reds for interaction.
- Radii: Bubbly, large rounded borders (`border-radius: 16px`) on all components.
- No Images: Use text-based colored circle avatars for brands rather than product images.

# Interface & Layout Architecture
1. **Left Column (Sidebar Menu - 20% width):** Static navigation links (Home, Trends, Settings).
2. **Middle Column (Master Switch List - 45% width):** 
   - Fixed search bar at the top filtering `Keyboard_Items`.
   - Scrollable vertical list of unique switches showing Name, Brand, and Lowest Price.
3. **Right Column (Detail View Card - 35% width):**
   - Hidden by default; opens smoothly using JavaScript when a switch in the middle column is clicked.
   - Formatted as a single beautiful card displaying all `Vendor_Listings` for the selected item, sorted by price.
   - Includes styled redirect buttons for `source_url`.
   - **Future Reservation:** Include an empty placeholder element `<div id="price-history-chart">` at the bottom of this card for our upcoming historical data tracking.

# Instructions for Codex
Generate `app.py` and `templates/index.html`. Implement a lightweight JavaScript event listener so that clicking a switch item triggers an asynchronous fetch request (AJAX) to a Flask route `/api/switch/<id>`. This endpoint should query the database for all active prices for that switch ID and inject them directly into the Right Column detail card without reloading the entire page.