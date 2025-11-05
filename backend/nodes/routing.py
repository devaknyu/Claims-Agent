# backend/nodes/routing.py
from ..main import ClaimState

def validation_router(state: ClaimState) -> str:
    if state["validation_status"] == "fail":
        return "request_additional_info"
    return "categorization"

def checklist_router(state: ClaimState) -> str:
    if state.get("missing_documents"):
        return "request_missing"
    category = state.get("claim_category")
    if category == "Auto":
        return "process_auto"
    elif category == "Health":
        return "process_health"
    elif category == "Home":
        return "process_home"
    elif category == "Travel":
        return "process_travel"
    elif category == "Life":
        return "process_life"
    else:
        return "process_other"

def route_after_request(state: ClaimState) -> str:
    if state.get("missing_documents"):
        return "checklist"
    return f"process_{state['claim_category'].lower()}"
