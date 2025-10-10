import pandas as pd
from datetime import datetime

# Import modules from src
from src.parser import parse_all_forms
from src.features import build_features
from src.validate_picks import validate_picks
from src.betting_summary import generate_betting_summary

def main():
    # === Step 1: Parse today's form ===
    with open("forms/BDGOG1010form.txt", "r", encoding="utf-8") as f:
        raw_text = f.read()

    parsed_df = parse_all_forms(raw_text, filename="BDGOG1010form.txt")
    parsed_df.to_csv("outputs/todays_form.csv", index=False)
    print("✅ Parsed form saved to outputs/todays_form.csv")

    # === Step 2: Score features ===
    ranked_df = build_features(parsed_df)
    ranked_df.to_csv("outputs/ranked.csv", index=False)
    print("✅ Ranked data saved to outputs/ranked.csv")

    # === Step 3: Validate picks ===
    validate_picks("outputs/ranked.csv", "outputs/todays_form.csv", "outputs/validation.csv")

    # === Step 4: Filter matched picks ===
    validation = pd.read_csv("outputs/validation.csv")
    matched = validation[validation["FoundInRaceField"] == "Yes"]

    # Merge with ranked data to get full details
    ranked = pd.read_csv("outputs/ranked.csv")
    betting_df = pd.merge(matched, ranked, on=["DogName", "RaceDate", "Track", "RaceNumber"])
    betting_df.to_csv("outputs/betting_summary.csv", index=False)
    print("✅ Betting summary saved to outputs/betting_summary.csv")

    # === Step 5: Optional betting summary printout ===
    print("\n📋 Today's Betting Picks:")
    for _, row in betting_df.iterrows():
        print(f"Race {row['RaceNumber']} - {row['DogName']} - {row['Track']} - {row['Distance']}m - Score: {row['Score']}")

if __name__ == "__main__":
    main()
