import os
import pandas as pd
from pdfminer.high_level import extract_text
from src.parser import parse_all_forms
from src.predictor import pick_winners

def convert_pdf_to_text(pdf_path):
    try:
        return extract_text(pdf_path)
    except Exception as e:
        print(f"❌ Failed to convert {pdf_path}: {e}")
        return ""

def main():
    print("🐾 Starting Greyhound Analysis for today...")

    input_folder = "data"
    output_folder = "outputs"
    os.makedirs(output_folder, exist_ok=True)

    all_text = ""

    # Convert all PDFs in data/ to text
    for filename in os.listdir(input_folder):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(input_folder, filename)
            print(f"📄 Converting {filename} to text...")
            text = convert_pdf_to_text(pdf_path)
            all_text += text + "\n"

    if not all_text.strip():
        print("🚫 No usable text extracted from PDFs.")
        return

    # Parse all races
    df = parse_all_forms(all_text)

    if df.empty:
        print("⚠️ No greyhound races detected or parsed.")
        return

    # Save full parsed data
    picks_path = os.path.join(output_folder, "picks.csv")
    df.to_csv(picks_path, index=False)
    print(f"✅ Parsed {df['RaceNumber'].nunique()} races with {len(df)} runners.")
    print(f"📁 Full data saved to: {picks_path}")

    # Predict winners
    winners = pick_winners(df)
    winners_path = os.path.join(output_folder, "winners.csv")
    winners.to_csv(winners_path, index=False)
    print(f"🏁 Winners saved to: {winners_path}")

if __name__ == "__main__":
    main()
