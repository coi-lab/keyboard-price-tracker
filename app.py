import sqlite3
from pathlib import Path

from flask import Flask, jsonify, render_template

from core.core_engine import initialize_database


PROJECT_ROOT = Path(__file__).resolve().parent
DB_PATH = PROJECT_ROOT / "switch_prices.db"

app = Flask(__name__)
initialize_database(DB_PATH)


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def latest_listings_cte() -> str:
    return """
        WITH latest_listings AS (
            SELECT listing.*
            FROM Vendor_Listings listing
            WHERE listing.id = (
                SELECT newer.id
                FROM Vendor_Listings newer
                WHERE newer.item_id = listing.item_id
                  AND newer.vendor_name = listing.vendor_name
                ORDER BY newer.date_updated DESC, newer.id DESC
                LIMIT 1
            )
        )
    """


@app.route("/")
def index():
    with get_connection() as connection:
        switches = connection.execute(
            latest_listings_cte()
            + """
            SELECT
                item.id,
                item.name,
                item.brand,
                COALESCE(
                    MIN(CASE WHEN listing.is_available = 1 THEN listing.unit_price END),
                    MIN(listing.unit_price)
                ) AS lowest_unit_price,
                COALESCE(
                    MIN(CASE WHEN listing.is_available = 1 THEN listing.retail_price END),
                    MIN(listing.retail_price)
                ) AS lowest_pack_price,
                COUNT(listing.id) AS listing_count,
                COALESCE(MAX(listing.is_available), 0) AS is_available
            FROM Keyboard_Items item
            LEFT JOIN latest_listings listing
                ON listing.item_id = item.id
            GROUP BY item.id, item.name, item.brand
            ORDER BY is_available DESC, item.name COLLATE NOCASE
            """
        ).fetchall()

    return render_template("index.html", switches=switches)


@app.route("/api/switch/<int:item_id>")
def switch_detail(item_id: int):
    with get_connection() as connection:
        item = connection.execute(
            """
            SELECT id, name, brand
            FROM Keyboard_Items
            WHERE id = ?
            """,
            (item_id,),
        ).fetchone()

        if item is None:
            return jsonify({"error": "Switch not found"}), 404

        listings = connection.execute(
            latest_listings_cte()
            + """
            SELECT
                vendor_name,
                retail_price,
                quantity,
                unit_price,
                source_url,
                date_updated,
                is_available
            FROM latest_listings
            WHERE item_id = ?
            ORDER BY is_available DESC, unit_price ASC, retail_price ASC, vendor_name COLLATE NOCASE
            """,
            (item_id,),
        ).fetchall()

    return jsonify(
        {
            "id": item["id"],
            "name": item["name"],
            "brand": item["brand"],
            "listings": [dict(listing) for listing in listings],
        }
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
