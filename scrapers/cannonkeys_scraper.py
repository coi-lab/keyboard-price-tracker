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


BASE_URL = "https://cannonkeys.com"
COLLECTION_URL = f"{BASE_URL}/collections/switches"
DEFAULT_BRAND = "CannonKeys"
VENDOR_NAME = "CannonKeys"


@dataclass(frozen=True)
class Product:
    name: str
    brand: str
    retail_price: Decimal
    quantity: int
    source_url: str


@dataclass(frozen=True)
class ParseResult:
    products: list[Product]
    used_collection_json: bool


def scrape_switch_collection(delay_seconds: float = 2.0, max_pages: Optional[int] = None) -> int:
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
        parse_result = parse_products(html, session, page)
        products = parse_result.products

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

        if parse_result.used_collection_json:
            print(f"Shopify collection JSON returned {len(products)} products on page {page}. Stopping.")
            break

        if not has_next_page(html, page):
            print(f"No next-page link found after page {page}. Stopping.")
            break

        page += 1
        time.sleep(delay_seconds)

    return saved_count


def build_page_url(page: int) -> str:
    return f"{COLLECTION_URL}?page={page}"


def build_products_json_url(page: int) -> str:
    return f"{COLLECTION_URL}/products.json?limit=250&page={page}"


def parse_products(html: str, session: requests.Session, page: int) -> ParseResult:
    soup = BeautifulSoup(html, "html.parser")

    products = list(parse_products_from_script_json(soup))
    if products:
        return ParseResult(products=products, used_collection_json=False)

    products = list(parse_products_from_collection_json(session, page))
    if products:
        return ParseResult(products=products, used_collection_json=True)

    products = []
    for card in find_product_cards(soup):
        product = parse_product_card(card)
        if product is not None:
            products.append(product)

    return ParseResult(products=products, used_collection_json=False)


def parse_products_from_script_json(soup: BeautifulSoup) -> Iterable[Product]:
    seen_urls = set()

    for script in soup.find_all("script", type="application/json"):
        script_text = script.string or script.get_text()
        if not script_text:
            continue

        try:
            data = json.loads(script_text)
        except json.JSONDecodeError:
            continue

        for raw_product in iter_shopify_products(data):
            product = product_from_shopify_dict(raw_product)
            if product is None or product.source_url in seen_urls:
                continue

            seen_urls.add(product.source_url)
            yield product


def parse_products_from_collection_json(
    session: requests.Session,
    page: int,
) -> Iterable[Product]:
    try:
        response = session.get(build_products_json_url(page), timeout=20)
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, json.JSONDecodeError) as error:
        print(f"Could not parse CannonKeys collection JSON for page {page}: {error}")
        return

    for raw_product in data.get("products", []):
        product = product_from_shopify_dict(raw_product)
        if product is not None:
            yield product


def iter_shopify_products(value) -> Iterable[dict]:
    if isinstance(value, dict):
        if is_shopify_product(value):
            yield value

        for nested_value in value.values():
            yield from iter_shopify_products(nested_value)
    elif isinstance(value, list):
        for nested_value in value:
            yield from iter_shopify_products(nested_value)


def is_shopify_product(value: dict) -> bool:
    return (
        isinstance(value.get("title"), str)
        and isinstance(value.get("handle"), str)
        and isinstance(value.get("variants"), list)
    )


def product_from_shopify_dict(raw_product: dict) -> Optional[Product]:
    name = clean_text(raw_product.get("title", ""))
    handle = raw_product.get("handle", "")
    variant_price = price_from_variants(raw_product.get("variants", []), name)

    if not name or not handle or variant_price is None:
        return None
    price, quantity = variant_price

    return Product(
        name=name,
        brand=normalize_brand(raw_product.get("vendor")) or infer_brand(name),
        retail_price=price,
        quantity=quantity,
        source_url=urljoin(BASE_URL, f"/products/{handle}"),
    )


def price_from_variants(variants: list[dict], product_name: str) -> Optional[tuple[Decimal, int]]:
    available_options = []
    fallback_options = []

    for variant in variants:
        if not isinstance(variant, dict):
            continue

        price = parse_price_value(variant.get("price"))
        if price is None:
            continue

        quantity = infer_quantity(
            " ".join(
                str(value)
                for value in [
                    variant.get("title"),
                    variant.get("option1"),
                    variant.get("option2"),
                    variant.get("option3"),
                    product_name,
                ]
                if value
            )
        )
        fallback_options.append((price, quantity))
        if variant.get("available", True):
            available_options.append((price, quantity))

    options = available_options or fallback_options
    return min(options, key=lambda option: option[0]) if options else None


def parse_price_value(value) -> Optional[Decimal]:
    if value is None:
        return None

    try:
        if isinstance(value, int):
            return Decimal(value) / Decimal("100")
        return Decimal(str(value).replace("$", "").replace(",", "").strip())
    except InvalidOperation:
        return None


def normalize_brand(value: Optional[str]) -> Optional[str]:
    if not value:
        return None

    text = clean_text(value)
    ignored_vendor_labels = {"stocked", "preorder", "group buy", "switches"}
    if text.lower() in ignored_vendor_labels:
        return None

    return text


def find_product_cards(soup: BeautifulSoup) -> list:
    cards = soup.select(".product-block, .product-card, li.grid__item, .card")
    cards = [card for card in cards if find_product_link(card) is not None]
    if cards:
        return cards

    product_links = soup.select('a[href*="/products/"]')
    found_cards = []
    seen_urls = set()
    for link in product_links:
        source_url = urljoin(BASE_URL, link.get("href", ""))
        if source_url in seen_urls:
            continue

        card = find_priced_parent(link)
        if card is not None:
            seen_urls.add(source_url)
            found_cards.append(card)

    return found_cards


def find_priced_parent(link):
    current = link
    for _ in range(8):
        if current is None:
            return None

        if "$" in current.get_text(" ", strip=True):
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
        source_url=urljoin(BASE_URL, link.get("href", "")),
    )


def find_product_link(card):
    links = card.select('a[href*="/products/"]')
    return links[0] if links else None


def extract_name(card, link) -> str:
    selectors = [
        ".product-title",
        ".product-block__title",
        ".card__heading",
        ".title",
        "h1",
        "h2",
        "h3",
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
        ".vendor",
        ".product-vendor",
        "[data-product-vendor]",
        "[class*='vendor']",
        "[class*='brand']",
    ]
    for selector in selectors:
        element = card.select_one(selector)
        if element:
            brand = normalize_brand(element.get_text(" ", strip=True))
            if brand:
                return brand

    return None


def extract_price(card) -> Optional[Decimal]:
    selectors = [
        ".price__current",
        ".price",
        ".product-price",
        "[data-product-price]",
    ]
    prices = []
    for selector in selectors:
        for element in card.select(selector):
            prices.extend(parse_prices(element.get_text(" ", strip=True)))

    if not prices:
        prices = parse_prices(card.get_text(" ", strip=True))

    return min(prices) if prices else None


def parse_prices(text: str) -> list[Decimal]:
    matches = re.findall(r"\$\s*([0-9]+(?:,[0-9]{3})*(?:\.[0-9]{1,2})?)", text)
    prices = []
    for match in matches:
        try:
            prices.append(Decimal(match.replace(",", "")))
        except InvalidOperation:
            continue

    return prices


def infer_quantity(text: str) -> int:
    patterns = [
        r"\bpack\s*of\s*(\d+)\b",
        r"\b(\d+)\s*(?:switches|pcs|pieces)\b",
        r"\bx\s*(\d+)\b",
        r"\((\d+)\)",
        r"^\s*(\d+)\b",
        r"^\s*(\d+)\s*$",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            quantity = int(match.group(1))
            if quantity > 0:
                return quantity

    return 1


def infer_brand(name: str) -> str:
    brand_patterns = [
        ("Gateron", r"\bgateron\b"),
        ("Cherry", r"\bcherry\b"),
        ("Kailh", r"\bkailh\b"),
        ("JWK", r"\bjwk\b|\bjwick\b"),
        ("Tecsee", r"\btecsee\b"),
        ("KTT", r"\bktt\b"),
        ("SP-Star", r"\bsp[- ]?star\b"),
        ("Aflion", r"\baflion\b"),
        ("Durock", r"\bdurock\b"),
        ("TTC", r"\bttc\b"),
    ]

    for brand, pattern in brand_patterns:
        if re.search(pattern, name, re.IGNORECASE):
            return brand

    return DEFAULT_BRAND


def has_next_page(html: str, current_page: int) -> bool:
    soup = BeautifulSoup(html, "html.parser")
    next_link = soup.select_one('a[rel="next"], a.pagination__next, a[href*="page="]')

    if next_link and next_link.get("href"):
        next_page_match = re.search(r"[?&]page=(\d+)", next_link["href"])
        if next_page_match:
            return int(next_page_match.group(1)) > current_page

    return bool(soup.select_one(f'a[href*="page={current_page + 1}"]'))


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape CannonKeys switch prices.")
    parser.add_argument(
        "--delay",
        type=float,
        default=2.0,
        help="Seconds to wait between collection pages.",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Optional page limit for testing.",
    )
    args = parser.parse_args()

    total_saved = scrape_switch_collection(
        delay_seconds=args.delay,
        max_pages=args.max_pages,
    )
    print(f"Saved {total_saved} products.")


if __name__ == "__main__":
    main()
