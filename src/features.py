import pandas as pd
import numpy as np


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Generate useful metrics from parsed forms."""
    df = df.copy()

    # Rename common columns if not present
    for col in ["track", "race_id", "dog", "box", "distance", "time_sec", "finish_pos", "race_date"]:
        if col not in df.columns:
            df[col] = np.nan

    # Average speed (m/s)
    df["speed_mps"] = df["distance"].astype(float) / df["time_sec"].astype(float)

    # Consistency: std of times per dog
    cons = df.groupby("dog")["time_sec"].std().reset_index().rename(columns={"time_sec": "time_stddev"})
    df = df.merge(cons, on="dog", how="left")

    # Preferred box
    box_pref = df.groupby(["dog", "box"])["finish_pos"].mean().reset_index()
    box_pref = box_pref.rename(columns={"finish_pos": "avg_finish_from_box"})
    df = df.merge(box_pref, on=["dog", "box"], how="left")

    # Distance form
    dist_perf = df.groupby(["dog", "distance"])["time_sec"].agg(["mean", "min"]).reset_index()
    dist_perf.columns = ["dog", "distance", "avg_time", "best_time"]
    df = df.merge(dist_perf, on=["dog", "distance"], how="left")

    # Top-3 rate
    df["in_top3"] = df["finish_pos"].apply(lambda x: 1 if x in [1, 2, 3] else 0)
    top3 = df.groupby("dog")["in_top3"].mean().reset_index().rename(columns={"in_top3": "top3_rate"})
    df = df.merge(top3, on="dog", how="left")

    df.fillna(0, inplace=True)
    return df
