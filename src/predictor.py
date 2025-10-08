import pandas as pd
import numpy as np

def score_dogs(race_df: pd.DataFrame, weights: dict = None) -> pd.DataFrame:
    """
    Given one race worth of dogs + features, assign a performance score to each dog.
    """
    if race_df.empty:
        return pd.DataFrame()

    if weights is None:
        # You can adjust these weights later based on testing
        weights = {
            "speed_mps": 0.35,
            "top3_rate": 0.25,
            "avg_finish_from_box": -0.15,  # lower average finish = better
            "best_time": -0.15,            # lower time = better
            "time_stddev": -0.10           # more consistent = better
        }

    df = race_df.copy()

    # Normalize numeric features to 0–1 scale
    for col in weights.keys():
        if col not in df.columns:
            df[col] = 0
        values = df[col].astype(float)
        df[col + "_norm"] = (values - values.min()) / (values.max() - values.min() + 1e-6)

    # Compute total weighted score
    df["score"] = 0
    for col, w in weights.items():
        df["score"] += df[col + "_norm"] * w

    # Rank dogs in this race by score (1 = best)
    df["rank_in_race"] = df["score"].rank(ascending=False, method="min")
    df = df.sort_values("score", ascending=False).reset_index(drop=True)
    return df


def rank_all_races(full_df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply scoring to all races in the full dataset.
    """
    if full_df.empty:
        return pd.DataFrame()

    all_ranked = []
    grouped = full_df.groupby(["track", "race"], dropna=False)

    for (track, race_id), race_data in grouped:
        ranked_race = score_dogs(race_data)
        ranked_race["track"] = track
        ranked_race["race"] = race_id
        all_ranked.append(ranked_race)

    return pd.concat(all_ranked, ignore_index=True)
