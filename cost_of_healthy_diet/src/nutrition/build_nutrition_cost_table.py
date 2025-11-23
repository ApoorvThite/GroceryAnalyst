import os
import pandas as pd
import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")


def compute_nutrient_density(row):
    """
    Simple nutrient density index.

    Higher:
      - protein
      - fiber
    Lower:
      - sugar
      - saturated fat
      - calories (lightly penalized)
    """
    protein = row["protein_per_100g"] or 0
    fiber = row["fiber_per_100g"] or 0
    sugar = row["sugar_per_100g"] or 0
    sat_fat = row["saturated_fat_per_100g"] or 0
    calories = row["calories_per_100g"] or 0

    beneficial = protein + fiber
    harmful = sugar + sat_fat + 0.02 * calories  # small penalty for calorie density

    if harmful <= 0:
        harmful = 1.0

    return beneficial / harmful


def main():
    prices_path = os.path.join(PROCESSED_DIR, "cleaned_prices.csv")
    nutrition_path = os.path.join(PROCESSED_DIR, "item_nutrition.csv")

    prices = pd.read_csv(prices_path)
    nutrition = pd.read_csv(nutrition_path)

    # Merge on item_name
    df = prices.merge(nutrition, on="item_name", how="left")

    # Compute nutrient density
    df["nutrient_density_score"] = df.apply(compute_nutrient_density, axis=1)

    # Cost per 100 calories
    # price_per_100g is price for 100 g
    # calories_per_100g is calories for 100 g
    df["cost_per_100_calories"] = np.where(
        df["calories_per_100g"] > 0,
        df["price_per_100g"] / (df["calories_per_100g"] / 100.0),
        np.nan,
    )

    # Cost per gram protein
    df["cost_per_gram_protein"] = np.where(
        df["protein_per_100g"] > 0,
        df["price_per_100g"] / df["protein_per_100g"],
        np.nan,
    )

    out_cols = [
        "date",
        "basket_type",
        "item_name",
        "scraped_name",
        "brand",
        "store",
        "price",
        "unit_size",
        "price_per_100g",
        "calories_per_100g",
        "protein_per_100g",
        "fiber_per_100g",
        "sugar_per_100g",
        "saturated_fat_per_100g",
        "nutrient_density_score",
        "cost_per_100_calories",
        "cost_per_gram_protein",
    ]

    df_out = df[out_cols].copy()
    out_path = os.path.join(PROCESSED_DIR, "item_nutrition_cost.csv")
    df_out.to_csv(out_path, index=False)
    print(f"Saved nutrition plus cost table to {out_path}")


if __name__ == "__main__":
    main()
