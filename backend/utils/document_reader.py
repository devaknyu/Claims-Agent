# backend/utils/document_reader.py
import pytesseract
from PIL import Image
import pdfplumber
import os

# Simple keyword lists for each claim category
CATEGORY_KEYWORDS = {
    "Auto": ["driver", "license", "vehicle", "registration", "accident", "insurance"],
    "Home": ["property", "fire", "damage", "homeowner", "address", "repair"],
    "Health": ["hospital", "bill", "medical", "surgery", "doctor", "patient"],
    "Travel": ["flight", "ticket", "itinerary", "luggage", "delay", "airline"],
    "Life": ["death", "certificate", "policy", "beneficiary"],
}

def extract_text_from_file(file_path: str) -> str:
    """Extracts text from PDF or image files."""
    text = ""
    ext = os.path.splitext(file_path)[1].lower()

    if ext in [".pdf"]:
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
        except Exception as e:
            print(f"PDF read error: {e}")
    elif ext in [".png", ".jpg", ".jpeg"]:
        try:
            img = Image.open(file_path)
            text = pytesseract.image_to_string(img)
        except Exception as e:
            print(f"OCR error: {e}")
    else:
        print(f"Unsupported file type: {ext}")

    return text.lower()

def check_document_relevance(file_path: str, keywords: list[str]) -> bool:
    """Check if a document contains required keywords."""
    content = extract_text_from_file(file_path)
    return any(kw.lower() in content for kw in keywords)