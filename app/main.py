from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
from dotenv import load_dotenv

from game_engine import CourtroomGameEngine
from models import GameState, PlayerAction, GameResponse, CaseData

load_dotenv()

app = FastAPI(
    title="CourtroomAI: Legal Minds",
    description="Interactive AI-driven legal simulation game backend",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize game engine
game_engine = CourtroomGameEngine()

class StartCaseRequest(BaseModel):
    case_id: Optional[str] = None

class AskQuestionRequest(BaseModel):
    question: str
    witness_name: str

class PresentEvidenceRequest(BaseModel):
    evidence_id: str
    description: str

class NextTurnRequest(BaseModel):
    action_type: str  # "question", "evidence", "objection", "closing"
    details: Dict[str, Any]

@app.post("/start_case", response_model=GameResponse)
async def start_case(request: StartCaseRequest):
    """Start a new case or load a specific case"""
    try:
        case_data = game_engine.start_case(request.case_id)
        return GameResponse(
            success=True,
            message="Case started successfully",
            data=case_data,
            game_state=game_engine.get_game_state()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask_question", response_model=GameResponse)
async def ask_question(request: AskQuestionRequest):
    """Ask a question to a specific witness"""
    try:
        response = game_engine.ask_question(request.question, request.witness_name)
        return GameResponse(
            success=True,
            message="Question processed",
            data=response,
            game_state=game_engine.get_game_state()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/present_evidence", response_model=GameResponse)
async def present_evidence(request: PresentEvidenceRequest):
    """Present evidence to the court"""
    try:
        response = game_engine.present_evidence(request.evidence_id, request.description)
        return GameResponse(
            success=True,
            message="Evidence presented",
            data=response,
            game_state=game_engine.get_game_state()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/next_turn", response_model=GameResponse)
async def next_turn(request: NextTurnRequest):
    """Process the next turn in the game"""
    try:
        response = game_engine.next_turn(request.action_type, request.details)
        return GameResponse(
            success=True,
            message="Turn processed",
            data=response,
            game_state=game_engine.get_game_state()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/verdict", response_model=GameResponse)
async def get_verdict():
    """Get the final verdict from the judge"""
    try:
        verdict = game_engine.get_verdict()
        return GameResponse(
            success=True,
            message="Verdict delivered",
            data=verdict,
            game_state=game_engine.get_game_state()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/game_state", response_model=GameState)
async def get_game_state():
    """Get current game state"""
    return game_engine.get_game_state()

@app.get("/available_actions")
async def get_available_actions():
    """Get available actions for the current turn"""
    try:
        actions = game_engine.get_available_actions()
        return {"actions": actions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/case_summary")
async def get_case_summary():
    """Get a summary of the current case"""
    try:
        summary = game_engine.get_case_summary()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 