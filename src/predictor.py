import pandas as pd


def score_and_rank(df: pd.DataFrame) -> pd.DataFrame:
    """Score each dog per race based on feature weights."""
    weights = {
        "speed_mps": 0.35,
        "top3_rate": 0.25,
        "avg_finish_from_box": -0.15,
        "best_time": -0.15,
        "time_stddev": -0.10,
    }

    df = df.copy()
    for f in weights:
        if f not in df.columns:
            df[f] = 0
        df[f + "_norm"] = (df[f] - df[f].min()) / (df[f].max() - df[f].min() + 1e-6)

    df["score"] = sum(df[f + "_norm"] * w for f, w in weights.items())

    df["rank_in_race"] = df.groupby(["track", "race_id"])["score"].rank(ascending=False, method="min")
    return df.sort_values(["track", "race_id", "rank_in_race"])
