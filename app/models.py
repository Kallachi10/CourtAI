from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from datetime import datetime

class GamePhase(str, Enum):
    OPENING = "opening"
    WITNESS_EXAMINATION = "witness_examination"
    CROSS_EXAMINATION = "cross_examination"
    CLOSING = "closing"
    VERDICT = "verdict"

class ActionType(str, Enum):
    QUESTION = "question"
    EVIDENCE = "evidence"
    OBJECTION = "objection"
    CLOSING = "closing"

class Witness(BaseModel):
    name: str
    role: str
    personality: str
    testimony: List[str]
    credibility: float
    is_hostile: bool = False

class Evidence(BaseModel):
    id: str
    name: str
    description: str
    relevance: float
    admissibility: bool
    presented: bool = False
    category: str  # "physical", "testimonial", "documentary"

class Clue(BaseModel):
    id: str
    description: str
    discovered: bool = False
    relevance_score: float
    category: str  # "timeline", "motive", "opportunity", "alibi"

class LegalRule(BaseModel):
    id: str
    name: str
    description: str
    category: str  # "evidence", "procedure", "objection"
    relevance_score: float

class GameState(BaseModel):
    case_id: str
    phase: GamePhase
    current_turn: int
    max_turns: int
    player_score: float
    witnesses_examined: List[str]
    evidence_presented: List[str]
    clues_discovered: List[str]
    objections_raised: List[str]
    judge_notes: List[str]
    case_summary: str
    time_remaining: Optional[int] = None

class PlayerAction(BaseModel):
    action_type: ActionType
    target: Optional[str] = None
    content: str
    timestamp: datetime

class GameResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    game_state: GameState

class CaseData(BaseModel):
    case_id: str
    title: str
    description: str
    charges: List[str]
    witnesses: List[Witness]
    evidence: List[Evidence]
    clues: List[Clue]
    legal_rules: List[LegalRule]
    background: str
    difficulty: str  # "easy", "medium", "hard"

class Verdict(BaseModel):
    guilty: bool
    reasoning: str
    evidence_weight: Dict[str, float]
    witness_credibility: Dict[str, float]
    player_performance: Dict[str, float]
    score: float

class AIResponse(BaseModel):
    speaker: str  # "judge", "witness_name", "prosecutor", "defense"
    content: str
    emotion: Optional[str] = None
    confidence: Optional[float] = None
    reveals_clue: Optional[bool] = False
    clue_id: Optional[str] = None 