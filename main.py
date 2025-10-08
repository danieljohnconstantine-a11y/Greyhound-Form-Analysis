import os
import pandas as pd
from pdfminer.high_level import extract_text
from src.parser import parse_all_forms

def convert_pdf_to_text(pdf_path):
    try:
        text = extract_text(pdf_path)
        return text
    except Exception as e:
        print(f"❌ Failed to convert {pdf_path}: {e}")
        return ""

def main():
    print("🐾 Starting Greyhound Analysis for today...")

    input_folder = "data"
    output_file = "outputs/picks.csv"
    all_text = ""

    for filename in os.listdir(input_folder):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(input_folder, filename)
            print(f"📄 Converting {filename} to text...")
            text = convert_pdf_to_text(pdf_path)
            all_text += text + "\n"

    if not all_text.strip():
        print("🚫 No usable text extracted from PDFs.")
        return

    df = parse_all_forms(all_text)

    if df.empty:
        print("⚠️ No greyhound races detected or parsed.")
    else:
        os.makedirs("outputs", exist_ok=True)
        df.to_csv(output_file, index=False)
        print(f"✅ Parsed {df['RaceNumber'].nunique()} races with {len(df)} runners.")
        print(f"📁 Results saved to: {output_file}")

if __name__ == "__main__":
    main()
