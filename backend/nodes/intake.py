# backend/nodes/intake.py
from backend.state import ClaimState

def claim_intake_node(state: ClaimState) -> ClaimState:
    """
    Handles initial user input capture and basic normalization.
    Later this can be extended with NLP entity extraction or Groq model parsing.
    """
    user_input = state.user_input or ""
    state.incident_description = user_input
    state.claimant_name = state.claimant_name or "Unknown"
    state.incident_date = state.incident_date or "Unknown"
    return state
