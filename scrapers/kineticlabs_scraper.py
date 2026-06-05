import argparse
import json
import re
import sys
import time
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.core_engine import (
    USER_AGENT,
    clean_text,
    fetch_html,
    initialize_database,
    save_item_data,
)


BASE_URL = "https://kineticlabs.com"
SWITCHES_URL = f"{BASE_URL}/switches"
DEFAULT_BRAND = "Kinetic Labs"
VENDOR_NAME = "Kinetic Labs"


@dataclass(frozen=True)
class Product:
    name: str
    brand: str
    retail_price: Decimal
    quantity: int
    source_url: str


def scrape_switches(delay_seconds: float = 2.0, max_pages: Optional[int] = None) -> int:
    initialize_database()

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    saved_count = 0
    seen_urls: set[str] = set()
    page = 1

    while max_pages is None or page <= max_pages:
        page_url = build_page_url(page)
        print(f"Fetching page {page}: {page_url}")

        html = fetch_html(page_url, session)
        products = list(parse_products(html))

        if not products:
            print(f"No products found on page {page}. Stopping.")
            break

        new_products = [product for product in products if product.source_url not in seen_urls]
        if not new_products:
            print(f"Page {page} contained no new products. Stopping.")
            break

        for product in new_products:
            seen_urls.add(product.source_url)
            item_id = save_item_data(
                name=product.name,
                brand=product.brand,
                vendor_name=VENDOR_NAME,
                retail_price=float(product.retail_price),
                source_url=product.source_url,
                quantity=product.quantity,
            )
            saved_count += 1
            print(f"Saved #{item_id}: {product.name} - ${product.retail_price} / {product.quantity}")

        if not has_next_page(html):
            print(f"No next-page link found after page {page}. Stopping.")
            break

        page += 1
        time.sleep(delay_seconds)

    return saved_count


def build_page_url(page: int) -> str:
    if page <= 1:
        return SWITCHES_URL
    return f"{SWITCHES_URL}?page={page}"


def parse_products(html: str) -> Iterable[Product]:
    soup = BeautifulSoup(html, "html.parser")

    products = list(parse_products_from_ssr_data(soup))
    if products:
        yield from products
        return

    for card in find_product_cards(soup):
        product = parse_product_card(card)
        if product is not None:
            yield product


def parse_products_from_ssr_data(soup: BeautifulSoup) -> Iterable[Product]:
    script = soup.find("script", id="kl-ssr-data", type="application/json")
    if script is None:
        return

    try:
        data = json.loads(script.string or script.get_text())
    except json.JSONDecodeError:
        return

    seen_urls = set()
    for raw_product in iter_collection_products(data):
        product = product_from_collection_node(raw_product)
        if product is None or product.source_url in seen_urls:
            continue

        seen_urls.add(product.source_url)
        yield product


def iter_collection_products(data: dict) -> Iterable[dict]:
    collection_data = None
    for key, value in data.items():
        if key.startswith("getProductsByCollection"):
            collection_data = value
            break

    if not collection_data:
        return

    products = (
        collection_data.get("payload", {})
        .get("collectionByHandle", {})
        .get("products", {})
        .get("edges", [])
    )

    for edge in products:
        node = edge.get("node") if isinstance(edge, dict) else None
        if isinstance(node, dict):
            yield node


def product_from_collection_node(raw_product: dict) -> Optional[Product]:
    name = clean_text(raw_product.get("title", ""))
    handle = raw_product.get("handle", "")
    variant_price = price_from_variants(raw_product.get("variants", {}), name)

    if not name or not handle or variant_price is None:
        return None
    price, quantity = variant_price

    return Product(
        name=name,
        brand=normalize_brand(raw_product.get("vendor")) or infer_brand(name),
        retail_price=price,
        quantity=quantity,
        source_url=urljoin(BASE_URL, f"/switches/{handle}"),
    )


def price_from_variants(variants: dict, product_name: str) -> Optional[tuple[Decimal, int]]:
    options = []
    for edge in variants.get("edges", []):
        variant = edge.get("node") if isinstance(edge, dict) else None
        if not isinstance(variant, dict):
            continue

        price_amount = variant.get("priceV2", {}).get("amount")
        if price_amount is None:
            continue

        try:
            price = Decimal(str(price_amount))
        except InvalidOperation:
            continue

        quantity = infer_quantity(f"{variant.get('title', '')} {product_name}")
        options.append((price, quantity))

    return min(options, key=lambda option: option[0]) if options else None


def normalize_brand(value: Optional[str]) -> Optional[str]:
    if not value:
        return None

    text = clean_text(value)
    known_brands = {
        "kinetic": "Kinetic Labs",
        "kinetic labs": "Kinetic Labs",
        "gateron": "Gateron",
        "durock": "Durock",
        "tecsee": "Tecsee",
        "ttc": "TTC",
        "kailh": "Kailh",
        "cherry": "Cherry",
        "jwk": "JWK",
        "wuque studio": "Wuque Studio",
    }
    return known_brands.get(text.lower(), text)


def parse_products_from_json(soup: BeautifulSoup) -> Iterable[Product]:
    seen_urls = set()

    for script in soup.find_all("script"):
        script_text = script.string or script.get_text()
        if not script_text or "switches" not in script_text.lower():
            continue

        for raw_product in extract_product_dicts(script_text):
            product = product_from_dict(raw_product)
            if product is None or product.source_url in seen_urls:
                continue

            seen_urls.add(product.source_url)
            yield product


def extract_product_dicts(script_text: str) -> Iterable[dict]:
    decoder = json.JSONDecoder()
    for match in re.finditer(r'"(?:name|title)"\s*:', script_text):
        start = script_text.rfind("{", 0, match.start())
        if start == -1:
            continue

        try:
            value, _ = decoder.raw_decode(script_text[start:])
        except json.JSONDecodeError:
            continue

        if isinstance(value, dict):
            yield value


def product_from_dict(raw_product: dict) -> Optional[Product]:
    name = first_text_value(raw_product, ["name", "title", "productName"])
    path = first_text_value(raw_product, ["url", "href", "path", "slug", "handle"])
    price = first_price_value(raw_product)

    if not name or price is None:
        return None

    source_url = normalize_product_url(path, name)
    if "/switches/" not in source_url:
        return None

    return Product(
        name=clean_text(name),
        brand=first_text_value(raw_product, ["brand", "vendor", "manufacturer"]) or infer_brand(name),
        retail_price=price,
        quantity=infer_quantity(name),
        source_url=source_url,
    )


def find_product_cards(soup: BeautifulSoup) -> list:
    product_links = soup.select('a[href*="/switches/"]')
    cards = []
    seen_urls = set()

    for link in product_links:
        source_url = absolute_product_url(link.get("href", ""))
        if source_url in seen_urls or source_url == SWITCHES_URL:
            continue

        card = find_priced_parent(link)
        if card is not None:
            seen_urls.add(source_url)
            cards.append(card)

    return cards


def find_priced_parent(link):
    current = link
    for _ in range(10):
        if current is None:
            return None

        text = current.get_text(" ", strip=True)
        if "$" in text:
            return current

        current = current.parent

    return None


def parse_product_card(card) -> Optional[Product]:
    link = find_product_link(card)
    if link is None:
        return None

    name = extract_name(card, link)
    price = extract_price(card)
    if not name or price is None:
        return None

    return Product(
        name=clean_text(name),
        brand=extract_brand(card) or infer_brand(name),
        retail_price=price,
        quantity=infer_quantity(f"{name} {card.get_text(' ', strip=True)}"),
        source_url=absolute_product_url(link.get("href", "")),
    )


def find_product_link(card):
    links = card.select('a[href*="/switches/"]')
    return links[0] if links else None


def extract_name(card, link) -> str:
    selectors = [
        "h1",
        "h2",
        "h3",
        "[data-product-title]",
        "[class*='title']",
        "[class*='name']",
    ]
    for selector in selectors:
        element = card.select_one(selector)
        if element:
            text = clean_text(element.get_text(" ", strip=True))
            if text and "$" not in text:
                return text

    return clean_text(link.get("title") or link.get_text(" ", strip=True))


def extract_brand(card) -> Optional[str]:
    selectors = [
        "[data-product-vendor]",
        "[class*='brand']",
        "[class*='vendor']",
    ]
    for selector in selectors:
        element = card.select_one(selector)
        if element:
            text = clean_text(element.get_text(" ", strip=True))
            if text:
                return text

    return None


def infer_brand(name: str) -> str:
    brand_patterns = [
        ("Kinetic Labs", r"\bkinetic labs\b|\bkinetic\b"),
        ("Gateron", r"\bgateron\b"),
        ("Tecsee", r"\btecsee\b"),
        ("Durock", r"\bdurock\b"),
        ("TTC", r"\bttc\b"),
        ("Wuque Studio", r"\bwuque\b|\bws\b"),
        ("JWK", r"\bjwk\b"),
        ("Kailh", r"\bkailh\b"),
        ("Cherry", r"\bcherry\b"),
    ]

    for brand, pattern in brand_patterns:
        if re.search(pattern, name, re.IGNORECASE):
            return brand

    return DEFAULT_BRAND


def extract_price(card) -> Optional[Decimal]:
    return first_decimal(parse_prices(card.get_text(" ", strip=True)))


def first_price_value(raw_product: dict) -> Optional[Decimal]:
    price_keys = [
        "price",
        "salePrice",
        "retailPrice",
        "unitPrice",
        "amount",
        "priceRange",
    ]
    prices = []
    collect_values_for_keys(raw_product, price_keys, prices)

    parsed_prices = []
    for value in prices:
        parsed_prices.extend(parse_price_value(value))

    return first_decimal(parsed_prices)


def parse_price_value(value) -> list[Decimal]:
    if isinstance(value, (int, float)):
        decimal_value = Decimal(str(value))
        if decimal_value > 1000 and decimal_value == decimal_value.to_integral_value():
            decimal_value = decimal_value / Decimal("100")
        return [decimal_value]

    if isinstance(value, str):
        return parse_prices(value)

    if isinstance(value, dict):
        prices = []
        for nested in value.values():
            prices.extend(parse_price_value(nested))
        return prices

    if isinstance(value, list):
        prices = []
        for nested in value:
            prices.extend(parse_price_value(nested))
        return prices

    return []


def parse_prices(text: str) -> list[Decimal]:
    matches = re.findall(r"\$\s*([0-9]+(?:,[0-9]{3})*(?:\.[0-9]{1,2})?)", text)
    prices = []
    for match in matches:
        try:
            prices.append(Decimal(match.replace(",", "")))
        except InvalidOperation:
            continue

    return prices


def first_decimal(prices: list[Decimal]) -> Optional[Decimal]:
    valid_prices = [price for price in prices if price >= 0]
    return min(valid_prices) if valid_prices else None


def infer_quantity(text: str) -> int:
    patterns = [
        r"\bpack\s*of\s*(\d+)\b",
        r"\b(\d+)\s*(?:switches|pcs|pieces)\b",
        r"\bx\s*(\d+)\b",
        r"\((\d+)\)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            quantity = int(match.group(1))
            if quantity > 0:
                return quantity

    return 1


def first_text_value(raw_product: dict, keys: list[str]) -> Optional[str]:
    values = []
    collect_values_for_keys(raw_product, keys, values)
    for value in values:
        if isinstance(value, str):
            text = clean_text(value)
            if text:
                return text

    return None


def collect_values_for_keys(value, keys: list[str], output: list) -> None:
    key_set = {key.lower() for key in keys}
    if isinstance(value, dict):
        for key, nested_value in value.items():
            if str(key).lower() in key_set:
                output.append(nested_value)
            collect_values_for_keys(nested_value, keys, output)
    elif isinstance(value, list):
        for nested_value in value:
            collect_values_for_keys(nested_value, keys, output)


def normalize_product_url(path: Optional[str], name: str) -> str:
    if path:
        if path.startswith("http"):
            return path
        if path.startswith("/"):
            return absolute_product_url(path)
        if path.startswith("switches/"):
            return absolute_product_url(f"/{path}")
        if "/" not in path:
            return absolute_product_url(f"/switches/{path}")

    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return absolute_product_url(f"/switches/{slug}")


def absolute_product_url(extracted_url: Optional[str]) -> str:
    if not extracted_url:
        return BASE_URL
    if extracted_url.startswith("http"):
        return extracted_url
    return urljoin(BASE_URL, extracted_url)


def has_next_page(html: str) -> bool:
    soup = BeautifulSoup(html, "html.parser")
    next_link = soup.find(
        "a",
        string=lambda text: text is not None and clean_text(text).lower() == "next",
    )
    if next_link and next_link.get("href"):
        return True

    next_button = soup.find(
        "button",
        string=lambda text: text is not None and clean_text(text).lower() == "next",
    )
    return bool(next_button and not next_button.has_attr("disabled"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape Kinetic Labs switch prices.")
    parser.add_argument(
        "--delay",
        type=float,
        default=2.0,
        help="Seconds to wait between pages.",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Optional page limit for testing.",
    )
    args = parser.parse_args()

    total_saved = scrape_switches(delay_seconds=args.delay, max_pages=args.max_pages)
    print(f"Saved {total_saved} products.")


if __name__ == "__main__":
    main()
