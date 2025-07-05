from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from datetime import datetime

class GamePhase(str, Enum):
    CASE_INTRO = "case_intro"
    WITNESS_EXAMINATION = "witness_examination"
    EVIDENCE_PRESENTATION = "evidence_presentation"
    CLOSING = "closing"
    VERDICT = "verdict"

class ActionType(str, Enum):
    CALL_WITNESS = "call_witness"
    QUESTION_WITNESS = "question_witness"
    USE_EVIDENCE = "use_evidence"
    GET_CLUE = "get_clue"
    CLOSING_ARGUMENT = "closing_argument"

class Witness(BaseModel):
    name: str
    role: str
    personality: str
    testimony: List[str]
    credibility: float
    is_hostile: bool = False
    key_information: List[str]  # Important facts this witness knows
    weaknesses: List[str]  # Areas where witness can be challenged

class Evidence(BaseModel):
    id: str
    name: str
    description: str
    relevance: float
    admissibility: bool
    presented: bool = False
    category: str  # "physical", "testimonial", "documentary"
    clue_hint: str  # Hint provided when "Get Clue" is used
    points_value: int  # Points awarded for using this evidence effectively

class Clue(BaseModel):
    id: str
    description: str
    discovered: bool = False
    relevance_score: float
    category: str  # "timeline", "motive", "opportunity", "alibi"
    points_value: int  # Points awarded for discovering this clue

class LegalRule(BaseModel):
    id: str
    name: str
    description: str
    category: str  # "evidence", "procedure", "objection"
    relevance_score: float

class CaseObjective(BaseModel):
    title: str
    description: str
    lawyer_task: str  # What the lawyer needs to accomplish
    win_conditions: List[str]  # Conditions for winning
    max_steps: int  # Maximum number of actions allowed
    target_score: int  # Minimum score needed to win

class GameState(BaseModel):
    case_id: str
    phase: GamePhase
    current_step: int
    max_steps: int
    player_score: float
    witnesses_examined: List[str]
    evidence_presented: List[str]
    clues_discovered: List[str]
    objections_raised: List[str]
    judge_notes: List[str]
    case_summary: str
    time_remaining: Optional[int] = None
    current_witness: Optional[str] = None  # Currently on stand
    available_actions: List[str] = []

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
    points_earned: int = 0

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
    objective: CaseObjective

class Verdict(BaseModel):
    guilty: bool
    reasoning: str
    evidence_weight: Dict[str, float]
    witness_credibility: Dict[str, float]
    player_performance: Dict[str, float]
    score: float
    won_case: bool  # Whether the lawyer won their objective

class AIResponse(BaseModel):
    speaker: str  # "judge", "witness_name", "prosecutor", "defense"
    content: str
    emotion: Optional[str] = None
    confidence: Optional[float] = None
    reveals_clue: Optional[bool] = False
    clue_id: Optional[str] = None
    points_awarded: int = 0 