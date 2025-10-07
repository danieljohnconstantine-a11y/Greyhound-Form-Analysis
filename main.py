import os
import argparse
from src.utils import ensure_dirs, save_df
from src.parser import parse_all_forms
from src.features import merge_features
from src.predictor import rank_all_races
from src.recommender import recommend


def main(args):
    input_dir = args.input_dir
    clean_dir = args.clean_dir
    output_dir = args.output_dir

    ensure_dirs([clean_dir, output_dir])

    print("🐾 Parsing race forms ...")
    raw_df = parse_all_forms(input_dir, clean_dir)
    if raw_df.empty:
        print("⚠️  No data parsed. Exiting.")
        return

    print("📊 Building features ...")
    feat_df = merge_features(raw_df)

    print("🧮 Scoring & ranking dogs ...")
    ranked = rank_all_races(feat_df)

    print("🎯 Generating recommendations ...")
    recs = recommend(ranked, min_score=args.min_score, max_rank=args.max_rank)

    picks_path = os.path.join(output_dir, "picks.csv")
    save_df(recs, picks_path)
    print(f"✅ Picks saved to {picks_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Greyhound Form Analysis Pipeline")
    parser.add_argument("--input_dir", type=str, default="data", help="Raw form files (PDF/CSV)")
    parser.add_argument("--clean_dir", type=str, default="cleaned_data", help="Parsed CSV outputs")
    parser.add_argument("--output_dir", type=str, default="outputs", help="Final picks output directory")
    parser.add_argument("--min_score", type=float, default=0.5, help="Minimum score threshold for recommendation")
    parser.add_argument("--max_rank", type=int, default=2, help="Max rank per race to consider bet")
    args = parser.parse_args()
    main(args)

