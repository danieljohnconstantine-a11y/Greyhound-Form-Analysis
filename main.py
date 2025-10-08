import os
import pandas as pd
from src.parser import parse_all_forms

def main():
    print("🐾 Starting Greyhound Analysis for today...")

    input_file = "forms/BDGOG0810form.txt"
    output_file = "outputs/picks.csv"

    if not os.path.exists(input_file):
        print(f"🚫 Input file not found: {input_file}")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        raw_text = f.read()

    df = parse_all_forms(raw_text)

    if df.empty:
        print("⚠️ No greyhound races detected or parsed.")
    else:
        os.makedirs("outputs", exist_ok=True)
        df.to_csv(output_file, index=False)
        print(f"✅ Parsed {df['RaceNumber'].nunique()} races with {len(df)} runners.")
        print(f"📁 Results saved to: {output_file}")

if __name__ == "__main__":
    main()
