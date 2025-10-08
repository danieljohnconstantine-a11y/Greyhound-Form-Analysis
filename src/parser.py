import os
import re
import pdfplumber
import pandas as pd
from src.utils import save_df


def parse_pdf_form(pdf_path: str) -> pd.DataFrame:
    """
    Advanced parser for Racing & Sports / Ladbrokes-style greyhound PDFs.
    Extracts Race#, Track, Dog name, Box, Trainer, Distance, Speed, Time, Margin, Rating, Win%, Place%.
    """
    print(f"📄 Reading PDF: {os.path.basename(pdf_path)}")
    all_rows = []
    track, race_num, distance = None, None, None

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue

            lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

            for i, line in enumerate(lines):
                # Track and race header, e.g. "Richmond Race 6" or "Race 4 – 520m"
                if re.search(r"Race\s*\d+", line, re.IGNORECASE):
                    m = re.search(r"(?P<track>[A-Za-z ]+)\s+Race\s*(?P<num>\d+)", line)
                    if m:
                        track = m.group("track").strip()
                        race_num = int(m.group("num"))
                    dist_match = re.search(r"(\d{3,4})m", " ".join(lines[i:i+3]))
                    distance = int(dist_match.group(1)) if dist_match else None

                # Each dog header line — pattern like: "Fear To Excel (1) 67112112"
                m_dog = re.match(r"^([A-Z][A-Za-z' ]+)\s*\((\d)\)", line)
                if m_dog:
                    dog = m_dog.group(1).strip().title()
                    box = int(m_dog.group(2))

                    # Look ahead for Trainer / Prize / Win Place
                    trainer, winp, placep, rating, speed, time = None, None, None, None, None, None
                    j = i
                    while j < len(lines) and not re.match(r"^[A-Z][A-Za-z' ]+\s*\(\d\)", lines[j]):
                        sub = lines[j]
                        if "Trainer:" in sub:
                            trainer = sub.split("Trainer:")[-1].split("(")[0].strip()
                        if "Win / Place:" in sub:
                            wp = re.findall(r"(\d+)%", sub)
                            if len(wp) >= 1:
                                winp = int(wp[0])
                            if len(wp) >= 2:
                                placep = int(wp[1])
                        if "Rating" in sub:
                            rmatch = re.search(r"(\d{2,3})", sub)
                            if rmatch:
                                rating = int(rmatch.group(1))
                        # average speed or win time (e.g. "0:22.92 63.0 km/h")
                        if re.search(r"\d+\.\d+\s*km/h", sub):
                            sm = re.search(r"(\d+\.\d+)\s*km/h", sub)
                            speed = float(sm.group(1)) if sm else None
                        if re.search(r"\d{2}\.\d{2}", sub):
                            tm = re.search(r"(\d{2}\.\d{2})", sub)
                            time = float(tm.group(1)) if tm else None
                        j += 1

                    all_rows.append({
                        "track": track,
                        "race": race_num,
                        "distance": distance,
                        "dog": dog,
                        "box": box,
                        "trainer": trainer,
                        "rating": rating,
                        "win_pct": winp,
                        "place_pct": placep,
                        "speed_kmh": speed,
                        "last_time": time,
                    })

    df = pd.DataFrame(all_rows)
    if df.empty:
        print("⚠️ No dogs detected in this form.")
    else:
        print(f"✅ Extracted {len(df)} dogs from {os.path.basename(pdf_path)}")

    return df


def parse_all_forms(input_dir: str, output_dir: str) -> pd.DataFrame:
    """
    Parse all PDF race forms in input_dir; write cleaned CSVs to output_dir.
    """
    os.makedirs(output_dir, exist_ok=True)
    all_dfs = []
    for file in os.listdir(input_dir):
        if not file.lower().endswith(".pdf"):
            continue
        print(f"📘 Processing {file} ...")
        df = parse_pdf_form(os.path.join(input_dir, file))
        if not df.empty:
            out_path = os.path.join(output_dir, os.path.splitext(file)[0] + "_clean.csv")
            save_df(df, out_path)
            all_dfs.append(df)
            print(f"✅ Saved cleaned data → {out_path}")
        else:
            print(f"⚠️ Skipped {file} (no usable data)")
    return pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()
