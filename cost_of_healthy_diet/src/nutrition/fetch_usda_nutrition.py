import os
import time
import requests
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")

USDA_API_KEY = "lyk1r33NC9OvcAaLqe19W31b8mfoLgQmhqF80the"  # replace with your actual key
SEARCH_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"

# Map your item_name to cleaner USDA style search terms
SEARCH_TERMS = {
    "Whole Wheat": "whole wheat bread",
    "Brown Rice": "brown rice cooked",
    "Quinoa": "quinoa cooked",
    "Chickpeas (Dry)": "chickpeas cooked",
    "Lentils (Dry)": "lentils cooked",
    "Greek Yogurt": "greek yogurt plain nonfat",
    "Spinach": "spinach raw",
    "Broccoli": "broccoli raw",
    "Carrots": "carrots raw",
    "Apples": "apples raw with skin",
    "Bananas": "bananas raw",
    "Tofu": "tofu firm",
    "Oats": "oats dry",
    "Peanut Butter": "peanut butter smooth",
    "Olive Oil": "olive oil",
    "Frozen Pizza": "pizza cheese frozen baked",
    "Soda": "carbonated beverage cola",
    "Chips": "potato chips",
    "Instant Noodles": "ramen noodle soup prepared",
    "Sugary Cereal": "ready to eat cereal sweetened",
    "Ice Cream": "ice cream vanilla",
    "Candy": "chocolate candy",
    "White Bread": "white bread",
    "Processed Cheese Slice": "american cheese processed",
    "Chicken Nuggets": "chicken nuggets fried",
    "Energy Drink": "energy drink",
    "Microwave Popcorn": "popcorn microwave",
    "Hot Dogs": "frankfurter beef",
    "Chocolate Cookies": "chocolate sandwich cookies",
    "Mac and Cheese": "macaroni and cheese prepared",
    "Pasta": "spaghetti cooked",
    "Tomato Sauce": "tomato sauce canned",
    "Milk": "milk 2 percent",
    "Potatoes": "potatoes white flesh baked",
    "White Rice": "white rice cooked",
    "Tortillas": "flour tortillas",
    "Butter": "butter salted",
    "Canned Corn": "corn canned",
    "Canned Beans": "black beans canned",
    "Onions": "onions raw",
    "Eggs": "egg whole raw",
    "Snack Crackers": "snack crackers",
    "Flour": "wheat flour all purpose",
    "Sugar": "sugar granulated",
}


# Nutrient IDs in FoodData Central
NUTRIENT_IDS = {
    "calories": 1008,
    "protein": 1003,
    "fiber": 1079,
    "sugar": 2000,
    "saturated_fat": 1258,
}


def get_unique_items():
    basket_path = os.path.join(PROJECT_ROOT, "basket_items.csv")
    df = pd.read_csv(basket_path)
    return sorted(df["item_name"].unique())


def search_food(term):
    # First attempt: with dataType filter
    params = {
        "api_key": USDA_API_KEY,
        "query": term,
        "pageSize": 5,
        "dataType": ["Survey (FNDDS)", "SR Legacy", "Branded"],
    }

    try:
        r = requests.get(SEARCH_URL, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        foods = data.get("foods", [])
        if foods:
            return foods[0]
        print(f"No foods found with dataType filter for '{term}', retrying without filter...")
    except requests.HTTPError as e:
        print(f"First attempt failed for '{term}' with error {e}, retrying without filter...")

    # Second attempt: no dataType filter (let API choose)
    params2 = {
        "api_key": USDA_API_KEY,
        "query": term,
        "pageSize": 5,
    }

    r2 = requests.get(SEARCH_URL, params=params2, timeout=10)
    r2.raise_for_status()
    data2 = r2.json()
    foods2 = data2.get("foods", [])
    if not foods2:
        print(f"No foods found at all for '{term}'")
        return None

    return foods2[0]


def extract_nutrients(food):
    """
    Extract relevant nutrients from a FoodData Central "food" record.
    Values are typically per 100 g for SR Legacy and FNDDS.
    """
    nutrients = {k: None for k in NUTRIENT_IDS.keys()}
    fdc_id = food.get("fdcId")
    description = food.get("description")
    data_type = food.get("dataType")

    for n in food.get("foodNutrients", []):
        nid = n.get("nutrientId")
        for key, wanted_id in NUTRIENT_IDS.items():
            if nid == wanted_id:
                nutrients[key] = n.get("value")

    nutrients["fdc_id"] = fdc_id
    nutrients["description"] = description
    nutrients["data_type"] = data_type
    return nutrients


def main():
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    items = get_unique_items()
    records = []

    for item in items:
        term = SEARCH_TERMS.get(item, item)
        print(f"Fetching nutrition for {item} -> '{term}'")
        try:
            food = search_food(term)
        except Exception as e:
            print(f"Error fetching {item}: {e}")
            continue

        if not food:
            print(f"No result for {item}")
            continue

        nutrients = extract_nutrients(food)
        record = {
            "item_name": item,
            "search_term": term,
            "fdc_id": nutrients["fdc_id"],
            "description": nutrients["description"],
            "data_type": nutrients["data_type"],
            "calories_per_100g": nutrients["calories"],
            "protein_per_100g": nutrients["protein"],
            "fiber_per_100g": nutrients["fiber"],
            "sugar_per_100g": nutrients["sugar"],
            "saturated_fat_per_100g": nutrients["saturated_fat"],
        }
        records.append(record)

        time.sleep(0.5)  # be polite to the API

    df = pd.DataFrame(records)
    out_path = os.path.join(PROCESSED_DIR, "item_nutrition.csv")
    df.to_csv(out_path, index=False)
    print(f"Saved item level nutrition to {out_path}")


if __name__ == "__main__":
    main()
