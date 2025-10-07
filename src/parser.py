import os
import pandas as pd
import pdfplumber
from .utils import save_df


def parse_csv(file_path: str) -> pd.DataFrame:
    """If the form is already a CSV, read directly."""
    return pd.read_csv(file_path)


def parse_pdf(file_path: str) -> pd.DataFrame:
    """Extract text or tables from PDF forms."""
    tables = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                df = pd.DataFrame(table[1:], columns=table[0])
                tables.append(df)

    if not tables:
        print(f"⚠️ No tables found in {file_path}")
        return pd.DataFrame()

    df = pd.concat(tables, ignore_index=True)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df


def parse_form(file_path: str, out_dir: str) -> pd.DataFrame:
    """Detect file type and parse accordingly."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        df = parse_csv(file_path)
    elif ext == ".pdf":
        df = parse_pdf(file_path)
    else:
        print(f"⚠️ Unsupported file type: {file_path}")
        return pd.DataFrame()

    if df.empty:
        return df

    out_name = os.path.splitext(os.path.basename(file_path))[0] + ".csv"
    out_path = os.path.join(out_dir, out_name)
    save_df(df, out_path)
    return df


def parse_all_forms(input_dir: str, output_dir: str) -> pd.DataFrame:
    """Parse all forms and combine them into one DataFrame."""
    all_dfs = []
    for fname in os.listdir(input_dir):
        path = os.path.join(input_dir, fname)
        if not os.path.isfile(path):
            continue
        try:
            df = parse_form(path, output_dir)
            if not df.empty:
                all_dfs.append(df)
        except Exception as e:
            print(f"❌ Error parsing {fname}: {e}")

    if all_dfs:
        combined = pd.concat(all_dfs, ignore_index=True)
        print(f"✅ Parsed {len(all_dfs)} files, {len(combined)} rows total.")
        return combined
    else:
        print("⚠️ No valid data extracted.")
        return pd.DataFrame()
