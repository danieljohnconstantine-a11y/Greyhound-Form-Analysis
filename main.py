import pandas as pd
from datetime import datetime

# Import modules from src
from src.pdf_to_text import convert_latest_pdf_to_text
from src.parser import parse_all_forms
from src.features import build_features
from src.validate_picks import validate_picks
from src.betting_summary import generate_betting_summary

def main():
    print("🚀 Starting Greyhound Analysis for today...")

    # === Step 1: Convert latest PDF to text ===
    # ✅ Changed from "forms" → "data" so it uses your existing folder
    form_path = convert_latest_pdf_to_text("data")
    if not form_path:
        print("❌ No form file found in data/. Exiting.")
        return

    # === Step 2: Parse the form ===
    with open(form_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    parsed_df = parse_all_forms(raw_text, filename=form_path)
    parsed_df.to_csv("outputs/todays_form.csv", index=False)
    print("✅ Parsed form saved to outputs/todays_form.csv")

    # === Step 3: Score features ===
    ranked_df = build_features(parsed_df)
    ranked_df.to_csv("outputs/ranked.csv", index=False)
    print("✅ Ranked data saved to outputs/ranked.csv")

    # === Step 4: Validate picks ===
    validate_picks("outputs/ranked.csv", "outputs/todays_form.csv", "outputs/validation.csv")

    # === Step 5: Filter matched picks ===
    validation = pd.read_csv("outputs/validation.csv")
    matched = validation[validation["FoundInRaceField"] == "Yes"]

    # Merge with ranked data to get full details
    ranked = pd.read_csv("outputs/ranked.csv")
    betting_df = pd.merge(matched, ranked, on=["DogName", "RaceDate", "Track", "RaceNumber"], how="inner")
    betting_df.to_csv("outputs/betting_summary.csv", index=False)
    print("✅ Betting summary saved to outputs/betting_summary.csv")

    # === Step 6: Print betting picks ===
    print("\n📋 Today's Betting Picks:")
    if betting_df.empty:
        print("⚠️ No matched picks found.")
    else:
        for _, row in betting_df.iterrows():
            print(f"Race {row['RaceNumber']} - {row['DogName']} - {row['Track']} - {row['Distance']}m - Score: {row['Score']}")

if __name__ == "__main__":
    main()
