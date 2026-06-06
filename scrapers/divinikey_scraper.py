import argparse
import json
import re
import sys
import time
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable, Optional
from urllib.parse import urljoin, urlparse, urlunparse

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


BASE_URL = "https://divinikey.com"
COLLECTION_URL = f"{BASE_URL}/collections/switches"
DEFAULT_BRAND = "Divinikey"
VENDOR_NAME = "Divinikey"
PAGINATION_DELAY_SECONDS = 2.5
BLACKLISTED_TITLE_TERMS = [
    "sample pack",
    "tester pack",
    "stem",
    "spring",
    "housing",
    "lube",
    "film",
    "puller",
    "opener",
    "accessory",
]
UNIT_PRICE_PATTERN = re.compile(
    r"\$\s*([0-9]+(?:\.[0-9]{1,4})?)\s*/\s*(?:switch|ea|each)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Product:
    name: str
    brand: str
    retail_price: Decimal
    quantity: int
    source_url: str
    is_available: bool = True


def scrape_switch_collection(delay_seconds: float = 2.0, max_pages: Optional[int] = None) -> int:
    initialize_database()

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    saved_count = 0
    seen_urls: set[str] = set()

    for availability_filter, availability_label in [(1, "available"), (0, "out of stock")]:
        page = 1

        while max_pages is None or page <= max_pages:
            page_url = build_page_url(page, availability_filter)
            print(f"Fetching {availability_label} page {page}: {page_url}")

            html = fetch_html(page_url, session)
            products = list(parse_products(html))

            if not products:
                print(f"No products found on {availability_label} page {page}. Stopping.")
                break

            new_products = [product for product in products if product.source_url not in seen_urls]
            if not new_products:
                print(f"{availability_label.title()} page {page} contained no new products. Stopping.")
                break

            for product in new_products:
                product = enrich_product_from_product_json(product, session)
                product = Product(
                    name=product.name,
                    brand=product.brand,
                    retail_price=product.retail_price,
                    quantity=product.quantity,
                    source_url=product.source_url,
                    is_available=availability_filter == 1,
                )
                seen_urls.add(product.source_url)
                item_id = save_item_data(
                    name=product.name,
                    brand=product.brand,
                    vendor_name=VENDOR_NAME,
                    retail_price=float(product.retail_price),
                    source_url=product.source_url,
                    quantity=product.quantity,
                    is_available=product.is_available,
                )
                saved_count += 1
                print(f"Saved #{item_id}: {product.name} - ${product.retail_price} / {product.quantity}")

            if not has_next_page(html, page):
                print(f"No next-page link found after {availability_label} page {page}. Stopping.")
                break

            page += 1
            time.sleep(PAGINATION_DELAY_SECONDS)

    return saved_count


def build_page_url(page: int, availability_filter: Optional[int] = None) -> str:
    if availability_filter is None:
        return f"{COLLECTION_URL}?page={page}"
    return f"{COLLECTION_URL}?filter.v.availability={availability_filter}&page={page}"


def parse_products(html: str) -> Iterable[Product]:
    soup = BeautifulSoup(html, "html.parser")

    products = list(parse_products_from_script_json(soup))
    if products:
        yield from products
        return

    for card in find_product_cards(soup):
        product = parse_product_card(card)
        if product is not None:
            yield product


def parse_products_from_script_json(soup: BeautifulSoup) -> Iterable[Product]:
    seen_urls = set()

    for script in soup.find_all("script"):
        script_text = script.string or script.get_text()
        if not script_text:
            continue

        script_type = script.get("type", "")
        if "application/json" not in script_type and "Shopify" not in script_text:
            continue

        for raw_product in extract_shopify_products(script_text):
            product = product_from_shopify_dict(raw_product)
            if product is None or product.source_url in seen_urls:
                continue

            seen_urls.add(product.source_url)
            yield product


def extract_shopify_products(script_text: str) -> Iterable[dict]:
    for value in parse_json_values(script_text):
        yield from iter_shopify_products(value)


def parse_json_values(script_text: str) -> Iterable:
    text = script_text.strip()
    if not text:
        return

    try:
        yield json.loads(text)
        return
    except json.JSONDecodeError:
        pass

    decoder = json.JSONDecoder()
    for match in re.finditer(r"[\[{]", script_text):
        try:
            value, _ = decoder.raw_decode(script_text[match.start() :])
        except json.JSONDecodeError:
            continue
        yield value


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

    if not name or is_blacklisted_title(name) or not handle or variant_price is None:
        return None
    price, quantity = variant_price
    native_unit_price = extract_native_unit_price(json.dumps(raw_product, default=str))
    if native_unit_price is not None:
        quantity = quantity_from_unit_price(price, native_unit_price) or quantity

    return Product(
        name=name,
        brand=normalize_brand(raw_product.get("vendor")) or infer_brand(name),
        retail_price=price,
        quantity=quantity,
        source_url=build_product_url(handle),
        is_available=any_available_variant(raw_product.get("variants", [])),
    )


def any_available_variant(variants: list[dict]) -> bool:
    if not variants:
        return True
    return any(variant.get("available", True) for variant in variants if isinstance(variant, dict))


def price_from_variants(variants: list[dict], product_name: str) -> Optional[tuple[Decimal, int]]:
    available_options = []
    fallback_options = []

    for variant in variants:
        if not isinstance(variant, dict):
            continue

        price = parse_price_value(variant.get("price"))
        if price is None:
            continue

        quantity = infer_quantity(variant_quantity_text(variant, product_name))
        fallback_options.append((price, quantity))
        if variant.get("available", True):
            available_options.append((price, quantity))

    options = available_options or fallback_options
    return min(options, key=lambda option: option[0]) if options else None


def variant_quantity_text(variant: dict, product_name: str) -> str:
    return " ".join(
        str(value)
        for value in [
            variant.get("title"),
            variant.get("public_title"),
            variant.get("option1"),
            variant.get("option2"),
            variant.get("option3"),
            product_name,
        ]
        if value
    )


def is_blacklisted_title(title: str) -> bool:
    normalized_title = title.lower()
    return any(term in normalized_title for term in BLACKLISTED_TITLE_TERMS)


def extract_native_unit_price(text: str) -> Optional[Decimal]:
    match = UNIT_PRICE_PATTERN.search(text)
    if match is None:
        return None

    try:
        return Decimal(match.group(1))
    except InvalidOperation:
        return None


def quantity_from_unit_price(retail_price: Decimal, unit_price: Decimal) -> Optional[int]:
    if unit_price <= 0:
        return None

    quantity = int((retail_price / unit_price).to_integral_value())
    return quantity if quantity > 0 else None


def parse_price_value(value) -> Optional[Decimal]:
    if value is None:
        return None

    try:
        if isinstance(value, int):
            return Decimal(value) / Decimal("100")
        decimal_value = Decimal(str(value).replace("$", "").replace(",", "").strip())
        if decimal_value > 1000 and decimal_value == decimal_value.to_integral_value():
            return decimal_value / Decimal("100")
        return decimal_value
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
    cards = soup.select(".card, .product-card, .product-block, li.grid__item, .slider__item")
    cards = [card for card in cards if find_product_link(card) is not None]
    if cards:
        return cards

    product_links = soup.select('a[href*="/products/"]')
    found_cards = []
    seen_urls = set()
    for link in product_links:
        source_url = clean_product_url(urljoin(BASE_URL, link.get("href", "")))
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
    if not name or is_blacklisted_title(name) or price is None:
        return None

    source_url = normalize_product_url(urljoin(BASE_URL, link.get("href", "")))
    card_text = card.get_text(" ", strip=True)
    native_unit_price = extract_native_unit_price(card_text)
    quantity = infer_quantity(f"{name} {card_text}")
    if native_unit_price is not None:
        quantity = quantity_from_unit_price(price, native_unit_price) or quantity

    return Product(
        name=clean_text(name),
        brand=extract_brand(card) or infer_brand(name),
        retail_price=price,
        quantity=quantity,
        source_url=source_url,
        is_available=not is_sold_out_text(card_text),
    )


def is_sold_out_text(text: str) -> bool:
    return bool(re.search(r"\bsold\s*out\b|\bunavailable\b", text, re.IGNORECASE))


def find_product_link(card):
    links = card.select('a[href*="/products/"]')
    return links[0] if links else None


def extract_name(card, link) -> str:
    selectors = [
        ".card__heading",
        ".card-link",
        ".product-title",
        ".product-block__title",
        "[data-product-title]",
        "h1",
        "h2",
        "h3",
        ".h6",
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
        ".js-value",
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
        r"\b(\d+)\s*-\s*pack\b",
        r"\b(\d+)\s*(?:set|pack)\b",
        r"\bpack\s*of\s*(\d+)\b",
        r"\b(\d+)\s+included\s+in\s+each\s+pack\b",
        r"\b(\d+)\s*(?:switches|pcs|pieces)\b",
        r"\bx\s*(\d+)\b",
        r"\((\d+)\)",
        r"\b(\d+)\s*$",
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
        ("Gazzew", r"\bgazzew\b|\bboba\b|\bu4t?\b"),
        ("Akko", r"\bakko\b"),
        ("Invokeys", r"\binvokeys?\b"),
    ]

    for brand, pattern in brand_patterns:
        if re.search(pattern, name, re.IGNORECASE):
            return brand

    return DEFAULT_BRAND


def clean_product_url(url: str) -> str:
    parsed = urlparse(url)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", "", ""))


def normalize_product_url(url: str) -> str:
    clean_url = clean_product_url(url)
    handle = product_handle_from_url(clean_url)
    if handle:
        return build_product_url(handle)
    return clean_url


def build_product_url(handle: str) -> str:
    return urljoin(BASE_URL, f"/products/{handle}")


def build_product_json_url(source_url: str) -> Optional[str]:
    handle = product_handle_from_url(source_url)
    if not handle:
        return None
    return urljoin(BASE_URL, f"/products/{handle}.js")


def product_handle_from_url(url: str) -> Optional[str]:
    parsed = urlparse(url)
    parts = [part for part in parsed.path.split("/") if part]
    if not parts:
        return None

    if "products" in parts:
        product_index = parts.index("products")
        if product_index + 1 < len(parts):
            return parts[product_index + 1]

    return None


def enrich_product_from_product_json(product: Product, session: requests.Session) -> Product:
    if product.quantity > 1:
        return product

    json_url = build_product_json_url(product.source_url)
    if json_url is None:
        return product

    try:
        response = session.get(json_url, timeout=20)
        response.raise_for_status()
        raw_product = response.json()
    except (requests.RequestException, json.JSONDecodeError):
        return product

    detailed_product = product_from_shopify_dict(raw_product)
    if detailed_product is None:
        return product

    enriched_product = Product(
        name=product.name,
        brand=detailed_product.brand or product.brand,
        retail_price=detailed_product.retail_price,
        quantity=detailed_product.quantity,
        source_url=detailed_product.source_url,
        is_available=detailed_product.is_available,
    )
    if enriched_product.quantity > 1:
        return enriched_product

    return enrich_quantity_from_product_page(enriched_product, session)


def enrich_quantity_from_product_page(product: Product, session: requests.Session) -> Product:
    try:
        html = fetch_html(product.source_url, session)
    except requests.RequestException:
        return product

    native_unit_price = extract_native_unit_price(html)
    if native_unit_price is not None:
        quantity = quantity_from_unit_price(product.retail_price, native_unit_price)
        if quantity is not None:
            return product_with_quantity(product, quantity)

    quantity = infer_quantity(BeautifulSoup(html, "html.parser").get_text(" ", strip=True))
    if quantity > 1:
        return product_with_quantity(product, quantity)

    return product


def product_with_quantity(product: Product, quantity: int) -> Product:
    return Product(
        name=product.name,
        brand=product.brand,
        retail_price=product.retail_price,
        quantity=quantity,
        source_url=product.source_url,
        is_available=product.is_available,
    )


def has_next_page(html: str, current_page: int) -> bool:
    soup = BeautifulSoup(html, "html.parser")
    next_link = soup.select_one('a[rel="next"], a.pagination__arrow--next[href], a.js-pagination-load-more[href]')
    if next_link and page_number_from_href(next_link.get("href")) > current_page:
        return True

    for link in soup.select('a[href*="page="]'):
        if page_number_from_href(link.get("href")) > current_page:
            return True

    return bool(soup.select_one(f'a[href*="page={current_page + 1}"]'))


def page_number_from_href(href: Optional[str]) -> int:
    if not href:
        return 0

    page_match = re.search(r"[?&]page=(\d+)", href)
    return int(page_match.group(1)) if page_match else 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape Divinikey switch prices.")
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
