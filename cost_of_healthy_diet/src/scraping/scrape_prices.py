import os
import time
import random
import csv
from datetime import datetime

import requests
from bs4 import BeautifulSoup
import pandas as pd


BASE_URL = "https://www.walmart.com/search"


def load_basket_items(path):
    return pd.read_csv(path)


def fetch_page(query):
    params = {"q": query}
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    r = requests.get(BASE_URL, params=params, headers=headers, timeout=10)
    r.raise_for_status()
    return r.text

def debug_save_html(html: str, query: str):
    safe_query = query.replace(" ", "_").replace("/", "_")
    out_path = f"debug_{safe_query}.html"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Saved debug HTML for '{query}' to {out_path}")


def parse_walmart_product(html):
    soup = BeautifulSoup(html, "html.parser")

    # Updated product card selector
    card = soup.select_one("div[data-automation-id='search-product']")
    if not card:
        return None

    # Product name
    title_el = card.select_one("span[data-automation-id='product-title']")
    title = title_el.get_text(strip=True) if title_el else None

    # Brand
    brand_el = card.select_one("span[data-automation-id='product-brand']")
    brand = brand_el.get_text(strip=True) if brand_el else None

    # Price
    whole_el = card.select_one("span[data-automation-id='price-characteristic']")
    frac_el = card.select_one("span[data-automation-id='price-mantissa']")

    if whole_el:
        try:
            whole = whole_el.get("content") or whole_el.get_text(strip=True)
            frac = frac_el.get("content") if frac_el else "00"
            price = float(f"{whole}.{frac}")
        except:
            price = None
    else:
        price = None

    # Unit size
    size_el = card.select_one("div[data-automation-id='product-variant']")
    size_text = size_el.get_text(strip=True) if size_el else None

    if not title or price is None:
        return None

    return {
        "scraped_name": title,
        "price": price,
        "unit_size": size_text,
        "brand": brand,
    }


def scrape_item(item):
    try:
        html = fetch_page(item)
        return parse_walmart_product(html)
    except Exception as e:
        print(f"Error while scraping {item}: {e}")
        return None


def scrape_all(basket_df):
    today = datetime.today().strftime("%Y-%m-%d")
    results = []

    for _, row in basket_df.iterrows():
        item = row["item_name"]
        basket = row["basket_type"]

        print(f"Scraping: {item}")

        product = scrape_item(item)

        if product is None:
            print(f"Skipping {item}, no data found")
            continue

        results.append({
            "date": today,
            "basket_type": basket,
            "item_name": item,
            "scraped_name": product["scraped_name"],
            "price": product["price"],
            "unit_size": product["unit_size"],
            "brand": product["brand"],
            "store": "Walmart",
        })

        # Polite delay
        time.sleep(random.uniform(2.5, 4.0))

    return results


def save_results(records):
    if not records:
        print("No data to save")
        return

    date_str = records[0]["date"].replace("-", "")
    out_dir = "cost_of_healthy_diet/data/raw/"
    os.makedirs(out_dir, exist_ok=True)

    filename = f"raw_prices_{date_str}.csv"
    path = os.path.join(out_dir, filename)

    fields = [
        "date", "basket_type", "item_name", "scraped_name",
        "price", "unit_size", "brand", "store"
    ]

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)

    print(f"Saved {len(records)} rows → {path}")


def main():
    # Go 2 levels up: scraping → src → project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

    basket_path = os.path.join(project_root, "basket_items.csv")
    raw_dir = os.path.join(project_root, "data", "raw")

    print("Looking for basket_items.csv at:", basket_path)

    basket_df = load_basket_items(basket_path)
    records = scrape_all(basket_df)
    save_results(records)


if __name__ == "__main__":
    query = "Whole Wheat Bread"
    html = fetch_page(query)
    debug_save_html(html, query)
    parsed = parse_walmart_product(html)
    print("Parsed product:", parsed)

