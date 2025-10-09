import pandas as pd

def generate_betting_summary(ranked_path, output_path, score_threshold=5):
    df = pd.read_csv(ranked_path)

    # Filter high-confidence picks
    picks = df[df["Score"] >= score_threshold]

    # Sort by RaceDate, Track, RaceNumber
    picks = picks.sort_values(by=["RaceDate", "Track", "RaceNumber"])

    # Format summary
    summary = []
    for _, row in picks.iterrows():
        line = f"Race {row['RaceNumber']} - {row['DogName']} - {row['Track']} - {row['Distance']}m - {row['RaceDate']}"
        summary.append(line)

    # Save to file
    pd.DataFrame({"Summary": summary}).to_csv(output_path, index=False)
    print(f"✅ Betting summary saved to: {output_path}")

if __name__ == "__main__":
    generate_betting_summary("outputs/ranked.csv", "outputs/betting_summary.csv")
