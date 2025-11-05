# CREATE diagnostic.py IN YOUR src FOLDER
import os
import pdfplumber
import re

def check_files_and_structure():
    print("=== CHECKING FILE STRUCTURE ===")
    
    # Check data directory
    data_dir = 'data'
    if os.path.exists(data_dir):
        pdf_files = [f for f in os.listdir(data_dir) if f.endswith('.pdf')]
        print(f"📁 Found {len(pdf_files)} PDF files in data/:")
        for pdf_file in pdf_files:
            print(f"   - {pdf_file}")
    else:
        print("❌ data/ directory not found!")
        return

    # Check one PDF file
    if pdf_files:
        test_pdf = os.path.join(data_dir, pdf_files[0])
        print(f"\n🔍 ANALYZING: {test_pdf}")
        
        try:
            with pdfplumber.open(test_pdf) as pdf:
                print(f"📄 PDF has {len(pdf.pages)} pages")
                
                # Analyze first page
                page1 = pdf.pages[0]
                text = page1.extract_text()
                
                print(f"\n📝 FIRST 1500 CHARACTERS:")
                print("=" * 50)
                print(text[:1500])
                print("=" * 50)
                
                # Look for patterns
                print(f"\n🎯 PATTERN ANALYSIS:")
                
                # Find numbered items (like "1. ", "2. ", etc.)
                numbered_items = re.findall(r'\n\s*(\d+)\.\s*([^\n]{20,100})', text)
                print(f"Numbered items found: {len(numbered_items)}")
                for num, content in numbered_items[:5]:
                    print(f"   {num}. {content}")
                
                # Find form patterns
                form_patterns = re.findall(r'[a-zA-Z]?\d+[a-zA-Z]?', text)
                unique_forms = list(set([f for f in form_patterns if len(f) >= 3]))[:10]
                print(f"\nForm patterns: {unique_forms}")
                
                # Find career stats
                stats = re.findall(r'\b\d+-\d+-\d+\b', text)
                print(f"Career stats: {stats[:5]}")
                
                # Find prize money
                money = re.findall(r'\$\d+[,]?\d*', text)
                print(f"Prize money: {money[:5]}")
                
        except Exception as e:
            print(f"❌ Error reading PDF: {e}")

if __name__ == "__main__":
    check_files_and_structure()