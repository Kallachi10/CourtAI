import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import random
from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

from models import (
    GameState, GamePhase, CaseData, Witness, Evidence, Clue, 
    LegalRule, AIResponse, Verdict, ActionType, CaseObjective
)
from vector_store import VectorStoreManager
from case_data import CASE_DATABASE

class CourtroomGameEngine:
    def __init__(self):
        self.groq_client = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="meta-llama/llama-4-scout-17b-16e-instruct"
        )
        
        self.vector_store_manager = VectorStoreManager()
        self.current_case: Optional[CaseData] = None
        self.game_state: Optional[GameState] = None
        self.conversation_history: List[Dict[str, Any]] = []
        
        
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
       
        self._initialize_vector_stores()
    
    def _initialize_vector_stores(self):
        """Initialize vector stores with legal knowledge and case data"""
        # Legal knowledge base
        legal_knowledge = [
            "Hearsay evidence is generally inadmissible unless it falls under an exception.",
            "Objections must be timely and specific to preserve the record.",
            "The burden of proof in criminal cases is beyond a reasonable doubt.",
            "Leading questions are generally not allowed on direct examination.",
            "Character evidence is limited to specific instances of conduct.",
            "Expert witnesses must be qualified to testify on their area of expertise.",
            "The prosecution must prove all elements of the crime charged.",
            "Defense attorneys can cross-examine prosecution witnesses.",
            "Physical evidence must be properly authenticated before admission.",
            "Witness credibility can be attacked through impeachment evidence.",
            "Reasonable doubt exists when there are multiple possible explanations for the evidence.",
            "Circumstantial evidence can be sufficient for conviction if it excludes all reasonable doubt."
        ]
        
        self.vector_store_manager.add_legal_knowledge(legal_knowledge)
    
    def start_case(self, case_id: Optional[str] = None) -> Dict[str, Any]:
        """Start a new case with introduction and objectives"""
        if case_id is None:
            case_id = random.choice(list(CASE_DATABASE.keys()))
        
        self.current_case = CASE_DATABASE[case_id]
        
        # Initialize game state
        self.game_state = GameState(
            case_id=case_id,
            phase=GamePhase.CASE_INTRO,
            current_step=0,
            max_steps=self.current_case.objective.max_steps,
            player_score=0.0,
            witnesses_examined=[],
            evidence_presented=[],
            clues_discovered=[],
            objections_raised=[],
            judge_notes=[],
            case_summary=self.current_case.description,
            time_remaining=1200,  
            current_witness=None,
            available_actions=["call_witness", "use_evidence", "get_clue"]
        )
        
        
        self._add_case_to_vector_store()
        
        return {
            "case_data": self.current_case,
            "objective": self.current_case.objective,
            "game_state": self.game_state,
            "available_actions": self.game_state.available_actions
        }
    
    def _add_case_to_vector_store(self):
        """Add case-specific clues and evidence to vector store"""
        case_texts = []
        
        # Add witness testimonies
        for witness in self.current_case.witnesses:
            case_texts.append(f"Witness {witness.name}: {witness.role} - {witness.personality}")
            for testimony in witness.testimony:
                case_texts.append(f"{witness.name} testimony: {testimony}")
            for info in witness.key_information:
                case_texts.append(f"{witness.name} key info: {info}")
            for weakness in witness.weaknesses:
                case_texts.append(f"{witness.name} weakness: {weakness}")
        
        # Add evidence descriptions
        for evidence in self.current_case.evidence:
            case_texts.append(f"Evidence {evidence.id}: {evidence.name} - {evidence.description}")
        
        # Add clues
        for clue in self.current_case.clues:
            case_texts.append(f"Clue {clue.id}: {clue.description}")
        
        self.vector_store_manager.add_case_data(case_texts, self.current_case.case_id)
    
    def call_witness(self, witness_name: str) -> Dict[str, Any]:
        """Call a witness to the stand"""
        if self.game_state.current_step >= self.game_state.max_steps:
            return {"error": "Maximum steps reached. Game over."}
        
        # Find the witness
        witness = next((w for w in self.current_case.witnesses if w.name.lower() == witness_name.lower()), None)
        if not witness:
            raise ValueError(f"Witness {witness_name} not found")
        
        # Update game state
        self.game_state.current_witness = witness_name
        self.game_state.phase = GamePhase.WITNESS_EXAMINATION
        self.game_state.current_step += 1
        self.game_state.available_actions = ["question_witness", "use_evidence", "get_clue"]
        
        # Generate witness introduction
        introduction = self._generate_witness_introduction(witness)
        
        # Award points and update score
        points_earned = 5
        self.game_state.player_score += points_earned
        
        return {
            "witness": witness,
            "introduction": introduction,
            "game_state": self.game_state,
            "points_earned": points_earned
        }
    
    def _generate_witness_introduction(self, witness: Witness) -> str:
        """Generate a witness introduction"""
        prompt = PromptTemplate(
            input_variables=["witness_name", "witness_role", "witness_personality"],
            template="""
            You are a court clerk introducing a witness to the stand.
            
            Witness: {witness_name}
            Role: {witness_role}
            Personality: {witness_personality}
            
            Provide a brief, professional introduction of the witness to the court.
            """
        )
        
        formatted_prompt = prompt.format(
            witness_name=witness.name,
            witness_role=witness.role,
            witness_personality=witness.personality
        )
        
        response = self.groq_client.invoke([HumanMessage(content=formatted_prompt)])
        return response.content
    
    def question_witness(self, question: str) -> Dict[str, Any]:
        """Ask a question to the current witness"""
        if not self.game_state.current_witness:
            return {"error": "No witness on the stand. Call a witness first."}
        
        if self.game_state.current_step >= self.game_state.max_steps:
            return {"error": "Maximum steps reached. Game over."}
        
        # Find the current witness
        witness = next((w for w in self.current_case.witnesses if w.name.lower() == self.game_state.current_witness.lower()), None)
        if not witness:
            raise ValueError(f"Current witness not found")
        
        # Retrieve relevant context
        context = self._retrieve_relevant_context(question, witness.name)
        
        # Generate witness response
        response = self._generate_witness_response(question, witness, context)
        
        # Update game state
        if witness.name not in self.game_state.witnesses_examined:
            self.game_state.witnesses_examined.append(witness.name)
        
        self.game_state.current_step += 1
        
        # Award points based on question quality
        points_earned = self._calculate_question_points(question, response, context)
        self.game_state.player_score += points_earned
        
        return {
            "witness_response": response,
            "witness_credibility": witness.credibility,
            "clues_revealed": response.reveals_clue,
            "clue_id": response.clue_id,
            "points_earned": points_earned,
            "game_state": self.game_state
        }
    
    def _calculate_question_points(self, question: str, response: AIResponse, context: Dict[str, Any]) -> int:
        """Calculate points earned for a good question"""
        points = 5  # Base points for asking a question
        
        # Bonus for strategic questions
        if any(keyword in question.lower() for keyword in ["alibi", "timeline", "opportunity", "reasonable doubt"]):
            points += 10
        
        # Bonus for questions that reveal clues
        if response.reveals_clue:
            points += 15
        
        # Bonus for questions that challenge witness credibility
        if any(weakness in question.lower() for weakness in context.get("witness_info", {}).get("weaknesses", [])):
            points += 10
        
        return points
    
    def use_evidence(self, evidence_id: str) -> Dict[str, Any]:
        """Present evidence to the court"""
        if self.game_state.current_step >= self.game_state.max_steps:
            return {"error": "Maximum steps reached. Game over."}
        
        # Find the evidence
        evidence = next((e for e in self.current_case.evidence if e.id == evidence_id), None)
        if not evidence:
            raise ValueError(f"Evidence {evidence_id} not found")
        
        if evidence.presented:
            return {"error": "Evidence already presented"}
        
        # Update game state
        evidence.presented = True
        self.game_state.evidence_presented.append(evidence_id)
        self.game_state.current_step += 1
        
        # Generate judge's response
        judge_response = self._generate_judge_response(evidence)
        
        # Award points and update score
        points_earned = evidence.points_value
        self.game_state.player_score += points_earned
        
        return {
            "evidence": evidence,
            "judge_response": judge_response,
            "points_earned": points_earned,
            "game_state": self.game_state
        }
    
    def get_clue(self) -> Dict[str, Any]:
        """Get a hint/clue to help the player"""
        if self.game_state.current_step >= self.game_state.max_steps:
            return {"error": "Maximum steps reached. Game over."}
        
        # Find undiscovered clues
        undiscovered_clues = [c for c in self.current_case.clues if not c.discovered]
        if not undiscovered_clues:
            return {"error": "No more clues available"}
        
        # Select the most relevant undiscovered clue
        clue = max(undiscovered_clues, key=lambda c: c.relevance_score)
        clue.discovered = True
        
        # Update game state
        self.game_state.clues_discovered.append(clue.id)
        self.game_state.current_step += 1
        
        # Award points and update score
        points_earned = clue.points_value
        self.game_state.player_score += points_earned
        
        return {
            "clue": clue,
            "points_earned": points_earned,
            "game_state": self.game_state
        }
    
    def _retrieve_relevant_context(self, question: str, witness_name: str) -> Dict[str, Any]:
        """Retrieve relevant legal rules and case context"""
        # Get legal context
        legal_context = self.vector_store_manager.search_legal_knowledge(question, k=3)
        
        # Get case-specific context
        case_context = self.vector_store_manager.search_case_data(
            f"{witness_name} {question}", k=5
        )
        
        return {
            "legal_rules": legal_context,
            "case_context": case_context,
            "witness_info": self._get_witness_info(witness_name)
        }
    
    def _get_witness_info(self, witness_name: str) -> Dict[str, Any]:
        """Get detailed information about a witness"""
        witness = next((w for w in self.current_case.witnesses if w.name.lower() == witness_name.lower()), None)
        if witness:
            return {
                "name": witness.name,
                "role": witness.role,
                "personality": witness.personality,
                "credibility": witness.credibility,
                "is_hostile": witness.is_hostile,
                "testimony": witness.testimony,
                "key_information": witness.key_information,
                "weaknesses": witness.weaknesses
            }
        return {}
    
    def _generate_witness_response(self, question: str, witness: Witness, context: Dict[str, Any]) -> AIResponse:
        """Generate a realistic witness response using AI"""
        prompt = PromptTemplate(
            input_variables=["witness_name", "witness_role", "witness_personality", "witness_testimony", "question", "legal_context", "case_context"],
            template="""
            You are {witness_name}, a witness in a criminal trial.
            
            Your role: {witness_role}
            Your personality: {witness_personality}
            Your testimony: {witness_testimony}
            
            Question from the attorney: {question}
            
            Legal context: {legal_context}
            Case context: {case_context}
            
            Respond as this witness would, considering their personality and role. Be realistic and consistent with their testimony. If the question reveals important information that could help the case, indicate this subtly.
            """
        )
        
        formatted_prompt = prompt.format(
            witness_name=witness.name,
            witness_role=witness.role,
            witness_personality=witness.personality,
            witness_testimony="; ".join(witness.testimony),
            question=question,
            legal_context=str(context.get("legal_rules", [])),
            case_context=str(context.get("case_context", []))
        )
        
        response = self.groq_client.invoke([HumanMessage(content=formatted_prompt)])
        
        # Check if response reveals a clue
        clue_revealed = self._check_clue_revelation(question, response.content)
        
        return AIResponse(
            speaker=witness.name,
            content=response.content,
            emotion=self._determine_emotion(witness.personality),
            confidence=witness.credibility,
            reveals_clue=clue_revealed["reveals"],
            clue_id=clue_revealed["clue_id"],
            points_awarded=10 if clue_revealed["reveals"] else 5
        )
    
    def _check_clue_revelation(self, question: str, response: str) -> Dict[str, Any]:
        """Check if the response reveals a clue"""
        # Simple keyword-based clue detection
        clue_keywords = {
            "C1": ["unlocked", "kitchen door", "access"],
            "C2": ["thompson", "hurrying", "8:55", "bag"],
            "C3": ["glove", "size 9", "size 11", "hand size"],
            "C4": ["security guard", "away", "10 minutes", "post"]
        }
        
        for clue_id, keywords in clue_keywords.items():
            if any(keyword.lower() in response.lower() for keyword in keywords):
                return {"reveals": True, "clue_id": clue_id}
        
        return {"reveals": False, "clue_id": None}
    
    def _determine_emotion(self, personality: str) -> str:
        """Determine witness emotion based on personality"""
        if "nervous" in personality.lower():
            return "anxious"
        elif "confident" in personality.lower():
            return "confident"
        elif "defensive" in personality.lower():
            return "defensive"
        elif "methodical" in personality.lower():
            return "calm"
        else:
            return "neutral"
    
    def _generate_judge_response(self, evidence: Evidence) -> AIResponse:
        """Generate judge's response to evidence presentation"""
        prompt = PromptTemplate(
            input_variables=["evidence_name", "evidence_description", "evidence_relevance"],
            template="""
            You are a judge presiding over a criminal trial. The defense attorney has presented evidence.
            
            Evidence: {evidence_name}
            Description: {evidence_description}
            Relevance: {evidence_relevance}
            
            Provide a brief response acknowledging the evidence and its admissibility. Be judicial and neutral.
            """
        )
        
        formatted_prompt = prompt.format(
            evidence_name=evidence.name,
            evidence_description=evidence.description,
            evidence_relevance=evidence.relevance
        )
        
        response = self.groq_client.invoke([HumanMessage(content=formatted_prompt)])
        
        return AIResponse(
            speaker="Judge",
            content=response.content,
            emotion="authoritative",
            confidence=0.9
        )
    
    def get_verdict(self) -> Verdict:
        """Generate the final verdict"""
        if not self.game_state or not self.current_case:
            raise ValueError("No active case or game state")
            
        if self.game_state.current_step < self.game_state.max_steps:
            # If game hasn't reached max steps, force it to end
            self.game_state.current_step = self.game_state.max_steps
        
        # Calculate evidence weight and witness credibility
        evidence_weight = {}
        witness_credibility = {}
        
        for evidence in self.current_case.evidence:
            if evidence.presented:
                evidence_weight[evidence.id] = evidence.relevance
        
        for witness in self.current_case.witnesses:
            if witness.name in self.game_state.witnesses_examined:
                witness_credibility[witness.name] = witness.credibility
        
        # Check win conditions
        won_case = self._check_win_conditions()
        
        # Generate verdict reasoning
        prompt = PromptTemplate(
            input_variables=["case_summary", "evidence_weight", "witness_credibility", "clues_discovered", "player_score", "won_case"],
            template="""
            You are a judge delivering a verdict in a criminal trial.
            
            Case summary: {case_summary}
            Evidence presented: {evidence_weight}
            Witness credibility: {witness_credibility}
            Clues discovered: {clues_discovered}
            Player performance score: {player_score}
            Defense won: {won_case}
            
            Based on the evidence and the defense attorney's performance, deliver a reasoned verdict (guilty or not guilty)
            with detailed reasoning. Consider the burden of proof and reasonable doubt.
            """
        )
        
        formatted_prompt = prompt.format(
            case_summary=self.game_state.case_summary,
            evidence_weight=str(evidence_weight),
            witness_credibility=str(witness_credibility),
            clues_discovered=str(self.game_state.clues_discovered),
            player_score=self.game_state.player_score,
            won_case=won_case
        )
        
        try:
            response = self.groq_client.invoke([HumanMessage(content=formatted_prompt)])
            reasoning = response.content
        except Exception as e:
            # Fallback reasoning if AI call fails
            reasoning = f"Based on the evidence presented and the defense attorney's performance (score: {self.game_state.player_score}), the court finds the defendant {'NOT GUILTY' if won_case else 'GUILTY'}."
        
        # Determine guilty verdict based on win conditions
        guilty = not won_case
        
        return Verdict(
            guilty=guilty,
            reasoning=reasoning,
            evidence_weight=evidence_weight,
            witness_credibility=witness_credibility,
            player_performance={
                "evidence_presented": len(self.game_state.evidence_presented),
                "witnesses_examined": len(self.game_state.witnesses_examined),
                "clues_discovered": len(self.game_state.clues_discovered),
                "objections_raised": len(self.game_state.objections_raised)
            },
            score=self.game_state.player_score,
            won_case=won_case
        )
    
    def _check_win_conditions(self) -> bool:
        """Check if the player meets all win conditions"""
        objective = self.current_case.objective
        
        # Check score requirement
        if self.game_state.player_score < objective.target_score:
            return False
        
        # Check clues discovered
        if len(self.game_state.clues_discovered) < 3:
            return False
        
        # Check evidence presented
        if len(self.game_state.evidence_presented) < 2:
            return False
        
        # Check witnesses examined
        if len(self.game_state.witnesses_examined) < 2:
            return False
        
        return True
    
    def get_game_state(self) -> GameState:
        """Get current game state"""
        return self.game_state
    
    def get_available_actions(self) -> List[str]:
        """Get available actions for the current turn"""
        return self.game_state.available_actions
    
    def get_case_summary(self) -> Dict[str, Any]:
        """Get a summary of the current case"""
        if not self.current_case:
            return {"error": "No case loaded"}
        
        return {
            "case_id": self.current_case.case_id,
            "title": self.current_case.title,
            "description": self.current_case.description,
            "charges": self.current_case.charges,
            "objective": self.current_case.objective,
            "witnesses": [w.name for w in self.current_case.witnesses],
            "evidence": [e.name for e in self.current_case.evidence],
            "clues": [c.description for c in self.current_case.clues if c.discovered],
            "game_state": self.game_state.dict()
        }
    
    def chat_with_judge(self, statement: str) -> Dict[str, Any]:
        """Chat directly with the judge for legal advice and points"""
        if self.game_state.current_step >= self.game_state.max_steps:
            return {"error": "Maximum steps reached. Game over."}
        
        # Generate judge's response and evaluate statement
        judge_response = self._generate_judge_chat_response(statement)
        
        # Calculate points for valid legal statements
        points_earned = self._evaluate_legal_statement(statement)
        
        # Update game state
        self.game_state.current_step += 1
        self.game_state.player_score += points_earned
        
        return {
            "judge_response": judge_response,
            "points_earned": points_earned,
            "game_state": self.game_state
        }
    
    def _generate_judge_chat_response(self, statement: str) -> AIResponse:
        """Generate judge's response to legal statements"""
        prompt = PromptTemplate(
            input_variables=["statement", "case_context"],
            template="""
            You are a judge in a criminal trial. A defense attorney is making a legal statement to you.
            
            Attorney's statement: {statement}
            Case context: {case_context}
            
            Provide a brief, judicial response. Be authoritative but helpful. If the statement shows good legal understanding, acknowledge it. If it's incorrect, gently correct it.
            """
        )
        
        formatted_prompt = prompt.format(
            statement=statement,
            case_context=self.game_state.case_summary
        )
        
        response = self.groq_client.invoke([HumanMessage(content=formatted_prompt)])
        
        return AIResponse(
            speaker="Judge",
            content=response.content,
            emotion="authoritative",
            confidence=0.9
        )
    
    def _evaluate_legal_statement(self, statement: str) -> int:
        """Evaluate legal statement and award points"""
        points = 0
        
        # Legal keywords that indicate good understanding
        legal_keywords = [
            "reasonable doubt", "burden of proof", "alibi", "evidence", 
            "witness credibility", "circumstantial evidence", "opportunity",
            "motive", "timeline", "objection", "hearsay", "admissible",
            "cross-examination", "direct examination", "impeachment"
        ]
        
        # Case-specific keywords
        case_keywords = [
            "carlos rivera", "necklace", "theft", "gala", "kitchen",
            "security footage", "glove", "thompson", "unlocked door"
        ]
        
        # Award points for legal knowledge
        for keyword in legal_keywords:
            if keyword.lower() in statement.lower():
                points += 5
        
        # Award points for case-specific knowledge
        for keyword in case_keywords:
            if keyword.lower() in statement.lower():
                points += 3
        
        # Bonus for strategic thinking
        if any(phrase in statement.lower() for phrase in [
            "reasonable doubt", "prove innocence", "alternative suspect",
            "lack of evidence", "timeline inconsistency"
        ]):
            points += 10
        
        # Cap points to prevent abuse
        return min(points, 25) 