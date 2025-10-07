import pandas as pd
import numpy as np


def feature_box_preference(df: pd.DataFrame) -> pd.DataFrame:
    grp = df.groupby(["dog", "box"])["finish_pos"].mean().reset_index()
    grp = grp.rename(columns={"finish_pos": "avg_finish_from_box"})
    return grp


def feature_distance_performance(df: pd.DataFrame) -> pd.DataFrame:
    grp = df.groupby(["dog", "distance"])["time_sec"].agg(["mean", "min"]).reset_index()
    grp = grp.rename(columns={"mean": "avg_time", "min": "best_time"})
    return grp


def feature_recent_top3(df: pd.DataFrame, window: int = 5) -> pd.DataFrame:
    df = df.sort_values(["dog", "race_date"], ascending=[True, False])
    def compute_top3(g):
        return g["finish_pos"].head(window).le(3).sum() / min(len(g), window)
    out = df.groupby("dog").apply(compute_top3).reset_index()
    out.columns = ["dog", "top3_rate"]
    return out


def feature_days_since_run(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(["dog", "race_date"])
    df["days_since_last"] = df.groupby("dog")["race_date"].diff().dt.days
    return df


def feature_consistency(df: pd.DataFrame) -> pd.DataFrame:
    grp = df.groupby("dog")["time_sec"].std().reset_index()
    grp = grp.rename(columns={"time_sec": "time_stddev"})
    return grp


def merge_features(raw_df: pd.DataFrame) -> pd.DataFrame:
    box = feature_box_preference(raw_df)
    dist = feature_distance_performance(raw_df)
    top3 = feature_recent_top3(raw_df)
    cons = feature_consistency(raw_df)
    df2 = feature_days_since_run(raw_df)

    df_ = raw_df.merge(box, on=["dog", "box"], how="left")
    df_ = df_.merge(dist, on=["dog", "distance"], how="left")
    df_ = df_.merge(top3, on="dog", how="left")
    df_ = df_.merge(cons, on="dog", how="left")
    df_["days_since_last"] = df2["days_since_last"]

    df_.fillna({
        "avg_finish_from_box": df_["avg_finish_from_box"].max(),
        "avg_time": df_["avg_time"].max(),
        "best_time": df_["best_time"].max(),
        "top3_rate": 0.0,
        "time_stddev": df_["time_stddev"].max(),
        "days_since_last": 999,
    }, inplace=True)
    return df_

