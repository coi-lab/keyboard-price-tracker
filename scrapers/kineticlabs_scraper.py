import argparse
import json
import re
import sys
import time
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

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
KINETIC_BRAND_SLUGS = {
    "bsun": "bsun",
    "cherry": "cherry",
    "chosfox": "chosfox",
    "durock": "durock",
    "gateron": "gateron",
    "hmx": "hmx",
    "jwk": "jwk",
    "kailh": "kailh",
    "kinetic": "kinetic",
    "kinetic labs": "kinetic",
    "ktt": "ktt",
    "tecsee": "tecsee",
    "ttc": "ttc",
    "wuque studio": "wuque-studios",
    "wuque studios": "wuque-studios",
}
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


def scrape_switches(delay_seconds: float = 2.0, max_pages: Optional[int] = None) -> int:
    initialize_database()

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    saved_count = 0
    seen_urls: set[str] = set()
    page = 1

    while max_pages is None or page <= max_pages:
        html, products = fetch_products_page(session, page)
        new_products = dedupe_products(products, seen_urls, page)
        if not new_products:
            break

        saved_count += save_products(new_products, seen_urls)

        if not has_next_page(html):
            print(f"No next-page link found after page {page}. Stopping.")
            break

        page += 1
        time.sleep(delay_seconds)

    return saved_count


def fetch_products_page(session: requests.Session, page: int) -> tuple[str, list[Product]]:
    page_url = build_page_url(page)
    print(f"Fetching page {page}: {page_url}")

    html = fetch_html(page_url, session)
    return html, list(parse_products(html))


def dedupe_products(products: list[Product], seen_urls: set[str], page: int) -> list[Product]:
    if not products:
        print(f"No products found on page {page}. Stopping.")
        return []

    new_products = [product for product in products if product.source_url not in seen_urls]
    if not new_products:
        print(f"Page {page} contained no new products. Stopping.")

    return new_products


def save_products(products: list[Product], seen_urls: set[str]) -> int:
    saved_count = 0
    for product in products:
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
    if not is_switch_product(raw_product, name):
        return None

    variant_price = price_from_variants(raw_product.get("variants", {}), name)
    if not name or not handle or variant_price is None:
        return None

    price, quantity = variant_price
    native_unit_price = extract_native_unit_price(json.dumps(raw_product, default=str))
    if native_unit_price is not None:
        quantity = quantity_from_unit_price(price, native_unit_price) or quantity

    brand = normalize_brand(raw_product.get("vendor")) or infer_brand(name)
    return Product(
        name=name,
        brand=brand,
        retail_price=price,
        quantity=quantity,
        source_url=build_product_url(handle, brand),
    )


def is_switch_product(raw_product: dict, name: str) -> bool:
    if is_blacklisted_title(name):
        return False

    product_type = clean_text(str(raw_product.get("productType", ""))).lower()
    if product_type and product_type != "switches":
        return False

    normalized_name = name.lower()
    excluded_terms = ["container", "fidget"]
    return not any(term in normalized_name for term in excluded_terms)


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

        quantity = infer_variant_quantity(variant, product_name)
        options.append((price, quantity))

    return min(options, key=lambda option: option[0]) if options else None


def infer_variant_quantity(variant: dict, product_name: str) -> int:
    metafield = variant.get("metafield")
    if isinstance(metafield, dict):
        quantity = quantity_from_metafield(metafield.get("value"))
        if quantity is not None:
            return quantity

    title_quantity = infer_quantity(str(variant.get("title", "")))
    if title_quantity > 1:
        return title_quantity

    return infer_quantity(f"{variant.get('title', '')} {product_name}")


def quantity_from_metafield(value: Any) -> Optional[int]:
    if not isinstance(value, str):
        return None

    try:
        data = json.loads(value)
    except json.JSONDecodeError:
        return None

    quantity = data.get("quantity", {}).get("quantity") if isinstance(data, dict) else None
    return int(quantity) if isinstance(quantity, int) and quantity > 0 else None


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

    if not name or is_blacklisted_title(name) or price is None:
        return None

    source_url = normalize_product_url(path, name)
    if "/switches/" not in source_url:
        return None

    native_unit_price = extract_native_unit_price(json.dumps(raw_product, default=str))
    quantity = infer_quantity(name)
    if native_unit_price is not None:
        quantity = quantity_from_unit_price(price, native_unit_price) or quantity

    return Product(
        name=clean_text(name),
        brand=first_text_value(raw_product, ["brand", "vendor", "manufacturer"]) or infer_brand(name),
        retail_price=price,
        quantity=quantity,
        source_url=source_url,
    )


def find_product_cards(soup: BeautifulSoup) -> list:
    product_links = soup.select(
        'a[href*="/switches/"], '
        'a[href*="/products/"], '
        'a[href^="switches/"], '
        'a[href^="/switches"]'
    )
    cards = []
    seen_urls = set()

    for link in product_links:
        source_url = absolute_product_url(link.get("href", ""))
        if source_url in seen_urls or not is_product_url(source_url):
            continue

        card = find_priced_parent(link)
        if card is not None:
            seen_urls.add(source_url)
            cards.append(card)

    return cards


def find_priced_parent(link: Tag) -> Optional[Tag]:
    current = link
    for _ in range(10):
        if current is None:
            return None

        text = current.get_text(" ", strip=True)
        if "$" in text:
            return current

        current = current.parent

    return None


def parse_product_card(card: Tag) -> Optional[Product]:
    link = find_product_link(card)
    if link is None:
        return None

    name = extract_name(card, link)
    price = extract_price(card)
    if not name or is_blacklisted_title(name) or price is None:
        return None

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
        source_url=absolute_product_url(link.get("href", "")),
    )


def find_product_link(card: Tag) -> Optional[Tag]:
    links = card.select(
        'a[href*="/switches/"], '
        'a[href*="/products/"], '
        'a[href^="switches/"], '
        'a[href^="/switches"]'
    )
    for link in links:
        source_url = absolute_product_url(link.get("href", ""))
        if is_product_url(source_url):
            return link

    return None


def extract_name(card: Tag, link: Tag) -> str:
    selectors = [
        "[data-testid*='product'][data-testid*='title']",
        "[data-product-title]",
        "[class*='ProductCard'][class*='title']",
        "[class*='product-card'][class*='title']",
        "[class*='productCard'][class*='title']",
        "[class*='product-title']",
        "[class*='productTitle']",
        "[class*='title']",
        "[class*='name']",
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


def extract_brand(card: Tag) -> Optional[str]:
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


def extract_price(card: Tag) -> Optional[Decimal]:
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


def parse_price_value(value: Any) -> list[Decimal]:
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
        r"^\s*(\d+)\b",
        r"\bpack\s*of\s*(\d+)\b",
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


def first_text_value(raw_product: dict, keys: list[str]) -> Optional[str]:
    values = []
    collect_values_for_keys(raw_product, keys, values)
    for value in values:
        if isinstance(value, str):
            text = clean_text(value)
            if text:
                return text

    return None


def collect_values_for_keys(value: Any, keys: list[str], output: list) -> None:
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
        normalized_path = path.strip()
        if normalized_path.startswith("http") or normalized_path.startswith("/"):
            return absolute_product_url(normalized_path)
        if normalized_path.startswith("products/"):
            return absolute_product_url(f"/{normalized_path}")
        if normalized_path.startswith("switches/"):
            return absolute_product_url(f"/{normalized_path}")
        if "/" not in normalized_path:
            return build_product_url(normalized_path, infer_brand(name))

    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return build_product_url(slug, infer_brand(name))


def build_product_url(handle: str, brand: str) -> str:
    clean_handle = handle.strip("/")
    if clean_handle.startswith("switches/"):
        return absolute_product_url(f"/{clean_handle}")

    brand_slug = brand_slug_from_name(brand)
    return absolute_product_url(f"/switches/{brand_slug}/{clean_handle}")


def brand_slug_from_name(brand: str) -> str:
    normalized_brand = clean_text(brand).lower()
    if normalized_brand in KINETIC_BRAND_SLUGS:
        return KINETIC_BRAND_SLUGS[normalized_brand]

    return re.sub(r"[^a-z0-9]+", "-", normalized_brand).strip("-")


def absolute_product_url(extracted_url: Optional[str]) -> str:
    if not extracted_url:
        return BASE_URL
    if extracted_url.startswith("http"):
        return extracted_url
    return urljoin(BASE_URL, extracted_url)


def is_product_url(url: str) -> bool:
    return (
        url.startswith(f"{BASE_URL}/products/")
        or url.startswith(f"{BASE_URL}/switches/")
    ) and url.rstrip("/") != SWITCHES_URL


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
