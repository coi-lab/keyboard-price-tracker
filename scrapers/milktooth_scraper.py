import argparse
import json
import re
import sys
import time
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable, Optional
from urllib.parse import urlencode, urljoin

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


BASE_URL = "https://milktooth.com"
COLLECTION_URL = f"{BASE_URL}/products/switches"
SEARCH_URL = "https://meilisearch.milktooth.com/indexes/products_table/search"
SEARCH_API_KEY = "773b6692cef48e422add97a72e18a8c8309f2db33836cd05655ef99d3dcf4b2b"
SWITCH_CATEGORY_ID = 1
HITS_PER_PAGE = 40
DEFAULT_BRAND = "Milktooth"
DEFAULT_QUANTITY = 10
VENDOR_NAME = "Milktooth"


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
    page = 1

    while max_pages is None or page <= max_pages:
        page_url = build_page_url(page)
        print(f"Fetching page {page}: {page_url}")

        products, has_next = fetch_products_page(session, page)
        if not products:
            products = list(parse_products(fetch_html(page_url, session)))
            has_next = has_next_page_from_html(fetch_html(page_url, session), page)

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
                is_available=product.is_available,
            )
            saved_count += 1
            print(f"Saved #{item_id}: {product.name} - ${product.retail_price} / {product.quantity}")

        if not has_next:
            print(f"No next-page link found after page {page}. Stopping.")
            break

        page += 1
        time.sleep(delay_seconds)

    return saved_count


def build_page_url(page: int) -> str:
    return f"{COLLECTION_URL}?{urlencode({'products_table[page]': page})}"


def fetch_products_page(session: requests.Session, page: int) -> tuple[list[Product], bool]:
    try:
        response = session.post(
            SEARCH_URL,
            headers={
                "Authorization": f"Bearer {SEARCH_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "q": "",
                "limit": HITS_PER_PAGE,
                "offset": (page - 1) * HITS_PER_PAGE,
                "filter": f"category_id = {SWITCH_CATEGORY_ID}",
            },
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, json.JSONDecodeError) as error:
        print(f"Could not parse Milktooth search JSON for page {page}: {error}")
        return [], False

    products = [
        product
        for product in (product_from_search_hit(hit) for hit in data.get("hits", []))
        if product is not None
    ]
    offset = int(data.get("offset", (page - 1) * HITS_PER_PAGE))
    limit = int(data.get("limit", HITS_PER_PAGE))
    estimated_total = int(data.get("estimatedTotalHits", offset + len(products)))

    return products, offset + limit < estimated_total


def product_from_search_hit(hit: dict) -> Optional[Product]:
    name = clean_text(
        " ".join(str(value) for value in [hit.get("name"), hit.get("suffix")] if value)
    )
    price = parse_price_value(hit.get("price"))
    source_url = normalize_product_url(hit.get("url") or hit.get("slug"))

    if not name or price is None or not source_url:
        return None

    brand = brand_from_hit(hit) or infer_brand(name)
    return Product(
        name=name,
        brand=brand,
        retail_price=price,
        quantity=infer_quantity(json.dumps(hit, default=str)) or DEFAULT_QUANTITY,
        source_url=source_url,
        is_available=not bool(hit.get("out_of_stock")),
    )


def brand_from_hit(hit: dict) -> Optional[str]:
    brand = hit.get("brand")
    if isinstance(brand, dict):
        return clean_text(str(brand.get("brand") or "")) or None
    if isinstance(brand, str):
        return clean_text(brand) or None
    return None


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
        if (
            "application/json" not in script_type
            and "__NEXT_DATA__" not in script.get("id", "")
            and "__next_f" not in script_text
            and "product" not in script_text.lower()
        ):
            continue

        for raw_product in extract_product_dicts(script_text):
            product = product_from_any_dict(raw_product)
            if product is None or product.source_url in seen_urls:
                continue

            seen_urls.add(product.source_url)
            yield product


def extract_product_dicts(script_text: str) -> Iterable[dict]:
    for value in parse_json_values(script_text):
        yield from iter_product_dicts(value)


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


def iter_product_dicts(value) -> Iterable[dict]:
    if isinstance(value, dict):
        if looks_like_product(value):
            yield value

        for nested_value in value.values():
            yield from iter_product_dicts(nested_value)
    elif isinstance(value, list):
        for nested_value in value:
            yield from iter_product_dicts(nested_value)


def looks_like_product(value: dict) -> bool:
    return (
        ("price" in value or "msrp" in value)
        and ("name" in value or "title" in value)
        and ("url" in value or "slug" in value)
    )


def product_from_any_dict(raw_product: dict) -> Optional[Product]:
    if raw_product.get("category_id") not in {None, SWITCH_CATEGORY_ID}:
        return None

    name = clean_text(
        " ".join(
            str(value)
            for value in [
                raw_product.get("name") or raw_product.get("title"),
                raw_product.get("suffix"),
            ]
            if value
        )
    )
    price = parse_price_value(raw_product.get("price"))
    source_url = normalize_product_url(raw_product.get("url") or raw_product.get("slug"))

    if not name or price is None or not source_url:
        return None

    return Product(
        name=name,
        brand=brand_from_hit(raw_product) or infer_brand(name),
        retail_price=price,
        quantity=infer_quantity(json.dumps(raw_product, default=str)) or DEFAULT_QUANTITY,
        source_url=source_url,
        is_available=not bool(raw_product.get("out_of_stock")),
    )


def find_product_cards(soup: BeautifulSoup) -> list:
    cards = soup.select("[class*='product'], article, li, div")
    return [card for card in cards if find_product_link(card) is not None and "$" in card.get_text(" ", strip=True)]


def parse_product_card(card) -> Optional[Product]:
    link = find_product_link(card)
    if link is None:
        return None

    name = extract_name(card, link)
    price = extract_price(card)
    source_url = normalize_product_url(link.get("href"))
    if not name or price is None or not source_url:
        return None

    card_text = card.get_text(" ", strip=True)
    return Product(
        name=name,
        brand=extract_brand(card) or infer_brand(name),
        retail_price=price,
        quantity=infer_quantity(card_text) or DEFAULT_QUANTITY,
        source_url=source_url,
        is_available=not is_sold_out_text(card_text),
    )


def is_sold_out_text(text: str) -> bool:
    return bool(re.search(r"\bsold\s*out\b|\bunavailable\b", text, re.IGNORECASE))


def find_product_link(card):
    links = card.select('a[href^="/products/"], a[href*="milktooth.com/products/"]')
    return links[0] if links else None


def extract_name(card, link) -> str:
    selectors = ["h1", "h2", "h3", "[class*='title']", "[class*='name']"]
    for selector in selectors:
        element = card.select_one(selector)
        if element:
            text = clean_text(element.get_text(" ", strip=True))
            if text and "$" not in text:
                return text

    return clean_text(link.get("title") or link.get_text(" ", strip=True))


def extract_brand(card) -> Optional[str]:
    brand_link = card.select_one('a[href^="/brands/"]')
    if brand_link is not None:
        text = clean_text(brand_link.get_text(" ", strip=True))
        if text:
            return text

    return None


def extract_price(card) -> Optional[Decimal]:
    return first_decimal(parse_prices(card.get_text(" ", strip=True)))


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


def infer_quantity(text: str) -> Optional[int]:
    patterns = [
        r"\b(\d+)\s*switches\s*per\s*order\b",
        r"\b(\d+)\s*(?:set|pack)\b",
        r"\bpack\s*of\s*(\d+)\b",
        r"\b(\d+)\s*(?:switches|pcs|pieces)\b",
        r"\bx\s*(\d+)\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            quantity = int(match.group(1))
            if quantity > 0:
                return quantity

    return DEFAULT_QUANTITY


def infer_brand(name: str) -> str:
    brand_patterns = [
        ("HMX", r"\bhmx\b"),
        ("Bsun", r"\bbsun\b"),
        ("Keygeek", r"\bkeygeek\b"),
        ("Lichicx", r"\blichicx\b"),
        ("Geon", r"\bgeon\b"),
        ("TTC", r"\bttc\b"),
        ("Everglide", r"\beverglide\b"),
        ("Haimu", r"\bhaimu\b"),
        ("Wuque Studio", r"\bwuque\b|\bws\b"),
        ("Outemu", r"\boutemu\b"),
        ("Invyr", r"\binvyr\b"),
        ("Gateron", r"\bgateron\b"),
        ("Cherry", r"\bcherry\b"),
        ("Kailh", r"\bkailh\b"),
        ("JWK", r"\bjwk\b|\bjwick\b"),
        ("Tecsee", r"\btecsee\b"),
        ("KTT", r"\bktt\b"),
        ("SP-Star", r"\bsp[- ]?star\b"),
        ("Aflion", r"\baflion\b"),
        ("Durock", r"\bdurock\b"),
        ("Gazzew", r"\bgazzew\b|\bboba\b|\bu4t?\b"),
    ]

    for brand, pattern in brand_patterns:
        if re.search(pattern, name, re.IGNORECASE):
            return brand

    return DEFAULT_BRAND


def normalize_product_url(value: Optional[str]) -> Optional[str]:
    if not value:
        return None

    text = str(value)
    if text.startswith("http"):
        return text
    if text.startswith("/"):
        return urljoin(BASE_URL, text)
    return urljoin(BASE_URL, f"/products/{text}")


def has_next_page_from_html(html: str, current_page: int) -> bool:
    soup = BeautifulSoup(html, "html.parser")
    for link in soup.select('a[href*="products_table%5Bpage%5D="], a[href*="products_table[page]="]'):
        page = page_number_from_href(link.get("href"))
        if page > current_page:
            return True
    return False


def page_number_from_href(href: Optional[str]) -> int:
    if not href:
        return 0

    page_match = re.search(r"(?:products_table%5Bpage%5D|products_table\[page\])=(\d+)", href)
    return int(page_match.group(1)) if page_match else 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape Milktooth switch prices.")
    parser.add_argument(
        "--delay",
        type=float,
        default=2.0,
        help="Seconds to wait between product-table pages.",
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
