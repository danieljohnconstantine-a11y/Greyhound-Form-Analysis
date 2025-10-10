import pandas as pd
from datetime import datetime

def validate_picks(winners_path, race_field_path, output_path):
    # Load winners
    winners = pd.read_csv(winners_path)

    # Load race field (from parsed PDF form)
    race_field = pd.read_csv(race_field_path)

    # Normalize date format
    winners["RaceDate"] = pd.to_datetime(winners["RaceDate"]).dt.strftime("%Y-%m-%d")
    race_field["RaceDate"] = pd.to_datetime(race_field["RaceDate"]).dt.strftime("%Y-%m-%d")

    # Today's date
    today = datetime.today().strftime("%Y-%m-%d")

    # Filter both to today's races
    winners_today = winners[winners["RaceDate"] == today]
    field_today = race_field[race_field["RaceDate"] == today]

    # Compare each winner to race field
    results = []
    for _, row in winners_today.iterrows():
        dog = row["DogName"]
        track = row["Track"]
        race_num = str(row["RaceNumber"])
        found = field_today[
            (field_today["DogName"].str.strip().str.lower() == dog.strip().lower()) &
            (field_today["Track"] == track) &
            (field_today["RaceNumber"].astype(str) == race_num)
        ]

        results.append({
            "DogName": dog,
            "RaceDate": today,
            "Track": track,
            "RaceNumber": race_num,
            "SuggestedAsWinner": "Yes",
            "FoundInRaceField": "Yes" if not found.empty else "No",
            "Notes": "✅ Match" if not found.empty else "❌ Dog not in race field"
        })

    # Save results
    pd.DataFrame(results).to_csv(output_path, index=False)
    print(f"✅ Validation saved to: {output_path}")

if __name__ == "__main__":
    validate_picks("outputs/winners.csv", "outputs/todays_form.csv", "outputs/validation.csv")
