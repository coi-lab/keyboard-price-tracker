# Project Context
We are upgrading the frontend UI to include a historical price graph inside the existing slide-out detail card. We need to implement a tabbed interface and use a JavaScript charting library (like Chart.js) to visualize the database's historical pricing data.

# Files to Update
`app.py` (To add a new API route for historical data)
`templates/index.html` (To add the tabs, canvas element, and Chart.js CDN)
`static/script.js` (To handle tab switching and chart rendering)
`static/styles.css` (To style the tabs)

# Instructions for Codex

## 1. The Python Backend (`app.py`)
- Create a new Flask route (e.g., `/api/history/<item_id>`) that fetches the historical pricing data for a specific switch.
- Query the `Vendor_Listings` table for all rows matching the `item_id`.
- The data returned must include the `vendor_name`, `price`, `valid_from`, `valid_to`, and `is_in_stock` status. Group or format this data so the frontend can easily parse it into separate lines per vendor.

## 2. The HTML & CSS (`index.html` & `styles.css`)
- Inject the Chart.js CDN into the `<head>` of the HTML.
- Inside the right-hand slide-out Detail Card, wrap the current live pricing list in a tabbed container.
- Create two tabs: "[ Live Prices ]" and "[ Historical Trends ]". 
- Create a hidden `<div>` for the Historical Trends tab that contains a `<canvas id="priceChart"></canvas>` element.
- Add minimal, clean CSS to style these tabs (e.g., active tab highlighting, hidden/block display logic).

## 3. The JavaScript Chart Logic (`script.js`)
- Write the JS logic to toggle the visibility between the Live Prices div and the Historical Trends div when the tabs are clicked.
- When the Historical Trends tab is clicked for a switch, fetch the data from the new `/api/history/` route.
- **Chart Rules:**
  - Initialize a new Chart.js instance on the canvas. Destroy any existing chart instance before drawing a new one.
  - **Multi-Line:** Create a separate dataset (line) for each unique vendor.
  - **Effective Dating (Step Chart):** Set `stepped: true` (or equivalent) on the datasets so the lines remain horizontally flat between date changes, rather than drawing diagonal slopes.
  - **Out of Stock Visualization:** If a data segment has `is_in_stock == false`, style that specific segment of the line differently (e.g., use a dashed `borderDash` array or lower the opacity) so the user knows it was sold out at that price.

## 4. Anti-Slop & Code Quality Standards
- Follow standard guard clauses.
- Output ONLY the modified code blocks or functions (Diffs Only). No full-file rewrites unless absolutely necessary for the HTML structure.