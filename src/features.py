import pandas as pd

def build_features(df):
    df = df.copy()

    # Normalize basic fields
    df["WinRate"] = (
        df["WinRate"]
        .astype(str)
        .replace(["None", "nan", "NaN"], "")
        .str.replace("%", "", regex=False)
        .replace("", "0")
        .astype(float)
        .fillna(0)
    )

    df["PlaceRate"] = (
        df["PlaceRate"]
        .astype(str)
        .replace(["None", "nan", "NaN"], "")
        .str.replace("%", "", regex=False)
        .replace("", "0")
        .astype(float)
        .fillna(0)
    )

    df["PrizeMoney"] = pd.to_numeric(df["PrizeMoney"], errors="coerce").fillna(0)
    df["Trainer"] = df["Trainer"].fillna("").str.title()

    # Normalize new fields
    df["SpeedKMH"] = pd.to_numeric(df["SpeedKMH"], errors="coerce").fillna(0)
    df["DaysSinceLastRun"] = pd.to_numeric(df["DaysSinceLastRun"], errors="coerce").fillna(999)
    df["DistanceSpecialist"] = df["DistanceSpecialist"].fillna(False).astype(bool)
    df["TrackExperienceCount"] = pd.to_numeric(df["TrackExperienceCount"], errors="coerce").fillna(0)

    # Scoring logic
    df["BoxScore"] = df["Box"].apply(lambda b: 1 if b in [1, 4] else 0)
    df["TrainerScore"] = df["Trainer"].apply(lambda x: any(t in x for t in [
        "Dailly", "Camilleri", "Azzopardi", "Priest", "Geall", "Britton"
    ])).astype(int)
    df["WinScore"] = df["WinRate"].apply(lambda x: 1 if x >= 20 else 0)
    df["PlaceScore"] = df["PlaceRate"].apply(lambda x: 1 if x >= 40 else 0)
    df["PrizeScore"] = df.groupby(["RaceDate", "Track", "RaceNumber"])["PrizeMoney"].transform(
        lambda x: (x > x.median()).astype(int)
    )

    # New feature scores
    df["SpeedScore"] = df["SpeedKMH"].apply(lambda x: 1 if x >= 55 else 0)
    df["RestScore"] = df["DaysSinceLastRun"].apply(lambda x: 1 if 3 <= x <= 7 else 0)
    df["SpecialistScore"] = df["DistanceSpecialist"].astype(int)
    df["ExperienceScore"] = df["TrackExperienceCount"].apply(lambda x: 1 if x >= 2 else 0)

    # Total score
    df["Score"] = (
        df["BoxScore"] + df["TrainerScore"] + df["WinScore"] + df["PlaceScore"] +
        df["PrizeScore"] + df["SpeedScore"] + df["RestScore"] +
        df["SpecialistScore"] + df["ExperienceScore"]
    )

    return df
