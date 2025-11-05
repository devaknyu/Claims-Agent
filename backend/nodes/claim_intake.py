from backend.state import ClaimState

def claim_intake_node(state: ClaimState) -> ClaimState:
    """
    Intake step: capture user input and initialize claim state.
    """
    # Example placeholder: parse input
    if "accident" in state.user_input.lower():
        state.claim_category = "Auto"
        state.incident_description = state.user_input

    return state
