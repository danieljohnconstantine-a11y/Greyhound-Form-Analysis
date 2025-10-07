import os
import pandas as pd
import pdfplumber
from .utils import save_df


def parse_csv_form(csv_path: str) -> pd.DataFrame:
    """Read CSV form directly."""
    df = pd.read_csv(csv_path)
    return df


def parse_pdf_form(pdf_path: str) -> pd.DataFrame:
    """Extracts tables from PDF form using pdfplumber."""
    tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tbl = page.extract_table()
            if tbl:
                df = pd.DataFrame(tbl[1:], columns=tbl[0])
                tables.append(df)

    if tables:
        df = pd.concat(tables, ignore_index=True)
    else:
        df = pd.DataFrame()

    # Standardize columns (example placeholders)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df


def parse_form(file_path: str, out_clean_path: str) -> pd.DataFrame:
    """Parse one form file (PDF or CSV)."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        df = parse_csv_form(file_path)
    elif ext == ".pdf":
        df = parse_pdf_form(file_path)
    else:
        print(f"⚠️ Unsupported file format: {file_path}")
        return pd.DataFrame()

    if not df.empty:
        save_df(df, out_clean_path)
    return df


def parse_all_forms(input_dir: str, output_dir: str) -> pd.DataFrame:
    """Parse every form in input_dir → output_dir → return combined DataFrame."""
    all_dfs = []
    for fname in os.listdir(input_dir):
        path = os.path.join(input_dir, fname)
        if not os.path.isfile(path):
            continue
        out_csv = os.path.join(output_dir, os.path.splitext(fname)[0] + ".csv")
        try:
            df = parse_form(path, out_csv)
            if not df.empty:
                all_dfs.append(df)
        except Exception as e:
            print(f"Error parsing {fname}: {e}")

    return pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()

