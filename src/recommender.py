import pandas as pd

def recommend(ranks_df: pd.DataFrame, min_score: float = 0.5, max_rank: int = 2) -> pd.DataFrame:
    """
    Recommend top dogs to bet on per race based on score and rank.
    - Only includes dogs above min_score and within top max_rank per race.
    """
    if ranks_df.empty:
        print("⚠️ No ranked data available for recommendations.")
        return pd.DataFrame()

    recommendations = []
    grouped = ranks_df.groupby(["track", "race"])

    for (track, race_id), group in grouped:
        # Filter by score threshold and rank position
        selected = group[(group["score"] >= min_score) & (group["rank_in_race"] <= max_rank)]
        if selected.empty:
            continue

        for _, row in selected.iterrows():
            bet_type = "WIN" if row["rank_in_race"] == 1 else "PLACE"
            rec = {
                "track": track,
                "race": race_id,
                "dog": row.get("dog", ""),
                "box": row.get("box", ""),
                "score": round(row.get("score", 0), 3),
                "speed_mps": round(row.get("speed_mps", 0), 2),
                "top3_rate": round(row.get("top3_rate", 0), 2),
                "bet_type": bet_type,
            }
            recommendations.append(rec)

    if not recommendations:
        print("⚠️ No dogs met the recommendation criteria.")
        return pd.DataFrame()

    recs_df = pd.DataFrame(recommendations)
    recs_df = recs_df.sort_values(["track", "race", "score"], ascending=[True, True, False])
    return recs_df
