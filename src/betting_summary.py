import pandas as pd

def generate_betting_summary(winners_path, output_path):
    df = pd.read_csv(winners_path)

    # Fill missing values
    df["Track"] = df["Track"].fillna("UNKNOWN")
    df["RaceDate"] = df["RaceDate"].fillna("UNKNOWN")
    df["Distance"] = df["Distance"].fillna("UNKNOWN")
    df["RaceNumber"] = df["RaceNumber"].fillna("UNKNOWN")

    # Format summary
    df["Summary"] = df.apply(
        lambda row: f"Race {row['RaceNumber']} - {row['DogName']} - {row['Track']} - {row['Distance']} - {row['RaceDate']}",
        axis=1
    )

    # Save to file
    df[["Summary"]].to_csv(output_path, index=False)
    print(f"📋 Betting summary saved to: {output_path}")

if __name__ == "__main__":
    generate_betting_summary("outputs/winners.csv", "outputs/betting_summary.csv")
