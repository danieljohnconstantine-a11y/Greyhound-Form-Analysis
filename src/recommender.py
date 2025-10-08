import pandas as pd
import numpy as np

def recommend(df: pd.DataFrame) -> pd.DataFrame:
    """
    Recommend top greyhounds to bet on based on form, speed, and reliability scores.
    """

    if df.empty:
        print("⚠️ No data provided to recommender.")
        return pd.DataFrame()

    print("🎯 Selecting best dogs to bet...")

    # Composite score: emphasize form and speed, slightly less consistency
    df["score"] = (
        0.5 * df["overall_form"] +
        0.3 * df["speed_score"] +
        0.2 * df["reliability"]
    )

    # Normalise 0–1
    df["score"] = (df["score"] - df["score"].min()) / (df["score"].max() - df["score"].min() + 1e-9)

    # Choose top dogs per race
    top_dogs = (
        df.sort_values(["track", "race", "score"], ascending=[True, True, False])
        .groupby(["track", "race"])
        .head(3)  # Top 3 per race
        .reset_index(drop=True)
    )

    # Label bet types
    top_dogs["bet_type"] = np.where(
        top_dogs["score"] > 0.7, "WIN",
        np.where(top_dogs["score"] > 0.5, "PLACE", "WATCH")
    )

    # Choose overall "best bet" per track
    best_per_track = (
        top_dogs.sort_values(["track", "score"], ascending=[True, False])
        .groupby("track")
        .head(1)
        .assign(bet_type="BEST BET")
    )

    final = pd.concat([top_dogs, best_per_track]).drop_duplicates()

    # Sort neatly
    final = final.sort_values(["track", "race", "score"], ascending=[True, True, False])

    print(f"✅ Selected {len(final)} betting recommendations.")
    return final
