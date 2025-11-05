import os
import re
import pdfplumber

def extract_text_from_latest_pdf(folder):
    if not os.path.exists(folder):
        print(f"❌ Folder not found: {folder}")
        return None

    pdf_files = [f for f in os.listdir(folder) if f.lower().endswith(".pdf")]
    if not pdf_files:
        print("❌ No PDF files found.")
        return None

    pdf_files.sort(key=lambda f: os.path.getmtime(os.path.join(folder, f)), reverse=True)
    pdf_path = os.path.join(folder, pdf_files[0])

    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += (page.extract_text() or "") + "\n"
    except Exception as e:
        print(f"⚠️ Error reading PDF: {e}")
        return None

    print(f"✅ Extracted text from {os.path.basename(pdf_path)}")
    return text

def main():
    print("🔍 Running debug parser...")

    forms_folder = "data"
    raw_text = extract_text_from_latest_pdf(forms_folder)
    if not raw_text:
        print("❌ No text extracted.")
        input("\nPress Enter to exit...")
        return

    lines = raw_text.splitlines()
    print(f"\n📄 First 100 lines of extracted text:\n")
    for i, line in enumerate(lines[:100]):
        print(f"{i+1:03d}: {line.strip()}")

    print("\n🔍 Checking for dog entry matches...\n")
    dog_pattern = re.compile(
        r"^(\d+)\.?\s*(\d{3,5})?([A-Za-z'’\- ]+)\s+(\d+[a-z])\s+([\d.]+)kg\s+(\d+)\s+([A-Za-z'’\- ]+)\s+(\d+)\s*-\s*(\d+)\s*-\s*(\d+)\s+\$(\d+[,\d]*)\s+(\S+)\s+(\S+)\s+(\S+)",
        re.IGNORECASE
    )

    match_count = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        match = dog_pattern.match(stripped)
        status = "✅ MATCH" if match else "❌ NO MATCH"
        print(f"{i+1:03d}: {status} | {stripped}")
        if match:
            match_count += 1

    print(f"\n🔎 Total matched dog entries: {match_count}")
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
