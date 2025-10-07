import os
import pandas as pd


def ensure_dirs(dir_list):
    """Make sure directories exist."""
    for d in dir_list:
        os.makedirs(d, exist_ok=True)


def save_df(df: pd.DataFrame, path: str):
    """Save DataFrame as CSV."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)


def load_df(path: str) -> pd.DataFrame:
    """Load CSV into DataFrame."""
    return pd.read_csv(path)
