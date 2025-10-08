import os
import argparse
import pandas as pd
from src.utils import ensure_dirs, save_df
from src.parser import parse_all_forms
from src.features import merge_features
from src.predictor import rank_all_races
from src.recommender import recommend

def main():
    print("🐾 Starting Greyhound Analysis for today...")

    # Folder setup
    input_dir = "data"
    clean_dir = "cleaned_data"
    output_dir = "outputs"
    ensure_dirs([clean_dir, output_dir])

    # Step 1: Parse race forms
    print("🐾 Step 1: Parsing race forms...")
    parsed_df = parse_all_forms(input_dir, clean_dir)
    if parsed_df.empty:
        print("⚠️ No data parsed. Exiting.")
        return

    # Step 2: Build features
    print("🐾 Step 2: Building dog features...")
    feat_df = merge_features(parsed_df)
    if feat_df.empty:
        print("⚠️ No features generated. Exiting.")
        return

    # Step 3: Rank dogs
    print("🐾 Step 3: Ranking dogs by performance...")
    ranked = rank_all_races(feat_df)
    if ranked.empty:
        print("⚠️ No ranked data. Exiting.")
        return

    # Step 4: Recommend bets
    print("🐾 Step 4: Selecting top betting picks...")
    recs = recommend(ranked, min_score=0.5, max_rank=2)
    if recs.empty:
        print("⚠️ No recommendations found.")
    else:
        # Save to CSV
        picks_path = os.path.join(output_dir, "picks.csv")
        save_df(recs, picks_path)
        print(f"✅ Betting recommendations saved to {picks_path}")

    print("\n🎯 Analysis complete.\n")

if __name__ == "__main__":
    main()
