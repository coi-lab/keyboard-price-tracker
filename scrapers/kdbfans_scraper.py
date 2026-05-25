import argparse
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

from core.core_engine import USER_AGENT, clean_text, fetch_html, initialize_database, save_item_data


BASE_URL = "https://kbdfans.com"
COLLECTION_URL = f"{BASE_URL}/collections/switches"
DEFAULT_BRAND = "KBDFans"
VENDOR_NAME = "KBDFans"


@dataclass(frozen=True)
class Product:
    name: str
    brand: str
    retail_price: Decimal
    quantity: int
    source_url: str


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

        if not has_next_page(html, page):
            print(f"No next-page link found after page {page}. Stopping.")
            break

        page += 1
        time.sleep(delay_seconds)

    return saved_count


def build_page_url(page: int) -> str:
    return f"{COLLECTION_URL}?page={page}"


def parse_products(html: str) -> Iterable[Product]:
    soup = BeautifulSoup(html, "html.parser")
    cards = find_product_cards(soup)

    for card in cards:
        product = parse_product_card(card)
        if product is not None:
            yield product


def find_product_cards(soup: BeautifulSoup) -> list:
    product_links = soup.select('a[href*="/collections/switches/products/"]')
    sale_section = soup.find(
        lambda tag: tag.name in {"h2", "h3"}
        and clean_text(tag.get_text(" ", strip=True)).lower() == "on sale"
    )
    sale_line = getattr(sale_section, "sourceline", None)
    cards = []
    seen_urls = set()
    for link in product_links:
        link_line = getattr(link, "sourceline", None)
        if sale_line is not None and link_line is not None and link_line > sale_line:
            continue

        source_url = urljoin(BASE_URL, link.get("href", ""))
        if source_url in seen_urls:
            continue

        card = find_priced_parent(link)
        if card is not None:
            seen_urls.add(source_url)
            cards.append(card)

    return cards


def find_priced_parent(link):
    current = link
    for _ in range(8):
        if current is None:
            return None

        text = current.get_text(" ", strip=True)
        if "$" in text and re.search(r"product|grid|card|block|item", class_text(current), re.IGNORECASE):
            return current

        current = current.parent

    return None


def parse_product_card(card) -> Optional[Product]:
    link = find_product_link(card)
    if link is None:
        return None

    name = extract_name(card, link)
    source_url = urljoin(BASE_URL, link.get("href", ""))
    price = extract_price(card)

    if not name or price is None:
        return None

    return Product(
        name=clean_text(name),
        brand=extract_brand(card) or infer_brand(name),
        retail_price=price,
        quantity=infer_quantity(f"{name} {card.get_text(' ', strip=True)}"),
        source_url=source_url,
    )


def find_product_link(card):
    links = card.select('a[href*="/collections/switches/products/"]')
    return links[0] if links else None


def extract_name(card, link) -> str:
    selectors = [
        ".product-block__title",
        ".product-title",
        ".product-card__title",
        ".grid-product__title",
        "[data-product-title]",
        "h2",
        "h3",
    ]
    for selector in selectors:
        element = card.select_one(selector)
        if element:
            text = element.get_text(" ", strip=True)
            if text:
                return text

    return link.get("title") or link.get_text(" ", strip=True)


def extract_brand(card) -> Optional[str]:
    selectors = [
        ".vendor",
        ".product-vendor",
        ".product-block__vendor",
        "[data-product-vendor]",
    ]
    for selector in selectors:
        element = card.select_one(selector)
        if element:
            text = clean_text(element.get_text(" ", strip=True))
            if text:
                return text

    return None


def infer_brand(name: str) -> str:
    normalized = name.lower()
    brand_patterns = [
        ("Cherry", r"\bcherry\b"),
        ("Gateron", r"\bgateron\b|\bgateron\b"),
        ("GEONWORKS", r"\bgeon\b"),
        ("HMX", r"\bhmx\b"),
        ("Siliworks", r"\bsiliworks\b|\bsillyworks\b"),
        ("KBDfans", r"\bkbdfans\b"),
        ("AGS", r"\bags\b"),
        ("UR ICE", r"\bur ice\b"),
        ("Mount Tai", r"\bmount tai\b"),
    ]

    for brand, pattern in brand_patterns:
        if re.search(pattern, normalized, re.IGNORECASE):
            return brand

    return DEFAULT_BRAND


def extract_price(card) -> Optional[Decimal]:
    selectors = [
        "[data-product-price]",
        ".theme-money",
        ".price",
        ".product-price",
        ".product-block__price",
        ".grid-product__price",
    ]
    prices = []
    for selector in selectors:
        for element in card.select(selector):
            prices.extend(parse_prices(element.get_text(" ", strip=True)))

    if not prices:
        prices = parse_prices(card.get_text(" ", strip=True))

    return min(prices) if prices else None


def parse_price(text: str) -> Optional[Decimal]:
    prices = parse_prices(text)
    return prices[0] if prices else None


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
        r"\bx\s*(\d+)\b",
        r"\((\d+)\)",
        r"\b(\d+)\s*(?:pcs|pieces|switches)\b",
        r"\bpack\s*of\s*(\d+)\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            quantity = int(match.group(1))
            if quantity > 0:
                return quantity

    return 1


def has_next_page(html: str, current_page: int) -> bool:
    soup = BeautifulSoup(html, "html.parser")
    next_link = soup.select_one('a[rel="next"], a.pagination__next, a[href*="page="]')

    if next_link and next_link.get("href"):
        next_page_match = re.search(r"[?&]page=(\d+)", next_link["href"])
        if next_page_match:
            return int(next_page_match.group(1)) > current_page

    return bool(soup.select_one(f'a[href*="page={current_page + 1}"]'))


def class_text(tag) -> str:
    classes = tag.get("class") or []
    return " ".join(classes)


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape KBDFans switch prices.")
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
