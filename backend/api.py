# backend/api.py
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from backend.state import ClaimState
from backend.graph import build_claim_graph
import shutil
import os
from typing import List

app = FastAPI(title="Claims Processing Agent API", version="1.0")

# Enable CORS (for your React/Vue frontend or AWS S3 hosted site)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can later restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/process-claim")
async def process_claim(
    user_input: str = Form(...),
    claimant_name: str = Form("Unknown"),
    incident_date: str = Form("Unknown"),
    files: List[UploadFile] = File([]),
):
    """
    Receives claim details + uploaded files and processes them
    through the claim agent graph.
    """

    # Save uploaded files locally for processing
    uploaded_paths = []
    for file in files:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        uploaded_paths.append(file_path)

    # Create initial state
    state = ClaimState(
        user_input=user_input,
        claimant_name=claimant_name,
        incident_date=incident_date,
        incident_description=user_input,
        uploaded_files=uploaded_paths,
    )

    # Run through the LangGraph pipeline
    graph = build_claim_graph()
    result_state = graph.invoke(state)

    return {
        "claim_category": result_state.claim_category,
        "validation_status": result_state.validation_status,
        "missing_documents": result_state.missing_documents,
        "notes": result_state.notes,
    }


@app.get("/")
async def root():
    return {"message": "Claims Agent API is running 🚀"}
