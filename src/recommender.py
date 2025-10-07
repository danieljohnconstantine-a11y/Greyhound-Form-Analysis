import pandas as pd


def recommend_bets(df: pd.DataFrame, min_score: float = 0.5, max_rank: int = 2) -> pd.DataFrame:
    """Select top dogs per race for WIN/PLACE recommendations."""
    recommendations = []
    for (track, race_id), grp in df.groupby(["track", "race_id"]):
        picks = grp[(grp["score"] >= min_score) & (grp["rank_in_race"] <= max_rank)]
        for _, row in picks.iterrows():
            rec = {
                "track": track,
                "race_id": race_id,
                "dog": row["dog"],
                "box": row["box"],
                "score": round(row["score"], 3),
                "rank": int(row["rank_in_race"]),
                "bet_type": "WIN" if row["rank_in_race"] == 1 else "PLACE",
            }
            recommendations.append(rec)
    return pd.DataFrame(recommendations)
