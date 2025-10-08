import pandas as pd

def build_features(df):
    df = df.copy()

    # Clean up WinRate and PlaceRate
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

    # Normalize prize money
    df["PrizeMoney"] = pd.to_numeric(df["PrizeMoney"], errors="coerce").fillna(0)

    # Standardize trainer names
    df["Trainer"] = df["Trainer"].fillna("").str.title()

    # Fill missing metadata
    df["RaceDate"] = df["RaceDate"].fillna("UNKNOWN")
    df["Track"] = df["Track"].fillna("UNKNOWN")
    df["RaceNumber"] = df["RaceNumber"].fillna("UNKNOWN")
    df["Distance"] = df["Distance"].fillna("")

    return df
