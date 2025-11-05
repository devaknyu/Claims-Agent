from backend.state import ClaimState

def categorize_claim(state: ClaimState) -> ClaimState:
    """
    Dummy categorizer (replace with LLM).
    """
    desc = (state.incident_description or "").lower()

    if "car" in desc or "accident" in desc:
        state.claim_category = "Auto"
    elif "house" in desc or "fire" in desc:
        state.claim_category = "Home"
    elif "hospital" in desc or "surgery" in desc:
        state.claim_category = "Health"
    elif "travel" in desc or "flight" in desc:
        state.claim_category = "Travel"
    elif "life" in desc or "death" in desc:
        state.claim_category = "Life"
    else:
        state.claim_category = "Other"

    return state
