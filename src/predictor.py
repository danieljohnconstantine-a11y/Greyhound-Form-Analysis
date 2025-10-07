import pandas as pd


def score_dogs(race_df: pd.DataFrame, weights: dict = None) -> pd.DataFrame:
    if weights is None:
        weights = {
            "avg_finish_from_box": -0.2,
            "best_time": -0.3,
            "top3_rate": 0.3,
            "time_stddev": -0.1,
            "days_since_last": -0.1,
        }

    df = race_df.copy()
    for f in weights:
        df[f + "_norm"] = (df[f] - df[f].min()) / (df[f].max() - df[f].min() + 1e-6)

    df["score"] = sum(df[f + "_norm"] * w for f, w in weights.items())
    df = df.sort_values("score", ascending=False).reset_index(drop=True)
    return df


def rank_all_races(full_df: pd.DataFrame) -> pd.DataFrame:
    out_records = []
    for (track, race_id), grp in full_df.groupby(["track", "race_id"]):
        scored = score_dogs(grp)
        scored["rank_in_race"] = scored["score"].rank(ascending=False, method="min")
        out_records.append(scored)
    return pd.concat(out_records, ignore_index=True)

