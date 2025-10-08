import pandas as pd
import numpy as np

def feature_box_preference(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute average finish per box for each dog.
    """
    box_perf = (
        df.groupby(["dog", "box"])["finish_pos"]
        .mean()
        .reset_index()
        .rename(columns={"finish_pos": "avg_finish_from_box"})
    )
    return box_perf


def feature_distance_performance(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute average and best time per distance for each dog.
    """
    dist_perf = (
        df.groupby(["dog", "distance"])["time_sec"]
        .agg(["mean", "min"])
        .reset_index()
        .rename(columns={"mean": "avg_time", "min": "best_time"})
    )
    return dist_perf


def feature_recent_top3(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute the percentage of top-3 finishes per dog.
    """
    top3 = (
        df.assign(top3=lambda x: (x["finish_pos"] <= 3).astype(int))
        .groupby("dog")["top3"]
        .mean()
        .reset_index()
        .rename(columns={"top3": "top3_rate"})
    )
    return top3


def feature_consistency(df: pd.DataFrame) -> pd.DataFrame:
    """
    Measure how consistent each dog's times are (lower stddev = more consistent).
    """
    cons = (
        df.groupby("dog")["time_sec"]
        .std()
        .reset_index()
        .rename(columns={"time_sec": "time_stddev"})
    )
    return cons


def merge_features(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge all engineered features into the main dataframe.
    """
    if raw_df.empty:
        return pd.DataFrame()

    box_feat = feature_box_preference(raw_df)
    dist_feat = feature_distance_performance(raw_df)
    top3_feat = feature_recent_top3(raw_df)
    cons_feat = feature_consistency(raw_df)

    # Merge all features
    df = raw_df.merge(box_feat, on=["dog", "box"], how="left")
    df = df.merge(dist_feat, on=["dog", "distance"], how="left")
    df = df.merge(top3_feat, on="dog", how="left")
    df = df.merge(cons_feat, on="dog", how="left")

    # Fill missing values
    df.fillna({
        "avg_finish_from_box": 4.5,  # mid-field
        "avg_time": df["time_sec"].max() if "time_sec" in df else 0,
        "best_time": df["time_sec"].max() if "time_sec" in df else 0,
        "top3_rate": 0.0,
        "time_stddev": df["time_sec"].std() if "time_sec" in df else 0.0,
    }, inplace=True)

    # Compute derived metric: speed (m/s)
    if "distance" in df.columns and "time_sec" in df.columns:
        df["speed_mps"] = df["distance"] / df["time_sec"].replace(0, np.nan)

    return df
