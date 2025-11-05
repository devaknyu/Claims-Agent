# backend/nodes/request_info.py
from backend.state import ClaimState

def request_additional_info(state: ClaimState) -> ClaimState:
    """
    Handles cases where validation fails and more info is required from user.
    """
    missing_notes = []
    if not state.claimant_name or state.claimant_name == "Unknown":
        missing_notes.append("Please provide your full name.")
    if not state.incident_date or state.incident_date == "Unknown":
        missing_notes.append("Please provide the incident date.")
    if not state.claim_category:
        missing_notes.append("We couldn’t identify your claim category. Please confirm it manually.")

    state.validation_status = "fail"
    state.notes = " ".join(missing_notes) if missing_notes else "Awaiting more details."
    return state
