import pandas as pd
from datetime import datetime

def filter_today_winners(winners_path, output_path):
    # Load winners
    df = pd.read_csv(winners_path)

    # Get today's date in YYYY-MM-DD format
    today = datetime.today().strftime("%Y-%m-%d")

    # Filter for today's races
    today_df = df[df["RaceDate"] == today]

    # Sort by RaceNumber
    today_df = today_df.sort_values(by="RaceNumber")

    # Save filtered results
    today_df.to_csv(output_path, index=False)
    print(f"✅ Today's winners saved to: {output_path}")

if __name__ == "__main__":
    filter_today_winners("outputs/winners.csv", "outputs/today_winners.csv")
