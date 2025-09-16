# main.py
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
from typing import TypedDict, List, Optional
import os

# Load env vars
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# Initialize Groq LLM
llm = ChatGroq(
    temperature=0,
    model_name="llama3-70b-8192",
    groq_api_key=groq_api_key
)

# ---- Define state schema ----
class ClaimState(TypedDict):
    user_input: str
    claimant_name: str
    incident_date: str
    incident_description: str
    claim_category: str
    uploaded_files: Optional[List[str]]  # List of file paths or file IDs
    missing_documents: Optional[List[str]]  # Missing required docs for the category
    validation_status: Optional[str]     # "pending", "pass", "fail"
    notes: Optional[str]   

# ---- Node function ----
def claim_intake_node(state: ClaimState) -> ClaimState:
    import json

    prompt = f"""
    You are an insurance claims intake assistant.

    Extract the following details from the customer message if present:
    - Claimant name
    - Incident date
    - Incident description

    If some details are missing, write "Unknown".

    Return ONLY valid JSON in the following format:
    {{
        "claimant_name": "...",
        "incident_date": "...",
        "incident_description": "..."
    }}

    Customer message:
    {state['user_input']}
    """

    response = llm.invoke(prompt)

    # Handle case where Groq returns a list of content chunks
    raw_output = ""
    if isinstance(response.content, list):
        raw_output = " ".join([c.get("text", "") for c in response.content])
    else:
        raw_output = str(response.content).strip()

    # Default values
    extracted = {
        "claimant_name": "Unknown",
        "incident_date": "Unknown",
        "incident_description": "Unknown"
    }

    # Try to parse JSON
    try:
        parsed = json.loads(raw_output)
        for key in extracted:
            if parsed.get(key):
                extracted[key] = parsed[key]
    except json.JSONDecodeError:
        # If JSON fails, at least keep the description
        extracted["incident_description"] = state["user_input"]

    return {**state, **extracted}

def validate_claim(state: ClaimState) -> ClaimState:
    errors = []

    # Validate claimant name
    if not state.get("claimant_name") or state["claimant_name"] == "Unknown":
        errors.append("Claimant name is missing")

    # Validate incident date (basic check)
    if not state.get("incident_date") or state["incident_date"] == "Unknown":
        errors.append("Incident date is missing")

    # Validate description
    if not state.get("incident_description") or state["incident_description"] == "Unknown":
        errors.append("Incident description is missing")

    # Validate category
    if not state.get("claim_category") or state["claim_category"] == "Other":
        errors.append("Claim category is invalid or not supported")

    # If errors found, fail validation
    if errors:
        return {
            **state,
            "validation_status": "fail",
            "notes": f"Validation failed: {', '.join(errors)}"
        }

    # If valid so far, pass
    return {
        **state,
        "validation_status": "pass",
        "notes": "Validation checks passed"
    }
def validation_router(state: ClaimState) -> str:
    if state["validation_status"] == "fail":
        return "request_additional_info"
    return "categorization"

def request_additional_info(state: ClaimState) -> ClaimState:
    return {
        **state,
        "notes": f"Missing info: {state['notes']}. Please resubmit with corrected details.",
        "validation_status": "fail"
    }
def categorize_claim(state: ClaimState) -> ClaimState:
    prompt = f"""
    You are an insurance claim classifier.

    Based on the incident description: "{state['incident_description']}",  
    classify the claim into exactly ONE of the following categories:  
    Auto, Home, Health, Travel, Life.  

    If the description clearly does NOT fit any of the above categories,  
    respond with "Other".  

    Respond with ONLY the category name.
    """
    response = llm.invoke(prompt)
    # print("DEBUG CATEGORIZATION RESPONSE:", response)  # <-- ADD THIS
    category = response.content.strip()
    return {**state, "claim_category": category}

# Placeholder checklist function
def category_checklist(state: ClaimState) -> ClaimState:
    category = state["claim_category"]
    uploaded = state.get("uploaded_files", []) or []
    required = []

    if category == "Auto":
        required = ["Driver’s License", "Vehicle Registration", "Accident Report"]
    elif category == "Home":
        required = ["Proof of Ownership", "Damage Photos", "Repair Estimates"]
    elif category == "Health":
        required = ["Medical Report", "Bills", "Insurance Card"]
    elif category == "Travel":
        required = ["Itinerary", "Proof of Expense", "Travel Insurance Policy"]
    elif category == "Life":
        required = ["Death Certificate", "Policy Document", "ID Proof"]

    missing = [doc for doc in required if doc not in uploaded]

    return {**state, "missing_documents": missing}


# Placeholder request missing docs node
def request_missing_docs(state: ClaimState) -> ClaimState:
    if state["missing_documents"]:
        note = f"Missing documents: {', '.join(state['missing_documents'])}. Please upload them."
        return {**state, "notes": note, "validation_status": "fail"}
    return state


# Placeholder process nodes for each category
def process_auto_claim(state: ClaimState) -> ClaimState:
    return {**state, "validation_status": "pass", "notes": "Auto claim is being processed."}

def process_home_claim(state: ClaimState) -> ClaimState:
    return {**state, "validation_status": "pass", "notes": "Home claim is being processed."}

def process_health_claim(state: ClaimState) -> ClaimState:
    return {**state, "validation_status": "pass", "notes": "Health claim is being processed."}

def process_travel_claim(state: ClaimState) -> ClaimState:
    return {**state, "validation_status": "pass", "notes": "Travel claim is being processed."}

def process_life_claim(state: ClaimState) -> ClaimState:
    return {**state, "validation_status": "pass", "notes": "Life claim is being processed."}
def process_other_claim(state: ClaimState) -> ClaimState:
    return {
        **state,
        "validation_status": "pending",
        "notes": "Claim category not recognized, sent for manual review."
    }



def route_by_category(state: ClaimState) -> str:
    category = state["claim_category"].lower()
    if category == "Auto":
        return "auto_checklist"
    elif category == "Home":
        return "home_checklist"
    elif category == "Health":
        return "health_checklist"
    elif category == "Travel":
        return "travel_checklist"
    elif category == "Life":
        return "life_checklist"
    else:
        return "process_other_claim"
    
def checklist_router(state: ClaimState):
    if state.get("missing_documents"):
        return "request_missing"
    else:
        category = state.get("claim_category")
        if category == "Auto":
            return "process_auto"
        elif category == "Health":
            return "process_health"
        elif category == "Home":
            return "process_home"
        else:
            return "process_other"

# ---- Build graph ----
builder = StateGraph(ClaimState)
builder.add_node("claim_intake", claim_intake_node)
builder.add_node("validation", validate_claim)
builder.add_node("request_additional_info", request_additional_info)

builder.add_node("categorization", categorize_claim)
builder.add_node("checklist", category_checklist)
builder.add_node("request_missing", request_missing_docs)
builder.add_node("process_auto", process_auto_claim)
builder.add_node("process_home", process_home_claim)
builder.add_node("process_health", process_health_claim)
builder.add_node("process_travel", process_travel_claim)
builder.add_node("process_life", process_life_claim)
builder.add_node("process_other", process_other_claim)



builder.set_entry_point("claim_intake")
builder.add_edge("claim_intake","validation")
builder.add_edge("categorization", "checklist")
builder.add_edge("request_additional_info", END)

# builder.add_edge("categorization", "checklist")

builder.add_conditional_edges(
    "validation",
    validation_router,
    {"request_additional_info": "request_additional_info", "categorization": "categorization"}
)

builder.add_conditional_edges(
    "checklist",
    checklist_router,
    {
        "request_missing": "request_missing",
        "process_auto": "process_auto",
        "process_health": "process_health",
        "process_home": "process_home",
        "process_other": "process_other"
    }
)

# Conditional routing after request_missing
def route_after_request(state: ClaimState) -> str:
    if state["missing_documents"]:   # Still missing docs
        return "checklist"  # loop back to re-check
    return f"process_{state['claim_category'].lower()}"

builder.add_conditional_edges(
    "request_missing",
    route_after_request,
    {
        END: END,
        "process_auto": "process_auto",
        "process_home": "process_home",
        "process_health": "process_health",
        "process_travel": "process_travel",
        "process_life": "process_life",
    }
)

# builder.add_edge("categorization",END)
# builder.add_edge("claim_intake", END)

# ---- Compile ----
graph = builder.compile()

if __name__ == "__main__":
    from langgraph.graph import StateGraph

    # Build the graph
    graph = builder.compile()

    # --- Test Case 1: Auto claim, missing police report ---
    state1 = {
        "user_input": "I was in a car accident last week",
        "claimant_name": "John Doe",
        "incident_date": "2025-08-10",
        "incident_description": "Rear-ended at traffic light",
        "claim_category": "Auto",
        "uploaded_files": ["DriverLicense"],  # Missing PoliceReport
        "missing_documents": [],
        "validation_status": None,
        "notes": None
    }

    print("\n=== Running Auto claim with missing docs ===")
    for step in graph.stream(state1):
        print(step)

    # --- Test Case 2: Health claim, all docs present ---
    state2 = {
        "user_input": "I had surgery and need to claim expenses",
        "claimant_name": "Alice Smith",
        "incident_date": "2025-07-22",
        "incident_description": "Appendix surgery",
        "claim_category": "Health",
        "uploaded_files": ["MedicalReport", "Bill"],
        "missing_documents": [],
        "validation_status": None,
        "notes": None
    }

    print("\n=== Running Health claim with all docs ===")
    test_state = {
    "user_input": "Car accident on August 12th",
    "claimant_name": "Unknown",   # Force a fail
    "incident_date": "2025-08-12",
    "incident_description": "Rear-ended at signal",
    "claim_category": "Auto",
    "uploaded_files": ["Driver’s License"],
    "missing_documents": [],
    "validation_status": None,
    "notes": None
    }

    for step in graph.stream(test_state):
        print(step) 