from backend.state import ClaimState

def validate_claim(state: ClaimState) -> ClaimState:
    errors = []

    if not state.claimant_name or state.claimant_name == "Unknown":
        errors.append("Claimant name is missing")

    if not state.incident_date or state.incident_date == "Unknown":
        errors.append("Incident date is missing")

    if not state.incident_description or state.incident_description == "Unknown":
        errors.append("Incident description is missing")

    if not state.claim_category or state.claim_category == "Other":
        errors.append("Claim category is invalid or not supported")

    if errors:
        state.validation_status = "fail"
        state.notes = f"Validation failed: {', '.join(errors)}"
    else:
        state.validation_status = "pass"
        state.notes = "Validation checks passed"

    return state


def request_additional_info(state: ClaimState) -> ClaimState:
    state.validation_status = "fail"
    state.notes = f"Missing info: {state.notes}. Please resubmit with corrected details."
    return state
