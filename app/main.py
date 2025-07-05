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

class CallWitnessRequest(BaseModel):
    witness_name: str

class QuestionWitnessRequest(BaseModel):
    question: str

class UseEvidenceRequest(BaseModel):
    evidence_id: str

class GetClueRequest(BaseModel):
    pass

class JudgeChatRequest(BaseModel):
    statement: str

@app.post("/start_case", response_model=GameResponse)
async def start_case(request: StartCaseRequest):
    """Start a new case with introduction and objectives"""
    try:
        case_data = game_engine.start_case(request.case_id)
        return GameResponse(
            success=True,
            message="Case started successfully",
            data=case_data,
            game_state=game_engine.get_game_state(),
            points_earned=0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/call_witness", response_model=GameResponse)
async def call_witness(request: CallWitnessRequest):
    """Call a witness to the stand"""
    try:
        response = game_engine.call_witness(request.witness_name)
        if "error" in response:
            raise HTTPException(status_code=400, detail=response["error"])
        
        return GameResponse(
            success=True,
            message=f"Witness {request.witness_name} called to the stand",
            data=response,
            game_state=game_engine.get_game_state(),
            points_earned=response.get("points_earned", 0)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/question_witness", response_model=GameResponse)
async def question_witness(request: QuestionWitnessRequest):
    """Ask a question to the current witness"""
    try:
        response = game_engine.question_witness(request.question)
        if "error" in response:
            raise HTTPException(status_code=400, detail=response["error"])
        
        return GameResponse(
            success=True,
            message="Question processed",
            data=response,
            game_state=game_engine.get_game_state(),
            points_earned=response.get("points_earned", 0)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/use_evidence", response_model=GameResponse)
async def use_evidence(request: UseEvidenceRequest):
    """Present evidence to the court"""
    try:
        response = game_engine.use_evidence(request.evidence_id)
        if "error" in response:
            raise HTTPException(status_code=400, detail=response["error"])
        
        return GameResponse(
            success=True,
            message="Evidence presented",
            data=response,
            game_state=game_engine.get_game_state(),
            points_earned=response.get("points_earned", 0)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get_clue", response_model=GameResponse)
async def get_clue(request: GetClueRequest):
    """Get a hint/clue to help the player"""
    try:
        response = game_engine.get_clue()
        if "error" in response:
            raise HTTPException(status_code=400, detail=response["error"])
        
        return GameResponse(
            success=True,
            message="Clue revealed",
            data=response,
            game_state=game_engine.get_game_state(),
            points_earned=response.get("points_earned", 0)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/judge_chat", response_model=GameResponse)
async def judge_chat(request: JudgeChatRequest):
    """Chat directly with the judge for legal advice and points"""
    try:
        response = game_engine.chat_with_judge(request.statement)
        if "error" in response:
            raise HTTPException(status_code=400, detail=response["error"])
        
        return GameResponse(
            success=True,
            message="Judge responded",
            data=response,
            game_state=game_engine.get_game_state(),
            points_earned=response.get("points_earned", 0)
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
            data=verdict.dict(),
            game_state=game_engine.get_game_state(),
            points_earned=0
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

@app.get("/witnesses")
async def get_witnesses():
    """Get list of available witnesses"""
    try:
        case_data = game_engine.get_case_summary()
        if "error" in case_data:
            raise HTTPException(status_code=400, detail=case_data["error"])
        
        return {"witnesses": case_data.get("witnesses", [])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/evidence")
async def get_evidence():
    """Get list of available evidence"""
    try:
        case_data = game_engine.get_case_summary()
        if "error" in case_data:
            raise HTTPException(status_code=400, detail=case_data["error"])
        
        # Get detailed evidence information
        current_case = game_engine.current_case
        if current_case:
            evidence_list = []
            for evidence in current_case.evidence:
                evidence_list.append({
                    "id": evidence.id,
                    "name": evidence.name,
                    "description": evidence.description,
                    "presented": evidence.presented,
                    "points_value": evidence.points_value
                })
            return {"evidence": evidence_list}
        
        return {"evidence": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 