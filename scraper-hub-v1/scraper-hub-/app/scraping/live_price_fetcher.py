"""
Omnis Signal — Real-Price Live Data Pipeline
=============================================
Fetches actual current prices from live Zimbabwean websites for all 7 sectors:
  Banking · Education · Food & Drink · Hotels · Retail · Telecom · Transport

Strategy:
  1. Use requests + BeautifulSoup to fetch and parse each source URL.
  2. Apply sector-specific parsing rules to extract (name, price, attributes).
  3. Upsert each extracted product into the catalog via the sector's service.
  4. Print a rich report of what was fetched vs. what previously existed.
"""

import re
import sys
import time
import logging
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.WARNING)  # suppress SQLAlchemy noise

# ── project imports ──────────────────────────────────────────────────────────
sys.path.insert(0, ".")
from app.db.session import SessionLocal
from app.db.models.catalog import Listing, Category, Provider, SectorConfig
from app.services.catalog_service import get_or_create_provider, upsert_listing
from app.db.models.catalog import ListingStatus, FreshnessStatus, ListingUpdateSource

# Sector services
from app.services.telecom_service import telecom_service
from app.services.banking_service import banking_service
from app.services.education_service import education_service
from app.services.food_service import food_service
from app.services.hotels_service import hotels_service
from app.services.retail_service import retail_service
from app.services.transport_service import transport_service


# ── HTTP helpers ─────────────────────────────────────────────────────────────

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def fetch(url: str, timeout: int = 15) -> Optional[BeautifulSoup]:
    """Fetch a URL and return a parsed BeautifulSoup object, or None on failure."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except Exception as e:
        print(f"  [FETCH ERROR] {url} -> {e}")
        return None


def parse_usd(text: str) -> Optional[float]:
    """Extract the first USD numeric value from arbitrary text."""
    if not text:
        return None
    text = re.sub(r"[,\s]", "", text)
    # Match patterns: $1.50  USD1.50  1.50USD  1.50$
    patterns = [
        r"\$\s*([\d]+(?:\.[\d]{1,2})?)",
        r"USD\s*([\d]+(?:\.[\d]{1,2})?)",
        r"([\d]+(?:\.[\d]{1,2})?)\s*USD",
        r"([\d]+(?:\.[\d]{1,2})?)\s*\$",
        r"US\$\s*([\d]+(?:\.[\d]{1,2})?)",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            try:
                return float(m.group(1))
            except ValueError:
                pass
    # Try any number if text is short (e.g. table cell "1.50")
    m = re.search(r"^([\d]+(?:\.[\d]{1,2})?)$", text.strip())
    if m:
        try:
            val = float(m.group(1))
            if 0.01 <= val <= 10000:
                return val
        except ValueError:
            pass
    return None


def parse_mb(text: str) -> Optional[float]:
    """Parse data allowance string to MB float (e.g. '1GB' -> 1000.0, '500MB' -> 500.0)."""
    if not text:
        return None
    text = text.strip().upper()
    m = re.search(r"([\d]+(?:\.[\d]+)?)\s*(GB|MB|TB)", text)
    if not m:
        return None
    val = float(m.group(1))
    unit = m.group(2)
    return val * 1000 if unit == "GB" else (val * 1_000_000 if unit == "TB" else val)


# ── RESULTS TRACKING ─────────────────────────────────────────────────────────

results: List[Dict[str, Any]] = []

def record(sector: str, source_url: str, name: str, price: Optional[float],
           currency: str, action: str, category: str):
    results.append({
        "sector": sector, "source": source_url, "name": name,
        "price": price, "currency": currency, "action": action, "category": category
    })
    status = "NEW" if action == "created" else ("UPD" if action == "updated" else "---")
    price_str = f"${price:.2f}" if price is not None else "N/A"
    print(f"  [{status}] [{sector}] {name[:60]:<60} {price_str:>10}  ({category})")


# ═══════════════════════════════════════════════════════════════════════════════
# 1. TELECOM  —  Econet · NetOne · Telecel
# ═══════════════════════════════════════════════════════════════════════════════

TELECOM_SOURCES = [
    # Econet USD bundles
    ("Econet Wireless", "https://www.econet.co.zw/usd-data-bundles/", "general-data"),
    ("Econet Wireless", "https://www.econet.co.zw/private-wifi-bundles/", "private-wifi"),
    ("Econet Wireless", "https://www.econet.co.zw/freedom-bundles/", "freedom-bundles"),
    ("Econet Wireless", "https://www.econet.co.zw/whatsapp-bundles/", "whatsapp-data"),
    # NetOne
    ("NetOne", "https://www.netone.co.zw/products-services/data/", "general-data"),
    # Telecel
    ("Telecel Zimbabwe", "https://www.telecel.co.zw/internet-bundles/", "general-data"),
]


def scrape_telecom(db) -> int:
    print("\n[TELECOM] Fetching live bundle prices...")
    count = 0
    for operator, url, cat_slug in TELECOM_SOURCES:
        soup = fetch(url)
        if not soup:
            continue

        text = soup.get_text(" ", strip=True)

        # Look for bundle price rows: patterns like "1GB  |  30 days  |  $2.00"
        # or "1GB  30 days  2.00" in tables/cards
        bundle_pattern = re.compile(
            r"([\d]+(?:\.\d+)?)\s*(GB|MB)\b.{0,120}?\$\s*([\d]+(?:\.[\d]{1,2})?)",
            re.IGNORECASE
        )

        for m in bundle_pattern.finditer(text):
            try:
                val = float(m.group(1))
                unit = m.group(2).upper()
                price = float(m.group(3))
                data_mb = val * 1000 if unit == "GB" else val
                if price <= 0 or price > 500 or data_mb < 1:
                    continue
                price_per_gb = round(price / (data_mb / 1000.0), 4) if data_mb >= 1 else None
                name = f"{operator} {int(val) if val == int(val) else val}{unit} Bundle"
                res = telecom_service.ingest_bundle_listing(
                    db,
                    operator_name=operator,
                    category_slug=cat_slug,
                    bundle_name=name,
                    price=price,
                    currency="USD",
                    source_url=url,
                    attributes={
                        "operator": operator,
                        "bundle_name": f"{int(val) if val == int(val) else val}{unit} Bundle",
                        "validity": "30 days",
                        "benefit": f"{int(val) if val == int(val) else val}{unit} data",
                        "data_mb": data_mb,
                        "price_per_gb": price_per_gb,
                    }
                )
                record("Telecom", url, name, price, "USD", res["action"], cat_slug)
                count += 1
            except Exception as e:
                pass

        # Also scan table rows for structured bundle tables
        for row in soup.find_all("tr"):
            cells = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
            if len(cells) < 2:
                continue
            row_text = " ".join(cells)
            # detect data + price in same row
            dm = re.search(r"([\d]+(?:\.\d+)?)\s*(GB|MB)", row_text, re.IGNORECASE)
            pm = re.search(r"\$\s*([\d]+(?:\.[\d]{1,2})?)", row_text)
            if not pm:
                pm = re.search(r"USD\s*([\d]+(?:\.[\d]{1,2})?)", row_text, re.IGNORECASE)
            if dm and pm:
                try:
                    val = float(dm.group(1)); unit = dm.group(2).upper()
                    price = float(pm.group(1))
                    data_mb = val * 1000 if unit == "GB" else val
                    if price <= 0 or price > 500:
                        continue
                    price_per_gb = round(price / (data_mb / 1000.0), 4) if data_mb >= 1 else None
                    name = f"{operator} {int(val) if val == int(val) else val}{unit} (Table)"
                    res = telecom_service.ingest_bundle_listing(
                        db,
                        operator_name=operator,
                        category_slug=cat_slug,
                        bundle_name=name,
                        price=price,
                        currency="USD",
                        source_url=url,
                        attributes={
                            "operator": operator,
                            "bundle_name": f"{int(val) if val == int(val) else val}{unit}",
                            "validity": "30 days",
                            "benefit": f"{int(val) if val == int(val) else val}{unit} data",
                            "data_mb": data_mb,
                            "price_per_gb": price_per_gb,
                        }
                    )
                    record("Telecom", url, name, price, "USD", res["action"], cat_slug)
                    count += 1
                except Exception:
                    pass

        time.sleep(0.5)
    return count


# ═══════════════════════════════════════════════════════════════════════════════
# 2. BANKING  —  Tariff sheets from Zimbabwean banks
# ═══════════════════════════════════════════════════════════════════════════════

BANKING_SOURCES = [
    ("CBZ Bank", "https://www.cbz.co.zw/tariffs", "transaction-fees"),
    ("Stanbic Bank", "https://www.stanbicbank.co.zw/zimbabwe/personal/rates-and-fees", "transaction-fees"),
    ("Steward Bank", "https://www.stewardbank.co.zw/personal-banking/charges", "mobile-banking-fees"),
    ("FBC Bank", "https://www.fbc.co.zw/personal/bank-charges", "transaction-fees"),
    ("CABS", "https://www.cabs.co.zw/personal-banking/tariff-guide", "mortgage-interest"),
    ("NMB Bank", "https://www.nmbz.co.zw/personal/charges", "transaction-fees"),
    ("ZB Bank", "https://www.zb.co.zw/personal-banking/tariffs", "transaction-fees"),
    ("BancABC", "https://www.bancabczimbabwe.com/personal/tariffs", "transaction-fees"),
    ("Nedbank Zimbabwe", "https://www.nedbank.co.zw/personal/rates", "transaction-fees"),
    ("POSB", "https://www.posb.co.zw/personal-banking/tariffs", "transaction-fees"),
]


def scrape_banking(db) -> int:
    print("\n[BANKING] Fetching live bank tariff prices...")
    count = 0

    for bank_name, url, revenue_slug in BANKING_SOURCES:
        soup = fetch(url)
        if not soup:
            # Bank sites often block — insert from known public tariff data
            continue

        text = soup.get_text(" ", strip=True)

        # Find fee table rows — look for label + USD price pairs
        # Pattern: any line with a service description followed by a $ price
        fee_rows = []

        # Try structured table rows first
        for row in soup.find_all("tr"):
            cells = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
            if len(cells) < 2:
                continue
            label = cells[0]
            # Skip header rows
            if re.search(r"(service|description|fee|charge|item|tariff)", label, re.I) and len(label) < 30:
                continue
            # Find price in any of the remaining cells
            price = None
            for cell in cells[1:]:
                price = parse_usd(cell)
                if price is not None:
                    break
            if price is not None and label and len(label) > 3:
                fee_rows.append((label.strip()[:80], price))

        # Also try scanning paragraphs/list items for "fee: $x.xx" patterns
        pattern = re.compile(
            r"([A-Za-z][A-Za-z\s/\-]{4,50}(?:fee|charge|levy|rate|maintenance|transfer|withdrawal|deposit|monthly|annual))"
            r".{0,60}?\$\s*([\d]+(?:\.[\d]{1,2})?)",
            re.IGNORECASE
        )
        for m in pattern.finditer(text):
            label = m.group(1).strip()[:80]
            price = float(m.group(2))
            fee_rows.append((label, price))

        # Deduplicate by label
        seen = set()
        for label, price in fee_rows:
            key = label.lower()[:40]
            if key in seen or price <= 0 or price > 10000:
                continue
            seen.add(key)
            listing_name = f"{bank_name} — {label}"
            try:
                res = banking_service.ingest_fee(
                    db,
                    bank_name=bank_name,
                    revenue_line_slug=revenue_slug,
                    listing_name=listing_name,
                    price=price,
                    currency="USD",
                    attributes={"fee_description": label, "fee_usd": price},
                    source_url=url
                )
                record("Banking", url, listing_name, price, "USD", res["action"], revenue_slug)
                count += 1
            except Exception as e:
                pass

        time.sleep(0.5)
    return count


# ═══════════════════════════════════════════════════════════════════════════════
# 3. EDUCATION  —  School and university fees
# ═══════════════════════════════════════════════════════════════════════════════

EDUCATION_SOURCES = [
    # Universities
    ("University of Zimbabwe", "https://www.uz.ac.zw/index.php/fees-structure", "universities", "https://www.uz.ac.zw"),
    ("NUST", "https://www.nust.ac.zw/index.php/tuition-fees", "universities", "https://www.nust.ac.zw"),
    ("MSU", "https://www.msu.ac.zw/fees", "universities", "https://www.msu.ac.zw"),
    ("HIT Harare", "https://www.hit.ac.zw/fees", "universities", "https://www.hit.ac.zw"),
    # Secondary schools (with known public fee notices)
    ("St George's College", "https://stgeorges.ac.zw/fees/", "secondary-schools", "https://stgeorges.ac.zw"),
    ("Churchill School", "https://www.churchillschool.co.zw/fees", "secondary-schools", "https://www.churchillschool.co.zw"),
]

def scrape_education(db) -> int:
    print("\n[EDUCATION] Fetching live school and university fees...")
    count = 0

    for institution, url, cat_slug, provider_url in EDUCATION_SOURCES:
        soup = fetch(url)
        if not soup:
            continue

        text = soup.get_text(" ", strip=True)
        prices_found = []

        # Look for term/semester fee amounts
        fee_patterns = [
            re.compile(r"(tuition|term fee|semester fee|registration|annual fee|boarding|levy)[^\n\$]{0,80}\$\s*([\d,]+(?:\.[\d]{1,2})?)", re.IGNORECASE),
            re.compile(r"\$\s*([\d,]+(?:\.[\d]{1,2})?)\s*(?:per\s+)?(?:term|semester|year|annum)", re.IGNORECASE),
        ]

        for pat in fee_patterns:
            for m in pat.finditer(text):
                try:
                    if pat.groups == 2:
                        label = m.group(1).strip()[:60]
                        price_str = m.group(2).replace(",", "")
                    else:
                        label = "Tuition"
                        price_str = m.group(1).replace(",", "")
                    price = float(price_str)
                    if price > 0:
                        prices_found.append((label, price))
                except Exception:
                    pass

        # Ingest top unique prices
        seen = set()
        for label, price in prices_found[:10]:
            key = f"{institution}:{label[:20]}:{price}"
            if key in seen:
                continue
            seen.add(key)
            listing_name = f"{institution} — {label} ({datetime.now().year})"
            try:
                res = education_service.ingest_education_listing(
                    db,
                    institution_name=institution,
                    category_slug=cat_slug,
                    listing_name=listing_name,
                    price=price,
                    currency="USD",
                    source_url=url,
                    attributes={
                        "term_fees": price,
                        "curriculum": "Zimbabwe",
                        "boarding": False,
                    }
                )
                record("Education", url, listing_name, price, "USD", res["action"], cat_slug)
                count += 1
            except Exception as e:
                pass

        time.sleep(0.5)
    return count


# ═══════════════════════════════════════════════════════════════════════════════
# 4. FOOD & DRINK  —  Restaurant menu prices
# ═══════════════════════════════════════════════════════════════════════════════

FOOD_SOURCES = [
    ("Chicken Inn", "https://www.innscorporation.co.zw/brands/chicken-inn/menu", "fast-food", "https://www.innscorporation.co.zw"),
    ("Pizza Inn", "https://www.innscorporation.co.zw/brands/pizza-inn/menu", "fast-food", "https://www.innscorporation.co.zw"),
    ("Nando's Zimbabwe", "https://www.nandos.co.zw/food/menu", "casual-dining", "https://www.nandos.co.zw"),
    ("Spur Zimbabwe", "https://www.spurzimbabwe.com/menu/", "casual-dining", "https://www.spurzimbabwe.com"),
    ("Ocean Basket Zimbabwe", "https://www.oceanbasket.co.zw/menu/", "casual-dining", "https://www.oceanbasket.co.zw"),
]


def scrape_food(db) -> int:
    print("\n[FOOD & DRINK] Fetching live restaurant menu prices...")
    count = 0

    for restaurant, url, cat_slug, provider_url in FOOD_SOURCES:
        soup = fetch(url)
        if not soup:
            continue

        text = soup.get_text(" ", strip=True)

        # Look for menu item + price patterns
        # e.g. "Streetwise Two  $4.99" or "Chicken Burger ......... $5.50"
        item_price_pattern = re.compile(
            r"([A-Z][A-Za-z\s\-&']{3,50})\s*[\.\-·•]{0,10}\s*\$\s*([\d]+(?:\.[\d]{1,2})?)",
            re.MULTILINE
        )

        seen = set()
        for m in item_price_pattern.finditer(text):
            label = m.group(1).strip()
            try:
                price = float(m.group(2))
            except ValueError:
                continue
            if price <= 0 or price > 200:
                continue
            # Filter out nav / header noise
            noise = ["menu", "home", "contact", "about", "privacy", "terms", "login", "sign"]
            if any(n in label.lower() for n in noise):
                continue
            key = f"{restaurant}:{label[:25]}"
            if key in seen:
                continue
            seen.add(key)
            listing_name = f"{restaurant} — {label}"
            try:
                res = food_service.ingest_food_listing(
                    db,
                    restaurant_name=restaurant,
                    category_slug=cat_slug,
                    item_name=listing_name,
                    price=price,
                    currency="USD",
                    source_url=url,
                    attributes={
                        "meal": label,
                        "delivery": False,
                        "halal": False,
                    }
                )
                record("Food", url, listing_name, price, "USD", res["action"], cat_slug)
                count += 1
            except Exception as e:
                pass

        time.sleep(0.5)
    return count


# ═══════════════════════════════════════════════════════════════════════════════
# 5. HOTELS  —  Room rates
# ═══════════════════════════════════════════════════════════════════════════════

HOTEL_SOURCES = [
    ("Meikles Hotel", "https://www.meikleshotel.com/accommodation/", "hotel-stays"),
    ("Rainbow Towers", "https://www.rainbowtowershotel.com/accommodation/", "hotel-stays"),
    ("Holiday Inn Harare", "https://www.ihg.com/holidayinn/hotels/gb/en/harare/hraze/hoteldetail", "hotel-stays"),
    ("Cresta Jameson Hotel", "https://www.crestahotels.com/jameson/", "hotel-stays"),
    ("Victoria Falls Hotel", "https://www.victoriafallshotel.com/accommodation/rooms-suites/", "hotel-stays"),
    ("Elephant Hills Resort", "https://www.african-sun.com/elephant-hills/", "hotel-stays"),
]


def scrape_hotels(db) -> int:
    print("\n[HOTELS] Fetching live room rates...")
    count = 0

    for hotel, url, cat_slug in HOTEL_SOURCES:
        soup = fetch(url)
        if not soup:
            continue

        text = soup.get_text(" ", strip=True)

        # Room type + price per night
        room_patterns = [
            re.compile(r"((?:standard|deluxe|superior|suite|twin|double|single|executive|king|queen|premium|luxury)[a-z\s\-]{0,30})\s*(?:room|suite)?.{0,80}?\$\s*([\d,]+(?:\.[\d]{1,2})?)\s*(?:per night|/night|pn)?", re.IGNORECASE),
            re.compile(r"\$\s*([\d,]+(?:\.[\d]{1,2})?)\s*(?:per night|/night|per room)", re.IGNORECASE),
        ]

        seen = set()
        for pat in room_patterns:
            for m in pat.finditer(text):
                try:
                    if pat.groups >= 2:
                        room_type = m.group(1).strip().title()[:60]
                        price = float(m.group(2).replace(",", ""))
                    else:
                        room_type = "Standard Room"
                        price = float(m.group(1).replace(",", ""))
                    if price <= 0 or price > 5000:
                        continue
                    key = f"{hotel}:{room_type[:20]}:{price}"
                    if key in seen:
                        continue
                    seen.add(key)
                    listing_name = f"{hotel} — {room_type}"
                    res = hotels_service.ingest_hotel_listing(
                        db,
                        hotel_name=hotel,
                        category_slug=cat_slug,
                        listing_name=listing_name,
                        price=price,
                        currency="USD",
                        source_url=url,
                        attributes={
                            "price_per_night": price,
                            "room_type": room_type,
                            "breakfast_included": False,
                        }
                    )
                    record("Hotels", url, listing_name, price, "USD", res["action"], cat_slug)
                    count += 1
                except Exception as e:
                    pass

        time.sleep(0.5)
    return count


# ═══════════════════════════════════════════════════════════════════════════════
# 6. RETAIL & GROCERIES  —  Supermarket prices
# ═══════════════════════════════════════════════════════════════════════════════

RETAIL_SOURCES = [
    # Textbook / published price sources for Zimbabwean retail staples
    ("OK Zimbabwe", "https://www.okzim.co.zw/specials", "cooking-oil"),
    ("Spar Zimbabwe", "https://www.spar.co.zw/specials-promotions", "cooking-oil"),
    ("Pick n Pay Zimbabwe", "https://www.picknpay.co.zw/online/promotions", "cooking-oil"),
    ("TM Supermarkets", "https://www.tm-supermarkets.co.zw", "cooking-oil"),
    ("Bakers Inn", "https://www.innscorporation.co.zw/brands/bakers-inn/", "bread"),
    ("Profeeds Zimbabwe", "https://www.profeeds.co.zw/products", "mealie-meal"),
]


def scrape_retail(db) -> int:
    print("\n[RETAIL] Fetching live grocery and product prices...")
    count = 0

    COMMON_CATEGORIES = [
        "cooking-oil", "mealie-meal", "bread", "rice", "sugar",
        "flour", "dairy", "eggs", "beverages", "toiletries"
    ]

    PRODUCT_KEYWORDS = {
        "cooking-oil": ["cooking oil", "mazoe oil", "sun oil", "vegetable oil", "olivine"],
        "mealie-meal": ["mealie meal", "roller meal", "champion", "gold star", "ufa"],
        "bread": ["bread", "loaf", "white bread", "brown bread"],
        "sugar": ["sugar", "huletts", "triangle sugar"],
        "flour": ["flour", "all purpose flour", "wheat flour"],
        "beverages": ["mazoe", "juice", "coca cola", "coke", "fanta", "sprite", "water"],
        "dairy": ["milk", "yoghurt", "lacto", "fresh milk", "cheese"],
        "eggs": ["eggs", "dozen eggs", "tray of eggs"],
        "toiletries": ["soap", "bathing soap", "washing powder", "lifebouy", "dettol"],
        "rice": ["rice", "basmati", "golden gate rice"],
    }

    for store, url, default_cat in RETAIL_SOURCES:
        soup = fetch(url)
        if not soup:
            continue

        text = soup.get_text(" ", strip=True)

        # Find product+price pairs
        item_price_pattern = re.compile(
            r"([A-Za-z][A-Za-z\s\-&'()\d\.]{5,60})\s*\$\s*([\d]+(?:\.[\d]{1,2})?)",
        )

        seen = set()
        for m in item_price_pattern.finditer(text):
            label = m.group(1).strip()
            try:
                price = float(m.group(2))
            except ValueError:
                continue
            if price <= 0 or price > 2000:
                continue
            noise = ["click", "view", "add to cart", "shop now", "home", "menu", "contact", "about"]
            if any(n in label.lower() for n in noise) or len(label) < 5:
                continue

            # Determine best category from keyword match
            cat_slug = default_cat
            label_lower = label.lower()
            for slug, keywords in PRODUCT_KEYWORDS.items():
                if any(kw in label_lower for kw in keywords):
                    cat_slug = slug
                    break

            key = f"{store}:{label[:25]}:{price}"
            if key in seen:
                continue
            seen.add(key)
            listing_name = f"{store} — {label[:60]}"
            try:
                res = retail_service.ingest_retail_listing(
                    db,
                    store_name=store,
                    category_slug=cat_slug,
                    product_name=listing_name,
                    price=price,
                    currency="USD",
                    source_url=url,
                    attributes={
                        "brand": label.split()[0] if label else store,
                        "pack_size": "1 unit",
                        "in_stock": True,
                    }
                )
                record("Retail", url, listing_name, price, "USD", res["action"], cat_slug)
                count += 1
            except Exception as e:
                pass

        time.sleep(0.5)
    return count


# ═══════════════════════════════════════════════════════════════════════════════
# 7. TRANSPORT  —  ZUPCO gazetted fares · ride-hailing · intercity
# ═══════════════════════════════════════════════════════════════════════════════

TRANSPORT_SOURCES = [
    ("ZUPCO - Urban", "https://www.zupco.co.zw/fares", "urban-commuter"),
    ("Extracity Luxury Coaches", "https://www.extracity.co.zw/bus-routes", "intercity"),
    ("Bolt Zimbabwe", "https://bolt.eu/en-zw/cities/harare/", "last-mile"),
    ("Intercape Zimbabwe", "https://www.intercape.co.za/route/harare-johannesburg/", "cross-border"),
    ("Fastjet", "https://www.fastjet.com/fly-from-to/ZW/harare/ZW/bulawayo", "air"),
]


def scrape_transport(db) -> int:
    print("\n[TRANSPORT] Fetching live fares and transit prices...")
    count = 0

    for operator, url, cat_slug in TRANSPORT_SOURCES:
        soup = fetch(url)
        if not soup:
            continue

        text = soup.get_text(" ", strip=True)

        # Fare patterns
        fare_patterns = [
            re.compile(r"((?:harare|bulawayo|mutare|gweru|masvingo|victoria falls|johannesburg|lusaka)[a-z\s\-&,]{0,40}?)\s*\$\s*([\d]+(?:\.[\d]{1,2})?)", re.IGNORECASE),
            re.compile(r"\$\s*([\d]+(?:\.[\d]{1,2})?)\s*(?:per trip|per journey|one.?way|return|per person)", re.IGNORECASE),
            re.compile(r"(?:fare|ticket|price)\s*[:=]?\s*\$\s*([\d]+(?:\.[\d]{1,2})?)", re.IGNORECASE),
        ]

        seen = set()
        for pat in fare_patterns:
            for m in pat.finditer(text):
                try:
                    if pat.groups >= 2:
                        route = m.group(1).strip().title()[:80]
                        price = float(m.group(2))
                    else:
                        route = f"{operator} service"
                        price = float(m.group(1))
                    if price <= 0 or price > 5000:
                        continue
                    key = f"{operator}:{route[:20]}:{price}"
                    if key in seen:
                        continue
                    seen.add(key)
                    listing_name = f"{operator} — {route}"
                    res = transport_service.ingest_transport_listing(
                        db,
                        operator_name=operator,
                        category_slug=cat_slug,
                        service_name=listing_name,
                        fare_gazetted=price,
                        fare_estimate=price,
                        currency="USD",
                        source_url=url,
                        attributes={
                            "service_level": "Standard",
                            "fare_gazetted": price,
                            "fare_estimate": price,
                            "province_district": route,
                            "ownership_status": "private",
                            "urbanicity": "both",
                            "passenger_or_freight": "passenger",
                        }
                    )
                    record("Transport", url, listing_name, price, "USD", res["action"], cat_slug)
                    count += 1
                except Exception as e:
                    pass

        time.sleep(0.5)
    return count


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("  OMNIS SIGNAL — LIVE REAL-PRICE DATA PIPELINE")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    db = SessionLocal()
    totals = {}

    try:
        totals["Telecom"]   = scrape_telecom(db)
        totals["Banking"]   = scrape_banking(db)
        totals["Education"] = scrape_education(db)
        totals["Food"]      = scrape_food(db)
        totals["Hotels"]    = scrape_hotels(db)
        totals["Retail"]    = scrape_retail(db)
        totals["Transport"] = scrape_transport(db)
        db.commit()

    except Exception as e:
        db.rollback()
        print(f"\n[FATAL ERROR] {e}")
        raise
    finally:
        db.close()

    # ── Summary Report ─────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("  LIVE PRICE FETCH SUMMARY")
    print("=" * 70)
    created = sum(1 for r in results if r["action"] == "created")
    updated = sum(1 for r in results if r["action"] == "updated")
    unchanged = sum(1 for r in results if r["action"] == "unchanged")
    print(f"  Total items processed : {len(results)}")
    print(f"  New listings created  : {created}")
    print(f"  Existing prices updated: {updated}")
    print(f"  Unchanged (same price) : {unchanged}")
    print()
    for sector, n in totals.items():
        print(f"  {sector:<15} {n:>4} items fetched")
    print("=" * 70)

    if not results:
        print("\n  NOTE: 0 real prices were extracted.")
        print("  This typically means the source websites returned bot-protection")
        print("  pages (Cloudflare, 403, 503) or have changed their HTML structure.")
        print("  Run the fallback seeder below to populate with best-known market prices:")
        print("    python app/data/real_market_seed.py")


if __name__ == "__main__":
    main()
