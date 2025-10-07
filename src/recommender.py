import pandas as pd


def recommend(ranks_df: pd.DataFrame, min_score: float = 0.5, max_rank: int = 2) -> pd.DataFrame:
    recs = []
    for (track, race_id), grp in ranks_df.groupby(["track", "race_id"]):
        picks = grp[(grp["score"] >= min_score) & (grp["rank_in_race"] <= max_rank)]
        for _, row in picks.iterrows():
            recs.append({
                "track": track,
                "race_id": race_id,
                "dog": row["dog"],
                "score": row["score"],
                "rank": row["rank_in_race"],
                "bet_type": "WIN" if row["rank_in_race"] == 1 else "PLACE"
            })
    return pd.DataFrame(recs)

