# backend/nodes/process_category.py

from typing import List
import os
import pytesseract
from PIL import Image
import pdfplumber
from backend.state import ClaimState  # Ensure consistent import path

# ---- Required documents mapping for categories ----
CATEGORY_REQUIRED_DOCS = {
    "Auto": ["Driver’s License", "Vehicle Registration", "Accident Report"],
    "Home": ["Proof of Ownership", "Damage Photos", "Repair Estimates"],
    "Health": ["Medical Report", "Bills", "Insurance Card"],
    "Travel": ["Itinerary", "Proof of Expense", "Travel Insurance Policy"],
    "Life": ["Death Certificate", "Policy Document", "ID Proof"],
    "Other": []
}

# ---- Keywords to detect each required document ----
REQUIRED_DOCS_KEYWORDS = {
    "Driver’s License": ["Driver License", "DL", "Date of Birth", "License Number"],
    "Vehicle Registration": ["Registration", "VIN", "Vehicle", "Owner"],
    "Accident Report": ["Police Report", "Accident", "Report Number"],
    "Proof of Ownership": ["Ownership", "Deed", "Title", "Property"],
    "Damage Photos": ["Damage", "Repair", "Photo", "Image"],
    "Repair Estimates": ["Estimate", "Repair", "Cost"],
    "Medical Report": ["Medical Report", "Hospital", "Diagnosis", "Patient"],
    "Bills": ["Invoice", "Bill", "Charge", "Payment"],
    "Insurance Card": ["Insurance", "Policy", "Card"],
    "Itinerary": ["Itinerary", "Flight", "Travel", "Schedule"],
    "Proof of Expense": ["Receipt", "Expense", "Invoice"],
    "Travel Insurance Policy": ["Insurance", "Policy", "Coverage"],
    "Death Certificate": ["Death Certificate", "Deceased", "Record"],
    "Policy Document": ["Policy", "Contract", "Coverage"],
    "ID Proof": ["ID", "Passport", "License", "Identity"]
}


# ---- Text extraction from file ----
def extract_text(file_path: str) -> str:
    _, ext = os.path.splitext(file_path.lower())
    try:
        if ext in [".png", ".jpg", ".jpeg"]:
            return pytesseract.image_to_string(Image.open(file_path))
        elif ext == ".pdf":
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += (page.extract_text() or "") + " "
            return text
        elif ext == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
    except Exception:
        pass
    return ""


# ---- Verify uploaded documents ----
def verify_uploaded_docs(uploaded_files: List[str], category: str) -> List[str]:
    required_docs = CATEGORY_REQUIRED_DOCS.get(category, [])
    missing = []
    for doc in required_docs:
        keywords = REQUIRED_DOCS_KEYWORDS.get(doc, [])
        matched = False
        for file_path in uploaded_files:
            text = extract_text(file_path)
            if any(k.lower() in text.lower() for k in keywords):
                matched = True
                break
        if not matched:
            missing.append(doc)
    return missing


# ---- Unified category processor ----
def process_category(state: ClaimState) -> ClaimState:
    """
    Handles verification and processing logic based on claim category.
    Integrates document validation and category-specific messages.
    """
    category = state.get("claim_category", "Other")
    uploaded = state.get("uploaded_files", []) or []

    # Manual fallback for unknown categories
    if category == "Other":
        state.notes = "Manual review required. Please upload any relevant documents."
        state.validation_status = "manual_review"
        return state

    # Step 1: verify uploaded docs
    missing = verify_uploaded_docs(uploaded, category)

    if missing:
        state.missing_documents = missing
        state.validation_status = "fail"
        state.notes = f"Missing or invalid documents: {', '.join(missing)}. Please upload them."
        return state

    # Step 2: process by category
    messages = {
        "Auto": "Auto claim is being processed successfully.",
        "Home": "Home claim is being processed successfully.",
        "Health": "Health claim is being processed successfully.",
        "Travel": "Travel claim is being processed successfully.",
        "Life": "Life claim is being processed successfully.",
    }

    state.missing_documents = []
    state.validation_status = "success"
    state.notes = messages.get(category, "Claim processed successfully.")

    return state
