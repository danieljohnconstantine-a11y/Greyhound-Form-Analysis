import os
import pandas as pd
from datetime import datetime
import pdfplumber

from src.parser import parse_all_forms
from src.features import build_features
from src.validate_picks import validate_picks

def convert_pdf_to_text(pdf_filename, source_folder="data"):
    # Ensure source folder exists
    if not os.path.exists(source_folder):
        os.makedirs(source_folder)
        print(f"📁 Created missing folder: {source_folder}")
        return None

    pdf_path = os.path.join(source_folder, pdf_filename)
    txt_path = pdf_path.replace(".pdf", ".txt")

    if not os.path.exists(pdf_path):
        print(f"❌ PDF not found: {pdf_path}")
        return None

    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"✅ Converted {pdf_filename} to {os.path.basename(txt_path)}")
    return txt_path

def main():
    print("🚀 Starting Greyhound Analysis for today...")

    # === Step 1: Choose your race form PDF ===
    pdf_filename = "QLAKG1010form.pdf"  # ✅ Change this to any file in data/
    form_path = convert_pdf_to_text(pdf_filename, source_folder="data")
    if not form_path:
        print("⚠️ Please place the correct PDF in the data/ folder and try again.")
        return

    # === Step 2: Parse the form ===
    with open(form_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    parsed_df = parse_all_forms(raw_text, filename=form_path)
    parsed_df.to_csv("outputs/todays_form.csv", index=False)
    print("✅ Parsed race form saved to outputs/todays_form.csv")

    # === Step 3: Score features ===
    ranked_df = build_features(parsed_df)
    ranked_df.to_csv("outputs/ranked.csv", index=False)
    print("✅ Ranked data saved to outputs/ranked.csv")

    # === Step 4: Select winners ===
    winners_df = ranked_df[ranked_df["WinScore"] > 0]
    winners_df.to_csv("outputs/winners.csv", index=False)
    print("✅ Winners saved to outputs/winners.csv")

    # === Step 5: Validate picks ===
    validate_picks("outputs/winners.csv", "outputs/todays_form.csv", "outputs/validation.csv")

    # === Step 6: Filter matched picks ===
    validation = pd.read_csv("outputs/validation.csv")
    if validation.empty:
        print("⚠️ No matching dogs found for today's races.")
        return

    matched = validation[validation["FoundInRaceField"] == "Yes"]
    betting_df = pd.merge(matched, ranked_df, on=["DogName", "RaceDate", "Track", "RaceNumber"])
    betting_df.to_csv("outputs/betting_summary.csv", index=False)
    print("✅ Betting summary saved to outputs/betting_summary.csv")

    # === Step 7: Print betting picks ===
    print("\n📋 Today's Betting Picks:")
    for _, row in betting_df.iterrows():
        print(f"Race {row['RaceNumber']} - {row['DogName']} - {row['Track']} - {row['Distance']}m - Score: {row['Score']}")

if __name__ == "__main__":
    main()
