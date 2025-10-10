import os
import pdfplumber

def convert_latest_pdf_to_text(forms_folder="forms"):
    # Find the most recent PDF file in the forms folder
    pdf_files = [f for f in os.listdir(forms_folder) if f.lower().endswith(".pdf")]
    if not pdf_files:
        print("❌ No PDF files found in forms/")
        return None

    latest_pdf = max(pdf_files, key=lambda f: os.path.getmtime(os.path.join(forms_folder, f)))
    pdf_path = os.path.join(forms_folder, latest_pdf)
    txt_path = pdf_path.replace(".pdf", ".txt")

    # Convert PDF to text
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"✅ Converted {latest_pdf} to {os.path.basename(txt_path)}")
    return txt_path
