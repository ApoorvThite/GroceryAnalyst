import os
import pandas as pd
from datetime import datetime
import numpy as np

# Yearly (monthly) inflation multipliers — realistic
INFLATION = {
    2020: {"Healthy": 0.0015, "UltraProcessed": 0.0015, "Neutral": 0.0015},
    2021: {"Healthy": 0.0025, "UltraProcessed": 0.0030, "Neutral": 0.0025},
    2022: {"Healthy": 0.0100, "UltraProcessed": 0.0070, "Neutral": 0.0080},
    2023: {"Healthy": 0.0050, "UltraProcessed": 0.0050, "Neutral": 0.0050},
    2024: {"Healthy": 0.0020, "UltraProcessed": 0.0025, "Neutral": 0.0020},
    2025: {"Healthy": 0.0020, "UltraProcessed": 0.0020, "Neutral": 0.0020},
}

def simulate_multiyear(input_csv, output_dir, start_year=2020, end_year=2025):
    df = pd.read_csv(input_csv)

    os.makedirs(output_dir, exist_ok=True)

    # baseline is Jan 2025 — we simulate backwards
    baseline_prices = df.copy()

    for year in range(end_year, start_year - 1, -1):
        for month in reversed(range(1, 13)):
            inflation = INFLATION[year]

            # Copy baseline
            month_df = baseline_prices.copy()
            month_date = datetime(year, month, 1)
            month_df["date"] = month_date.strftime("%Y-%m-%d")

            # Apply inflation (reverse annual drift)
            for basket in ["Healthy", "UltraProcessed", "Neutral"]:
                mask = month_df["basket_type"] == basket

                rate = inflation[basket]
                # reverse direction for backward simulation
                backward_factor = 1 / (1 + rate)

                # noise to make it more realistic
                noise = np.random.normal(1.0, 0.01, size=mask.sum())

                month_df.loc[mask, "price"] = (
                    month_df.loc[mask, "price"] * backward_factor * noise
                )

            # round
            month_df["price"] = month_df["price"].round(2)

            # Save file
            file_name = f"raw_prices_{month_date.strftime('%Y%m')}.csv"
            out_path = os.path.join(output_dir, file_name)
            month_df.to_csv(out_path, index=False)

            print(f"Saved {out_path}")

        # Prepare next year's baseline by applying larger backward deflation
        for basket in ["Healthy", "UltraProcessed", "Neutral"]:
            mask = baseline_prices["basket_type"] == basket
            rate = INFLATION[year][basket]
            baseline_prices.loc[mask, "price"] = (
                baseline_prices.loc[mask, "price"] / (1 + rate)
            )


def main():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    raw_dir = os.path.join(project_root, "data", "raw")
    baseline_csv = os.path.join(raw_dir, "raw_prices_20250101.csv")

    simulate_multiyear(
        input_csv=baseline_csv,
        output_dir=raw_dir,
        start_year=2020,
        end_year=2025
    )


if __name__ == "__main__":
    main()
