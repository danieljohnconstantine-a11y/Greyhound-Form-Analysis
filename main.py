import os
import pandas as pd
from pdfminer.high_level import extract_text
from src.parser import parse_all_forms
from src.features import build_features
from src.predictor import pick_winners
from src.recommender import recommend
from src.betting_summary import generate_betting_summary

def convert_pdf_to_text(pdf_path):
    try:
        return extract_text(pdf_path)
    except Exception as e:
        print(f"❌ Failed to convert {pdf_path}: {e}")
        return ""

def main():
    print("🐾 Starting Greyhound Analysis for today...")

    input_folder = "data"
    output_folder = "outputs"
    os.makedirs(output_folder, exist_ok=True)

    all_dfs = []

    print("🐾 Step 1: Parsing race forms...")
    for filename in os.listdir(input_folder):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(input_folder, filename)
            print(f"📘 Processing {filename} ...")
            text = convert_pdf_to_text(pdf_path)
            print(f"📄 Reading PDF: {filename}")
            parsed_df = parse_all_forms(text, filename)
            print(f"✅ Extracted {len(parsed_df)} dogs from {filename}")
            all_dfs.append(parsed_df)

    if not all_dfs:
        print("🚫 No race data found.")
        return

    df = pd.concat(all_dfs, ignore_index=True)
    picks_path = os.path.join(output_folder, "picks.csv")
    df.to_csv(picks_path, index=False)
    print(f"✅ Saved full parsed data → {picks_path}")

    print("🐾 Step 2: Building dog features...")
    ranked = build_features(df)

    print("🐾 Step 3: Ranking dogs by performance...")
    ranked_path = os.path.join(output_folder, "ranked.csv")
    ranked.to_csv(ranked_path, index=False)
    print(f"✅ Ranked data saved → {ranked_path}")

    print("🐾 Step 4: Selecting top betting picks...")
    winners = pick_winners(ranked)
    winners_path = os.path.join(output_folder, "winners.csv")
    winners.to_csv(winners_path, index=False)
    print(f"🏁 Winners saved to: {winners_path}")

    print("🐾 Step 5: Generating betting summary...")
    summary_path = os.path.join(output_folder, "betting_summary.csv")
    generate_betting_summary(winners_path, summary_path)

    print(f"📋 Betting summary saved to: {summary_path}")
    print("🎯 Done! Check your results in the outputs folder.")

if __name__ == "__main__":
    main()
