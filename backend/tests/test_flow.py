# backend/tests/test_flow.py
from backend.graph import build_claim_graph
from backend.state import ClaimState

def run_test(description, uploaded_files=None):
    print(f"\n=== Running claim test for input: '{description}' ===")
    graph = build_claim_graph()
    state = ClaimState(
        user_input=description,
        claimant_name="Unknown",
        incident_date="Unknown",
        incident_description=description,
        uploaded_files=uploaded_files or []
    )

    for event in graph.stream(state, {"recursion_limit": 30}):
        for node, update in event.items():
            if node != "__end__":
                print(f"\n[{node}]")
                print(update)

def main():
    # Test 1: Auto claim missing docs
    run_test("I was in a car accident last week", uploaded_files=["DriverLicense"])

    # Test 2: Health claim with partial info
    run_test("Hospital surgery for leg fracture", uploaded_files=["MedicalBill", "DoctorReport"])

    # Test 3: Other claim category (manual handling)
    run_test("Lost my antique collection due to flood", uploaded_files=["FloodDamageReport"])

if __name__ == "__main__":
    main()
