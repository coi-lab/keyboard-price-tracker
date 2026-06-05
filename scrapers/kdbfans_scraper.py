import argparse
import json
import re
import sys
import time
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Iterable, Optional
from urllib.parse import urljoin, urlsplit, urlunsplit

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
MIN_REASONABLE_UNIT_PRICE = Decimal("0.15")
MAX_REASONABLE_UNIT_PRICE = Decimal("1.50")


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
            product = ensure_reasonable_unit_price(product, session)
            if product is None:
                continue

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
    source_url = normalize_product_url(urljoin(BASE_URL, link.get("href", "")))
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


def ensure_reasonable_unit_price(product: Product, session: requests.Session) -> Optional[Product]:
    unit_price = calculate_unit_price(f"{product.name} {product.quantity}pcs", product.retail_price)
    if is_reasonable_unit_price(unit_price):
        return product

    enriched_product = enrich_quantity_from_product_page(product, session)
    enriched_unit_price = calculate_unit_price(
        f"{enriched_product.name} {enriched_product.quantity}pcs",
        enriched_product.retail_price,
    )
    if is_reasonable_unit_price(enriched_unit_price):
        return enriched_product

    print(
        "Skipping implausible KBDFans price: "
        f"{product.name} - ${product.retail_price} / {enriched_product.quantity} "
        f"(${enriched_unit_price:.2f}/ea)"
    )
    return None


def calculate_unit_price(name: str, raw_price: Decimal) -> Decimal:
    quantity = infer_quantity(name)
    return raw_price / Decimal(quantity)


def is_reasonable_unit_price(unit_price: Decimal) -> bool:
    return MIN_REASONABLE_UNIT_PRICE <= unit_price <= MAX_REASONABLE_UNIT_PRICE


def enrich_quantity_from_product_page(product: Product, session: requests.Session) -> Product:
    try:
        html = fetch_html(product.source_url, session)
    except RuntimeError as error:
        print(f"Could not fetch KBDFans product page for quantity check: {product.source_url}: {error}")
        return product

    quantity = choose_quantity_for_price(
        product.retail_price,
        [product.quantity, *infer_quantities_from_product_page(html)],
    )
    return Product(
        name=product.name,
        brand=product.brand,
        retail_price=product.retail_price,
        quantity=quantity,
        source_url=product.source_url,
    )


def choose_quantity_for_price(raw_price: Decimal, quantities: list[int]) -> int:
    unique_quantities = sorted({quantity for quantity in quantities if quantity > 0})
    for quantity in unique_quantities:
        if is_reasonable_unit_price(raw_price / Decimal(quantity)):
            return quantity
    return max(unique_quantities) if unique_quantities else 1


def infer_quantities_from_product_page(html: str) -> list[int]:
    soup = BeautifulSoup(html, "html.parser")
    candidates = []

    for selector in [
        "option",
        "button",
        "label",
        "[data-value]",
        "[data-option-value]",
        "[data-variant-title]",
        ".product-form__input",
        ".variant-input",
    ]:
        for element in soup.select(selector):
            text_values = [element.get_text(" ", strip=True)]
            for attr in ["value", "title", "aria-label", "data-value", "data-option-value", "data-variant-title"]:
                attr_value = element.get(attr)
                if attr_value:
                    text_values.append(str(attr_value))
            candidates.extend(text_values)

    for script in soup.find_all("script"):
        script_text = script.string or script.get_text()
        if script_text and ("variant" in script_text.lower() or "pack" in script_text.lower()):
            candidates.extend(extract_variant_texts(script_text))

    return [infer_quantity(candidate) for candidate in candidates if infer_quantity(candidate) > 1]


def extract_variant_texts(script_text: str) -> list[str]:
    texts = []
    for value in parse_json_values(script_text):
        collect_variant_texts(value, texts)
    return texts


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


def collect_variant_texts(value, texts: list[str]) -> None:
    if isinstance(value, dict):
        for key, nested_value in value.items():
            if str(key).lower() in {"title", "name", "option1", "option2", "option3", "public_title"}:
                texts.append(str(nested_value))
            collect_variant_texts(nested_value, texts)
    elif isinstance(value, list):
        for nested_value in value:
            collect_variant_texts(nested_value, texts)


def find_product_link(card):
    links = card.select('a[href*="/collections/switches/products/"]')
    for link in links:
        candidate_name = link.get("title") or link.get_text(" ", strip=True)
        if not is_pack_variant_label(candidate_name):
            return link

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
            if text and not is_pack_variant_label(text):
                return text

    for attr in ("title", "aria-label"):
        text = link.get(attr)
        if text and not is_pack_variant_label(text):
            return text

    text = link.get_text(" ", strip=True)
    return "" if is_pack_variant_label(text) else text


def is_pack_variant_label(text: Optional[str]) -> bool:
    if not text:
        return False

    normalized = clean_text(text).lower()
    normalized = re.sub(r"\s+", " ", normalized).strip()
    if not normalized:
        return False

    return bool(
        re.fullmatch(r".*\bswitch(?:es)?\s*x\s*\d+", normalized)
        or re.fullmatch(r"(?:switch(?:es)?\s*)?x\s*\d+", normalized)
        or re.fullmatch(r"\d+\s*(?:switch(?:es)?|pcs|pieces)", normalized)
        or re.fullmatch(r"pack\s*of\s*\d+", normalized)
    )


def normalize_product_url(url: str) -> str:
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path.rstrip("/"), "", ""))


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
        r"\b(\d+)\s*-\s*pack\b",
        r"\b(\d+)\s*x\b",
        r"\bx\s*(\d+)\b",
        r"\((\d+)\)",
        r"\b(\d+)\s*(?:pcs?|pieces|switches)\b",
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
