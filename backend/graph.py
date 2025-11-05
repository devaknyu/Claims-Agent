from langgraph.graph import StateGraph, END
from backend.nodes.intake import claim_intake_node
from backend.nodes.validation import validate_claim
from backend.nodes.request_info import request_additional_info
from backend.nodes.process_category import process_category
from backend.state import ClaimState


def build_claim_graph():
    graph = StateGraph(ClaimState)

    graph.add_node("claim_intake", claim_intake_node)
    graph.add_node("validation", validate_claim)
    graph.add_node("request_additional_info", request_additional_info)
    graph.add_node("process_category", process_category)

    graph.set_entry_point("claim_intake")

    graph.add_edge("claim_intake", "validation")
    graph.add_conditional_edges(
        "validation",
        lambda state: (
            "request_additional_info"
            if state.validation_status == "fail"
            else "process_category"
        ),
        {
            "request_additional_info": "request_additional_info",
            "process_category": "process_category",
        },
    )

    graph.add_edge("request_additional_info", END)
    graph.add_edge("process_category", END)

    return graph.compile()
