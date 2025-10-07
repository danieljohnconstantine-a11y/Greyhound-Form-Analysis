#!/usr/bin/env python3
"""pipeline/parse_forms.py

Find PDFs for a given date (folder `forms/YYYY-MM-DD/`), parse each PDF using pdfplumber,
and write structured JSON files to `parsed/YYYY-MM-DD/`.

This parser uses best-effort heuristics and will likely need small layout-specific
tweaks to perfectly extract all fields from your forms.
"""
import argparse
from pathlib import Path
import json
import pdfplumber
import re
from datetime import datetime
from tqdm import tqdm

def iso_date(s):
    # allow passing YYYY-MM-DD or default to today
    if s:
        return s
    return datetime.utcnow().strftime("%Y-%m-%d")

def find_pdfs_for_date(date_str):
    p = Path("forms") / date_str
    if not p.exists():
        return []
    return sorted([str(x) for x in p.glob("*.pdf")])

def parse_pdf_minimal(pdf_path):
    # returns a list of race dicts
    races = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text() or ""
                lines = [l.strip() for l in text.splitlines() if l.strip()]
                current = None
                for ln in lines:
                    # detect race header: common patterns like 'Race 1' or 'Race No 1'
                    m_r = re.search(r"\b[Rr]ace(?:\s+No)?\s*(\d{1,2})\b", ln)
                    if m_r:
                        current = {"race_no": int(m_r.group(1)), "raw_header": ln, "runners": []}
                        races.append(current)
                        continue
                    # runner line heuristic: starts with box number or '1.' etc.
                    m_run = re.match(r"^(?:\d{1,2}[\.)]?\s+)([A-Za-z'\-\. ]{2,60})(?:\s+(\d{1,2}\.\d{2}))?$", ln)
                    if m_run and current is not None:
                        name = m_run.group(1).strip()
                        time = float(m_run.group(2)) if m_run.group(2) else None
                        # attempt to extract box if present at line start
                        m_box = re.match(r"^(\d{1,2})", ln)
                        box = int(m_box.group(1)) if m_box else None
                        current['runners'].append({"box": box, "name": name, "last_time": time, "raw": ln})
    except Exception as e:
        print(f"Failed to parse {pdf_path}: {e}")
    return races

def save_parsed(races, date_str, pdf_filename):
    out_dir = Path("parsed") / date_str
    out_dir.mkdir(parents=True, exist_ok=True)
    name = Path(pdf_filename).stem + ".json"
    out_path = out_dir / name
    out_path.write_text(json.dumps(races, indent=2, ensure_ascii=False), encoding='utf-8')
    return out_path

def main(date=None):
    date = iso_date(date)
    pdfs = find_pdfs_for_date(date)
    if not pdfs:
        print("No PDFs found for date:", date)
        return
    for pdf in tqdm(pdfs, desc="Parsing PDFs"):
        races = parse_pdf_minimal(pdf)
        out = save_parsed(races, date, pdf)
        print("Wrote parsed JSON:", out)

if __name__ == '__main__':
    import sys
    parser = argparse.ArgumentParser(description='Parse PDFs for a date')
    parser.add_argument('--date', help='YYYY-MM-DD (defaults to today)', default=None)
    args = parser.parse_args()
    main(args.date)
