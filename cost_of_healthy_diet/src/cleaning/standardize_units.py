import os
import re
import pandas as pd
import numpy as np


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
INTERIM_DIR = os.path.join(PROJECT_ROOT, "data", "interim")


WEIGHT_TO_GRAMS = {
    "g": 1.0,
    "gram": 1.0,
    "grams": 1.0,
    "kg": 1000.0,
    "lb": 453.592,
    "pound": 453.592,
    "pounds": 453.592,
    "oz": 28.3495,
    "ounce": 28.3495,
    "ounces": 28.3495,
    # approximate for liquids
    "fl oz": 29.57,
    "floz": 29.57,
    "ml": 1.0,
    "l": 1000.0,
    "liter": 1000.0,
    "liters": 1000.0,
}

COUNT_UNITS = {
    "count",
    "ct",
    "pack",
    "packs",
    "can",
    "cans",
    "box",
    "boxes",
    "bag",
    "bags",
    "dozen",
}


def parse_unit_size(text):
    """
    Parse unit_size strings like:
      - '20 oz'
      - '2 lb bag'
      - '3 lb'
      - '12 count'
      - '15.25 oz can'
      - '3 lb bag'

    Returns:
      value (float or None), unit (normalized str or None)
    """
    if not isinstance(text, str):
        return None, None

    text = text.strip().lower()

    # Match patterns like "3 lb", "15.25 oz", "2 lb bag"
    m = re.search(r"([\d\.]+)\s*([a-zA-Z ]+)", text)
    if not m:
        return None, None

    value_str = m.group(1)
    unit_str = m.group(2).strip()

    try:
        value = float(value_str)
    except ValueError:
        return None, None

    # normalize unit
    unit_str = unit_str.replace(".", "").strip()

    # handle some common composed units
    if "fl oz" in unit_str:
        unit = "fl oz"
    elif "floz" in unit_str:
        unit = "fl oz"
    elif "ounce" in unit_str or "oz" in unit_str:
        unit = "oz"
    elif "pound" in unit_str or "lb" in unit_str:
        unit = "lb"
    elif "gram" in unit_str or unit_str == "g":
        unit = "g"
    elif unit_str.startswith("kg"):
        unit = "kg"
    elif "liter" in unit_str or unit_str == "l":
        unit = "l"
    elif "ml" in unit_str:
        unit = "ml"
    elif any(u in unit_str for u in COUNT_UNITS):
        # treat count like a unit of items
        unit = "count"
    else:
        # fallback
        unit = unit_str

    return value, unit


def grams_from_unit(value, unit):
    """
    Convert a quantity and unit into total grams where possible.
    If the unit is count based or unknown, return None.
    """
    if unit is None:
        return None

    if unit in WEIGHT_TO_GRAMS:
        return value * WEIGHT_TO_GRAMS[unit]

    # count based or unknown, no gram conversion
    return None


def load_all_raw():
    frames = []
    for fname in os.listdir(RAW_DIR):
        if fname.startswith("raw_prices_") and fname.endswith(".csv"):
            path = os.path.join(RAW_DIR, fname)
            df = pd.read_csv(path)
            df["source_file"] = fname
            frames.append(df)
    if not frames:
        raise RuntimeError("No raw_prices_*.csv files found in data/raw")
    return pd.concat(frames, ignore_index=True)


def main():
    os.makedirs(INTERIM_DIR, exist_ok=True)

    df = load_all_raw()

    # parse unit_size into numeric value and unit
    values = []
    units = []
    grams_list = []

    for text in df["unit_size"]:
        v, u = parse_unit_size(text)
        values.append(v)
        units.append(u)
        grams_list.append(grams_from_unit(v, u) if v is not None else None)

    df["unit_value"] = values
    df["unit_unit"] = units
    df["grams_total"] = grams_list

    # price per 100 g only where grams_total is known and > 0
    df["price_per_100g"] = np.where(
        (df["grams_total"].notna()) & (df["grams_total"] > 0),
        df["price"] / df["grams_total"] * 100.0,
        np.nan,
    )

    # price per unit for count style items: if unit_unit == 'count'
    df["price_per_unit"] = np.where(
        (df["unit_unit"] == "count") & (df["unit_value"].notna()) & (df["unit_value"] > 0),
        df["price"] / df["unit_value"],
        np.nan,
    )

    out_path = os.path.join(INTERIM_DIR, "standardized_prices.csv")
    df.to_csv(out_path, index=False)
    print(f"Saved standardized prices to {out_path}")


if __name__ == "__main__":
    main()
