import os
import re
import pandas as pd
import pdfplumber
from src.utils import save_df


def parse_pdf_form(pdf_path: str) -> pd.DataFrame:
    """
    Extract text-based data from Racing & Sports greyhound form PDFs.
    Detects each dog's line (box number, name, trainer, last times, etc.)
    """
    print(f"📄 Reading PDF: {os.path.basename(pdf_path)}")

    dogs_data = []
    current_race = None
    track_name = os.path.splitext(os.path.basename(pdf_path))[0][:5]  # e.g., QLAKG → QLD track code

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue

            # Detect race header (e.g. "Race 3 – 520m")
            race_match = re.search(r"Race\s*(\d+).*?(\d{3,4})m", text)
            if race_match:
                current_race = int(race_match.group(1))
                distance = int(race_match.group(2))
            else:
                distance = None

            # Detect dog lines (Box No., Dog Name, Trainer, etc.)
            lines = text.split("\n")
            for line in lines:
                if re.match(r"^\s*\d+\s+[A-Z].*", line):  # starts with box number + name
                    parts = re.split(r"\s{2,}", line.strip())
                    if len(parts) < 2:
                        continue

                    # Try to capture dog info
                    box_no_match = re.match(r"^\d+", parts[0])
                    box_no = int(box_no_match.group()) if box_no_match else None
                    dog_name = parts[0].split(" ", 1)[1] if " " in parts[0] else parts[0]
                    trainer = None
                    last_3 = None

                    # Extract time (like "29.87" or "30.10")
                    time_match = re.search(r"\b\d{2}\.\d{2}\b", line)
                    time_val = float(time_match.group()) if time_match else None

                    # Extract placing or performance keywords
                    placing = None
                    if "1st" in line:
                        placing = 1
                    elif "2nd" in line:
                        placing = 2
                    elif "3rd" in line:
                        placing = 3

                    dogs_data.append({
                        "track": track_name,
                        "race": current_race,
                        "box": box_no,
                        "dog": dog_name.strip(),
                        "trainer": trainer,
                        "time_sec": time_val,
                        "distance": distance,
                        "finish_pos": placing,
                    })

    df = pd.DataFrame(dogs_data)
    if df.empty:
        print("⚠️ No dogs detected in this form.")
    return df


def parse_all_forms(input_dir: str, output_dir: str) -> pd.DataFrame:
    """
    Parse all form PDFs in input_dir and save cleaned CSVs to output_dir.
    """
    os.makedirs(output_dir, exist_ok=True)
    all_dfs = []

    for fname in os.listdir(input_dir):
        if not fname.lower().endswith(".pdf"):
            continue
        fpath = os.path.join(input_dir, fname)
        print(f"📘 Processing {fname} ...")
        df = parse_pdf_form(fpath)
        if not df.empty:
            out_name = os.path.splitext(fname)[0] + "_clean.csv"
            save_df(df, os.path.join(output_dir, out_name))
            all_dfs.append(df)
            print(f"✅ Saved cleaned data to cleaned_data/{out_name}")
        else:
            print(f"⚠️ Skipped {fname} (no usable data)")

    if all_dfs:
        return pd.concat(all_dfs, ignore_index=True)
    else:
        print("⚠️ No valid data extracted from any form.")
        return pd.DataFrame()
