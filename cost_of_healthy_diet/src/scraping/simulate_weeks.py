import os
from datetime import datetime, timedelta

import numpy as np
import pandas as pd


def simulate_weeks(
    input_csv: str,
    output_dir: str,
    num_weeks: int = 8,
    weekly_mean_inflation: float = 0.01,
    weekly_std_inflation: float = 0.02,
):
    df = pd.read_csv(input_csv)

    # Ensure there is a date column
    if "date" not in df.columns:
        raise ValueError("Input CSV must have a 'date' column")

    base_date = pd.to_datetime(df["date"].iloc[0])

    os.makedirs(output_dir, exist_ok=True)

    for week in range(num_weeks):
        week_df = df.copy()
        week_date = base_date + timedelta(weeks=week)
        week_date_str = week_date.strftime("%Y-%m-%d")

        # Draw a random inflation factor per row
        # You can tweak these to make healthy basket inflate more later
        random_inflation = np.random.normal(
            loc=weekly_mean_inflation * week,  # slight upward drift over time
            scale=weekly_std_inflation,
            size=len(week_df),
        )

        week_df["price"] = week_df["price"] * (1 + random_inflation)
        week_df["price"] = week_df["price"].round(2)
        week_df["date"] = week_date_str

        out_path = os.path.join(
            output_dir,
            f"raw_prices_{week_date.strftime('%Y%m%d')}.csv"
        )
        week_df.to_csv(out_path, index=False)
        print(f"Saved simulated week {week + 1} to {out_path}")


def main():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

    raw_dir = os.path.join(project_root, "data", "raw")
    # Use the baseline file you created manually
    baseline_csv = os.path.join(raw_dir, "raw_prices_20250101.csv")

    simulate_weeks(
        input_csv=baseline_csv,
        output_dir=raw_dir,
        num_weeks=8,
        weekly_mean_inflation=0.01,
        weekly_std_inflation=0.015,
    )


if __name__ == "__main__":
    main()
