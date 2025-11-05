from backend.state import ClaimState

# backend/nodes/category_checklist.py
from ..main import ClaimState
from .process_category import CATEGORY_REQUIRED_DOCS

def category_checklist(state: ClaimState) -> ClaimState:
    category = state.get("claim_category")
    uploaded = state.get("uploaded_files", []) or []
    required = CATEGORY_REQUIRED_DOCS.get(category, [])
    missing = [doc for doc in required if doc not in uploaded]
    return {**state, "missing_documents": missing}



def request_missing_docs(state: ClaimState) -> ClaimState:
    if state.missing_documents:
        state.notes = f"Missing documents: {', '.join(state.missing_documents)}. Please upload them."
        state.validation_status = "fail"
    return state
