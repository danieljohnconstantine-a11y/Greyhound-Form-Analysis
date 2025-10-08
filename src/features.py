import pandas as pd
import numpy as np

def feature_box_preference(df: pd.DataFrame) -> pd.DataFrame:
    """
    Estimate a dog's comfort with each box based on available rating + performance averages.
    """
    if "box" not in df.columns:
        return pd.DataFrame()
    grouped = (
        df.groupby(["dog", "box"])["rating"]
        .mean()
        .reset_index()
        .rename(columns={"rating": "avg_box_rating"})
    )
    return grouped


def feature_speed(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute average and best speeds per dog across all races.
    """
    if "speed_kmh" not in df.columns:
        return pd.DataFrame()
    grouped = (
        df.groupby("dog")["speed_kmh"]
        .agg(["mean", "max"])
        .reset_index()
        .rename(columns={"mean": "avg_speed_kmh", "max": "best_speed_kmh"})
    )
    return grouped


def feature_consistency(df: pd.DataFrame) -> pd.DataFrame:
    """
    Measure how consistent the dog’s speeds are (low std = consistent performer).
    """
    if "speed_kmh" not in df.columns:
        return pd.DataFrame()
    grouped = (
        df.groupby("dog")["speed_kmh"]
        .std()
        .reset_index()
        .rename(columns={"speed_kmh": "speed_stddev"})
    )
    return grouped


def feature_win_place(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize win and place percentages (to scale 0–1).
    """
    subset = df[["dog", "win_pct", "place_pct"]].drop_duplicates()
    subset["win_rate"] = subset["win_pct"].fillna(0) / 100
    subset["place_rate"] = subset["place_pct"].fillna(0) / 100
    return subset[["dog", "win_rate", "place_rate"]]


def merge_features(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Combine all engineered features into one DataFrame.
    """
    if raw_df.empty:
        print("⚠️ No data provided to merge_features()")
        return pd.DataFrame()

    print("🔧 Building performance features...")

    box_feat = feature_box_preference(raw_df)
    spd_feat = feature_speed(raw_df)
    con_feat = feature_consistency(raw_df)
    wp_feat = feature_win_place(raw_df)

    merged = raw_df.merge(box_feat, on=["dog", "box"], how="left")
    merged = merged.merge(spd_feat, on="dog", how="left")
    merged = merged.merge(con_feat, on="dog", how="left")
    merged = merged.merge(wp_feat, on="dog", how="left")

    # Fill any NaN with neutral values
    merged.fillna({
        "avg_box_rating": merged["avg_box_rating"].mean(),
        "avg_speed_kmh": merged["avg_speed_kmh"].mean(),
        "best_speed_kmh": merged["best_speed_kmh"].mean(),
        "speed_stddev": merged["speed_stddev"].mean(),
        "win_rate": 0.0,
        "place_rate": 0.0
    }, inplace=True)

    # Create derived metrics for prediction
    merged["speed_score"] = merged["avg_speed_kmh"] / merged["best_speed_kmh"]
    merged["reliability"] = 1 / (1 + merged["speed_stddev"])
    merged["overall_form"] = (
        0.4 * merged["win_rate"] +
        0.3 * merged["place_rate"] +
        0.3 * merged["speed_score"]
    )

    print("✅ Features merged successfully.")
    return merged
