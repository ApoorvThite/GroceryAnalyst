import os
import pandas as pd


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
INTERIM_DIR = os.path.join(PROJECT_ROOT, "data", "interim")
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")


def main():
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    standardized_path = os.path.join(INTERIM_DIR, "standardized_prices.csv")
    df = pd.read_csv(standardized_path)

    # Basic sanity cleanup
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["date", "basket_type", "item_name"])

    # Select and order columns for the cleaned master table
    cols = [
        "date",
        "basket_type",
        "item_name",
        "scraped_name",
        "brand",
        "store",
        "price",
        "unit_size",
        "unit_value",
        "unit_unit",
        "grams_total",
        "price_per_100g",
        "price_per_unit",
        "source_file",
    ]
    cleaned = df[cols].copy()

    cleaned_path = os.path.join(PROCESSED_DIR, "cleaned_prices.csv")
    cleaned.to_csv(cleaned_path, index=False)
    print(f"Saved cleaned master table to {cleaned_path}")

    # Build canonical mapping: which scraped names map to which canonical item_name
    mapping = (
        cleaned[["item_name", "scraped_name", "brand", "store"]]
        .drop_duplicates()
        .sort_values(["item_name", "scraped_name"])
    )

    mapping_path = os.path.join(PROCESSED_DIR, "canonical_mapping.csv")
    mapping.to_csv(mapping_path, index=False)
    print(f"Saved canonical mapping to {mapping_path}")


if __name__ == "__main__":
    main()
