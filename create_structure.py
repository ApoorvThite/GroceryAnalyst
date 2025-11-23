import os

PROJECT_STRUCTURE = [
    "cost_of_healthy_diet/",
    "cost_of_healthy_diet/data/",
    "cost_of_healthy_diet/data/raw/",
    "cost_of_healthy_diet/data/interim/",
    "cost_of_healthy_diet/data/processed/",
    "cost_of_healthy_diet/notebooks/",
    "cost_of_healthy_diet/src/",
    "cost_of_healthy_diet/src/scraping/",
    "cost_of_healthy_diet/src/cleaning/",
    "cost_of_healthy_diet/src/nutrition/",
    "cost_of_healthy_diet/src/analysis/",
    "cost_of_healthy_diet/config/",
    "cost_of_healthy_diet/logs/",
]

PLACEHOLDER_FILES = {
    "cost_of_healthy_diet/README.md": "",
    "cost_of_healthy_diet/basket_items.csv": "",
    "cost_of_healthy_diet/notebooks/exploration.ipynb": "",
    "cost_of_healthy_diet/src/scraping/scrape_prices.py": "",
    "cost_of_healthy_diet/src/scraping/simulate_weeks.py": "",
    "cost_of_healthy_diet/src/cleaning/standardize_units.py": "",
    "cost_of_healthy_diet/src/cleaning/build_master_table.py": "",
    "cost_of_healthy_diet/src/nutrition/fetch_usda_nutrition.py": "",
    "cost_of_healthy_diet/src/analysis/basket_aggregates.py": "",
    "cost_of_healthy_diet/src/analysis/trends.py": "",
    "cost_of_healthy_diet/config/settings_example.yaml": "",
    "cost_of_healthy_diet/logs/scraping.log": "",
    "cost_of_healthy_diet/logs/errors.log": "",
}


def create_folders():
    for folder in PROJECT_STRUCTURE:
        os.makedirs(folder, exist_ok=True)
        print(f"Created folder: {folder}")


def create_files():
    for filepath, content in PLACEHOLDER_FILES.items():
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Created file: {filepath}")


if __name__ == "__main__":
    create_folders()
    create_files()
    print("\nProject structure created successfully!")
