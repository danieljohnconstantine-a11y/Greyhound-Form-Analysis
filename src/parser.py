import os
import pandas as pd
import tabula
from src.utils import save_df

def parse_pdf_form(pdf_path: str) -> pd.DataFrame:
    """
    Extracts all tables from a racing form PDF using tabula-py.
    Returns a combined DataFrame of all detected race data.
    """
    print(f"📄 Reading PDF: {os.path.basename(pdf_path)}")

    try:
        # Extract all tables from PDF
        tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True, guess=True, lattice=True)
    except Exception as e:
        print(f"❌ Tabula error: {e}")
        return pd.DataFrame()

    if not tables:
        print("⚠️ No tables found in PDF.")
        return pd.DataFrame()

    # Combine tables into one DataFrame
    combined = pd.concat(tables, ignore_index=True)
    combined = combined.dropna(how="all")
    combined.columns = [str(c).strip().lower().replace(" ", "_") for c in combined.columns]

    # Try to find important columns
    possible_cols = ["dog", "greyhound", "box", "no", "time", "distance", "place", "finish", "trainer", "split"]
    keep_cols = [c for c in combined.columns if any(k in c for k in possible_cols)]

    if not keep_cols:
        print("⚠️ No recognizable race columns found.")
        return pd.DataFrame()

    clean_df = combined[keep_cols].copy()
    clean_df.columns = [c.replace("\n", "_") for c in clean_df.columns]

    # Add metadata
    clean_df["source_file"] = os.path.basename(pdf_path)
    return clean_df


def parse_all_forms(input_dir: str, output_dir: str) -> pd.DataFrame:
    """
    Parse all PDF forms in input_dir and save cleaned versions to output_dir.
    """
    all_dfs = []
    os.makedirs(output_dir, exist_ok=True)

    for fname in os.listdir(input_dir):
        path = os.path.join(input_dir, fname)
        if not os.path.isfile(path) or not fname.lower().endswith(".pdf"):
            continue

        print(f"📘 Processing {fname} ...")
        out_name = os.path.splitext(fname)[0] + "_clean.csv"
        out_path = os.path.join(output_dir, out_name)

        df = parse_pdf_form(path)
        if not df.empty:
            save_df(df, out_path)
            all_dfs.append(df)
            print(f"✅ Saved cleaned data to {out_path}")
        else:
            print(f"⚠️ Skipped {fname} (no usable data)")

    if all_dfs:
        full_df = pd.concat(all_dfs, ignore_index=True)
        return full_df
    else:
        print("⚠️ No valid data extracted from any form.")
        return pd.DataFrame()
