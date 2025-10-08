import os
import pandas as pd
from src.parser import parse_all_forms

def main():
    print("🐾 Starting Greyhound Analysis for today...")

    input_folder = "data"
    output_file = "outputs/picks.csv"
    all_text = ""

    for filename in os.listdir(input_folder):
        if filename.endswith(".txt"):
            with open(os.path.join(input_folder, filename), "r", encoding="utf-8") as f:
                all_text += f.read() + "\n"

    if not all_text.strip():
        print("🚫 No text files found in 'data' folder.")
        return

    df = parse_all_forms(all_text)

    if df.empty:
        print("⚠️ No greyhound races detected or parsed.")
    else:
        os.makedirs("outputs", exist_ok=True)
        df.to_csv(output_file, index=False)
        print(f"✅ Parsed {df['RaceNumber'].nunique()} races with {len(df)} runners.")
        print(f"📁 Results saved to: {output_file}")

if __name__ == "__main__":
    main()
