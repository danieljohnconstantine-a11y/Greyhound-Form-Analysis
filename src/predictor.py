import pandas as pd

def pick_winners(df):
    known_trainers = [
        "Dailly", "Delbridge", "Azzopardi", "Camilleri", "Formosa", "Geall",
        "Britton", "Petersen", "Bewley", "Priest", "Chilcott", "Robertson"
    ]

    df = df.copy()

    # Normalize and fill missing
    df["Trainer"] = df["Trainer"].fillna("").str.title()
    df["WinRate"] = df["WinRate"].astype(float).fillna(0)
    df["PlaceRate"] = df["PlaceRate"].astype(float).fillna(0)
    df["PrizeMoney"] = pd.to_numeric(df["PrizeMoney"], errors="coerce").fillna(0)

    # Scoring rules
    df["BoxScore"] = df["Box"].apply(lambda b: 1 if b in [1, 2, 3, 4] else 0)
    df["TrainerScore"] = df["Trainer"].apply(lambda x: any(t in x for t in known_trainers)).astype(int)
    df["WinScore"] = df["WinRate"].apply(lambda x: 1 if x >= 20 else 0)
    df["PlaceScore"] = df["PlaceRate"].apply(lambda x: 1 if x >= 40 else 0)
    df["PrizeScore"] = df.groupby(["RaceDate", "Track", "RaceNumber"])["PrizeMoney"].transform(
        lambda x: (x > x.median()).astype(int)
    )

    # Total score
    df["Score"] = df["BoxScore"] + df["TrainerScore"] + df["WinScore"] + df["PlaceScore"] + df["PrizeScore"]

    # Pick top scorer per race
    winners = (
        df.sort_values(by="Score", ascending=False)
        .groupby(["RaceDate", "Track", "RaceNumber"])
        .head(1)
        .reset_index(drop=True)
    )

    return winners
