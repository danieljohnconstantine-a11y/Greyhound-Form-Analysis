import os
import pandas as pd


def ensure_dirs(dir_list):
    for d in dir_list:
        os.makedirs(d, exist_ok=True)


def save_df(df: pd.DataFrame, path: str):
    df.to_csv(path, index=False)


def load_df(path: str) -> pd.DataFrame:
    return pd.read_csv(path)

