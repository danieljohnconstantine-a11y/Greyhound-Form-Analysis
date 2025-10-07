import os
import argparse
from src.utils import ensure_dirs, save_df
from src.parser import parse_all_forms
from src.features import build_features
from src.predictor import score_and_rank
from src.recommender import recommend_bets


def main(args):
    input_dir = args.input_dir
    clean_dir = args.clean_dir
    output_dir = args.output_dir

    ensure_dirs([clean_dir, output_dir])

    print("🐾 Step 1: Parsing race forms...")
    raw_df = parse_all_forms(input_dir, clean_dir)
    if raw_df.empty:
        print("⚠️ No data parsed. Exiting.")
        return

    print("📊 Step 2: Building features...")
    feat_df = build_features(raw_df)

    print("🧮 Step 3: Scoring and ranking dogs...")
    ranked_df = score_and_rank(feat_df)

    print("🎯 Step 4: Generating betting recommendations...")
    recs = recommend_bets(ranked_df, min_score=args.min_score, max_rank=args.max_rank)

    picks_path = os.path.join(output_dir, "picks.csv")
    save_df(recs, picks_path)
    print(f"✅ Picks saved to {picks_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Greyhound Form Analysis Pipeline")
    parser.add_argument("--input_dir", type=str, default="data", help="Raw forms directory (PDF/CSV)")
    parser.add_argument("--clean_dir", type=str, default="cleaned_data", help="Parsed CSV output folder")
    parser.add_argument("--output_dir", type=str, default="outputs", help="Folder for recommendations")
    parser.add_argument("--min_score", type=float, default=0.5, help="Minimum score threshold")
    parser.add_argument("--max_rank", type=int, default=2, help="Maximum rank per race to include")
    args = parser.parse_args()
    main(args)
