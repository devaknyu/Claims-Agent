from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field

@dataclass
class ClaimState:
    user_input: str
    claimant_name: Optional[str] = "Unknown"
    incident_date: Optional[str] = "Unknown"
    incident_description: Optional[str] = None
    claim_category: Optional[str] = None
    uploaded_files: List[str] = field(default_factory=list)
    missing_documents: List[str] = field(default_factory=list)
    validation_status: Optional[str] = None
    notes: Optional[str] = None

    # This lets LangGraph treat ClaimState as a dict-like object
    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)

    def dict(self) -> Dict[str, Any]:
        return self.__dict__
