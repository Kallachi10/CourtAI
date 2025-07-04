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
    LegalRule, AIResponse, Verdict, ActionType
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
        
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        
        # Load legal knowledge and case data into vector stores
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
            "Witness credibility can be attacked through impeachment evidence."
        ]
        
        self.vector_store_manager.add_legal_knowledge(legal_knowledge)
    
    def start_case(self, case_id: Optional[str] = None) -> CaseData:
        """Start a new case or load a specific case"""
        if case_id is None:
            case_id = random.choice(list(CASE_DATABASE.keys()))
        
        self.current_case = CASE_DATABASE[case_id]
        
        # Initialize game state
        self.game_state = GameState(
            case_id=case_id,
            phase=GamePhase.OPENING,
            current_turn=1,
            max_turns=20,
            player_score=0.0,
            witnesses_examined=[],
            evidence_presented=[],
            clues_discovered=[],
            objections_raised=[],
            judge_notes=[],
            case_summary=self.current_case.description,
            time_remaining=1200  # 20 minutes
        )
        
        # Add case-specific data to vector store
        self._add_case_to_vector_store()
        
        # Generate opening statement
        opening_statement = self._generate_opening_statement()
        
        return {
            "case_data": self.current_case,
            "opening_statement": opening_statement,
            "game_state": self.game_state
        }
    
    def _add_case_to_vector_store(self):
        """Add case-specific clues and evidence to vector store"""
        case_texts = []
        
        # Add witness testimonies
        for witness in self.current_case.witnesses:
            case_texts.append(f"Witness {witness.name}: {witness.role} - {witness.personality}")
            for testimony in witness.testimony:
                case_texts.append(f"{witness.name} testimony: {testimony}")
        
        # Add evidence descriptions
        for evidence in self.current_case.evidence:
            case_texts.append(f"Evidence {evidence.id}: {evidence.name} - {evidence.description}")
        
        # Add clues
        for clue in self.current_case.clues:
            case_texts.append(f"Clue {clue.id}: {clue.description}")
        
        self.vector_store_manager.add_case_data(case_texts, self.current_case.case_id)
    
    def _generate_opening_statement(self) -> str:
        """Generate an opening statement for the case"""
        prompt = PromptTemplate(
            input_variables=["case_title", "case_description", "charges"],
            template="""
            You are a judge presiding over a criminal trial. Generate a brief opening statement 
            that introduces the case to the jury.
            
            Case: {case_title}
            Description: {case_description}
            Charges: {charges}
            
            Provide a neutral, professional opening statement that sets the stage for the trial.
            """
        )
        
        formatted_prompt = prompt.format(
            case_title=self.current_case.title,
            case_description=self.current_case.description,
            charges=", ".join(self.current_case.charges)
        )
        
        response = self.groq_client.invoke([HumanMessage(content=formatted_prompt)])
        return response.content
    
    def ask_question(self, question: str, witness_name: str) -> Dict[str, Any]:
        """Ask a question to a specific witness"""
        # Find the witness
        witness = next((w for w in self.current_case.witnesses if w.name.lower() == witness_name.lower()), None)
        if not witness:
            raise ValueError(f"Witness {witness_name} not found")
        
        # Retrieve relevant context
        context = self._retrieve_relevant_context(question, witness_name)
        
        # Generate witness response
        response = self._generate_witness_response(question, witness, context)
        
        # Update game state
        if witness_name not in self.game_state.witnesses_examined:
            self.game_state.witnesses_examined.append(witness_name)
        
        self.game_state.current_turn += 1
        
        return {
            "witness_response": response,
            "witness_credibility": witness.credibility,
            "clues_revealed": response.reveals_clue,
            "clue_id": response.clue_id
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
                "testimony": witness.testimony
            }
        return {}
    
    def _generate_witness_response(self, question: str, witness: Witness, context: Dict[str, Any]) -> AIResponse:
        """Generate a realistic witness response using AI"""
        prompt = PromptTemplate(
            input_variables=["witness_name", "witness_role", "witness_personality", "question", "legal_context", "case_context"],
            template="""
            You are {witness_name}, a {witness_role} in a criminal trial. Your personality is: {witness_personality}
            
            The player asks: "{question}"
            
            Legal context: {legal_context}
            Case context: {case_context}
            
            Respond as the witness would naturally speak. Be consistent with your personality and role.
            Don't reveal everything at once - be realistic about what you would know and say.
            If you reveal a clue, mention it naturally in your response.
            
            Respond in first person as the witness:
            """
        )
        
        formatted_prompt = prompt.format(
            witness_name=witness.name,
            witness_role=witness.role,
            witness_personality=witness.personality,
            question=question,
            legal_context="\n".join(context["legal_rules"]),
            case_context="\n".join(context["case_context"])
        )
        
        response = self.groq_client.invoke([HumanMessage(content=formatted_prompt)])
        
        # Determine if a clue is revealed
        reveals_clue = random.random() < 0.3  # 30% chance
        clue_id = None
        if reveals_clue and self.current_case.clues:
            undiscovered_clues = [c for c in self.current_case.clues if not c.discovered]
            if undiscovered_clues:
                clue = random.choice(undiscovered_clues)
                clue.discovered = True
                clue_id = clue.id
                self.game_state.clues_discovered.append(clue_id)
        
        return AIResponse(
            speaker=witness.name,
            content=response.content,
            emotion=self._determine_emotion(witness.personality),
            confidence=witness.credibility,
            reveals_clue=reveals_clue,
            clue_id=clue_id
        )
    
    def _determine_emotion(self, personality: str) -> str:
        """Determine the emotional state based on personality"""
        emotions = {
            "nervous": ["anxious", "worried", "fearful"],
            "confident": ["assured", "certain", "bold"],
            "hostile": ["angry", "defensive", "aggressive"],
            "cooperative": ["helpful", "willing", "friendly"],
            "evasive": ["cautious", "hesitant", "unclear"]
        }
        
        for trait, emotion_list in emotions.items():
            if trait in personality.lower():
                return random.choice(emotion_list)
        
        return "neutral"
    
    def present_evidence(self, evidence_id: str, description: str) -> Dict[str, Any]:
        """Present evidence to the court"""
        evidence = next((e for e in self.current_case.evidence if e.id == evidence_id), None)
        if not evidence:
            raise ValueError(f"Evidence {evidence_id} not found")
        
        # Generate judge's response to evidence
        judge_response = self._generate_judge_response(evidence, description)
        
        # Update game state
        if evidence_id not in self.game_state.evidence_presented:
            self.game_state.evidence_presented.append(evidence_id)
            evidence.presented = True
        
        self.game_state.current_turn += 1
        
        return {
            "judge_response": judge_response,
            "evidence_admitted": evidence.admissibility,
            "relevance_score": evidence.relevance
        }
    
    def _generate_judge_response(self, evidence: Evidence, description: str) -> AIResponse:
        """Generate judge's response to presented evidence"""
        prompt = PromptTemplate(
            input_variables=["evidence_name", "evidence_description", "player_description", "admissibility"],
            template="""
            You are a judge presiding over a criminal trial. The defense attorney is presenting evidence.
            
            Evidence: {evidence_name}
            Evidence description: {evidence_description}
            Attorney's presentation: {player_description}
            Admissibility: {admissibility}
            
            Respond as the judge would, considering admissibility, relevance, and proper procedure.
            Be professional and authoritative.
            """
        )
        
        formatted_prompt = prompt.format(
            evidence_name=evidence.name,
            evidence_description=evidence.description,
            player_description=description,
            admissibility="Admissible" if evidence.admissibility else "Inadmissible"
        )
        
        response = self.groq_client.invoke([HumanMessage(content=formatted_prompt)])
        
        return AIResponse(
            speaker="Judge",
            content=response.content,
            emotion="authoritative",
            confidence=0.9
        )
    
    def next_turn(self, action_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Process the next turn in the game"""
        if action_type == ActionType.QUESTION:
            return self.ask_question(details["question"], details["witness_name"])
        elif action_type == ActionType.EVIDENCE:
            return self.present_evidence(details["evidence_id"], details["description"])
        elif action_type == ActionType.OBJECTION:
            return self._handle_objection(details)
        elif action_type == ActionType.CLOSING:
            return self._handle_closing_argument(details)
        else:
            raise ValueError(f"Unknown action type: {action_type}")
    
    def _handle_objection(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Handle player objections"""
        objection_type = details.get("objection_type", "general")
        reason = details.get("reason", "")
        
        # Generate judge's ruling on objection
        prompt = PromptTemplate(
            input_variables=["objection_type", "reason"],
            template="""
            You are a judge ruling on an objection in a criminal trial.
            
            Objection type: {objection_type}
            Attorney's reason: {reason}
            
            Provide a brief ruling on the objection. Be decisive and cite relevant legal principles.
            """
        )
        
        formatted_prompt = prompt.format(
            objection_type=objection_type,
            reason=reason
        )
        
        response = self.groq_client.invoke([HumanMessage(content=formatted_prompt)])
        
        # Update game state
        self.game_state.objections_raised.append(f"{objection_type}: {reason}")
        self.game_state.current_turn += 1
        
        return {
            "judge_ruling": response.content,
            "objection_sustained": "sustained" in response.content.lower()
        }
    
    def _handle_closing_argument(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Handle player's closing argument"""
        argument = details.get("argument", "")
        
        # Generate judge's response to closing argument
        prompt = PromptTemplate(
            input_variables=["argument", "case_summary"],
            template="""
            You are a judge listening to closing arguments in a criminal trial.
            
            Attorney's closing argument: {argument}
            Case summary: {case_summary}
            
            Provide a brief response acknowledging the closing argument and setting up for deliberation.
            """
        )
        
        formatted_prompt = prompt.format(
            argument=argument,
            case_summary=self.game_state.case_summary
        )
        
        response = self.groq_client.invoke([HumanMessage(content=formatted_prompt)])
        
        # Move to verdict phase
        self.game_state.phase = GamePhase.VERDICT
        
        return {
            "judge_response": response.content,
            "phase": "verdict"
        }
    
    def get_verdict(self) -> Verdict:
        """Generate the final verdict"""
        if self.game_state.phase != GamePhase.VERDICT:
            raise ValueError("Case must be in verdict phase to get verdict")
        
        # Calculate evidence weight and witness credibility
        evidence_weight = {}
        witness_credibility = {}
        
        for evidence in self.current_case.evidence:
            if evidence.presented:
                evidence_weight[evidence.id] = evidence.relevance
        
        for witness in self.current_case.witnesses:
            if witness.name in self.game_state.witnesses_examined:
                witness_credibility[witness.name] = witness.credibility
        
        # Generate verdict reasoning
        prompt = PromptTemplate(
            input_variables=["case_summary", "evidence_weight", "witness_credibility", "clues_discovered"],
            template="""
            You are a judge delivering a verdict in a criminal trial.
            
            Case summary: {case_summary}
            Evidence presented: {evidence_weight}
            Witness credibility: {witness_credibility}
            Clues discovered: {clues_discovered}
            
            Based on the evidence and testimony, deliver a reasoned verdict (guilty or not guilty)
            with detailed reasoning. Consider the burden of proof and reasonable doubt.
            """
        )
        
        formatted_prompt = prompt.format(
            case_summary=self.game_state.case_summary,
            evidence_weight=str(evidence_weight),
            witness_credibility=str(witness_credibility),
            clues_discovered=str(self.game_state.clues_discovered)
        )
        
        response = self.groq_client.invoke([HumanMessage(content=formatted_prompt)])
        
        # Determine guilty verdict (simplified logic)
        guilty = len(self.game_state.evidence_presented) > 3 and len(self.game_state.clues_discovered) > 2
        
        # Calculate player performance score
        performance_score = self._calculate_performance_score()
        
        return Verdict(
            guilty=guilty,
            reasoning=response.content,
            evidence_weight=evidence_weight,
            witness_credibility=witness_credibility,
            player_performance={
                "evidence_presented": len(self.game_state.evidence_presented),
                "witnesses_examined": len(self.game_state.witnesses_examined),
                "clues_discovered": len(self.game_state.clues_discovered),
                "objections_raised": len(self.game_state.objections_raised)
            },
            score=performance_score
        )
    
    def _calculate_performance_score(self) -> float:
        """Calculate player performance score"""
        score = 0.0
        
        # Base score for actions taken
        score += len(self.game_state.evidence_presented) * 10
        score += len(self.game_state.witnesses_examined) * 15
        score += len(self.game_state.clues_discovered) * 20
        score += len(self.game_state.objections_raised) * 5
        
        # Bonus for efficiency (fewer turns used)
        efficiency_bonus = max(0, (self.game_state.max_turns - self.game_state.current_turn) * 2)
        score += efficiency_bonus
        
        return min(100.0, score)
    
    def get_game_state(self) -> GameState:
        """Get current game state"""
        return self.game_state
    
    def get_available_actions(self) -> List[str]:
        """Get available actions for the current turn"""
        actions = []
        
        if self.game_state.phase == GamePhase.OPENING:
            actions.extend(["examine_witness", "present_evidence"])
        elif self.game_state.phase == GamePhase.WITNESS_EXAMINATION:
            actions.extend(["ask_question", "present_evidence", "raise_objection"])
        elif self.game_state.phase == GamePhase.CROSS_EXAMINATION:
            actions.extend(["cross_examine", "present_evidence", "raise_objection"])
        elif self.game_state.phase == GamePhase.CLOSING:
            actions.append("closing_argument")
        
        return actions
    
    def get_case_summary(self) -> Dict[str, Any]:
        """Get a summary of the current case"""
        if not self.current_case:
            return {"error": "No case loaded"}
        
        return {
            "case_id": self.current_case.case_id,
            "title": self.current_case.title,
            "description": self.current_case.description,
            "charges": self.current_case.charges,
            "witnesses": [w.name for w in self.current_case.witnesses],
            "evidence": [e.name for e in self.current_case.evidence],
            "clues": [c.description for c in self.current_case.clues if c.discovered],
            "game_state": self.game_state.dict()
        } 