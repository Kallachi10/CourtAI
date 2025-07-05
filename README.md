# CourtroomAI: Legal Minds

An interactive AI-driven legal simulation game where players act as defense attorneys in criminal trials.

## Game Overview

CourtroomAI: Legal Minds is a structured, step-limited courtroom simulation game that teaches legal procedures while providing an engaging AI-powered experience.

### Game Features

- **Case Introduction**: Clear case description, lawyer tasks, and game rules
- **Witness Examination**: Call witnesses and ask strategic questions
- **Evidence Presentation**: Present evidence to support your case
- **Clue System**: Discover hidden clues to strengthen your defense
- **Step-Limited Gameplay**: Complete your case within a limited number of actions
- **Scoring System**: Earn points for good legal strategy
- **AI-Powered Responses**: Realistic witness and judge responses using Groq LLM

### Current Case: "The Missing Necklace"

You are defending Carlos Rivera, a caterer accused of stealing a $500,000 diamond necklace from a high-society gala. Your task is to create reasonable doubt and prove his innocence.

## Game Structure

### 1. Case Introduction
- Case description and background
- Your specific lawyer task
- Game rules and win conditions
- Maximum steps allowed (12)

### 2. Gameplay Actions
- **Call Witness**: Bring witnesses to the stand
- **Question Witness**: Ask strategic questions to reveal information
- **Use Evidence**: Present evidence to the court
- **Get Clue**: Receive hints to help your case

### 3. Win Conditions
- Score at least 80 points
- Discover at least 3 clues
- Present at least 2 pieces of evidence
- Question at least 2 witnesses

### 4. Scoring System
- Calling witnesses: 5 points
- Good questions: 5-25 points (based on strategy)
- Presenting evidence: 10-25 points (based on relevance)
- Discovering clues: 15-25 points (based on importance)

## Installation & Setup

### Prerequisites
- Python 3.8+
- Groq API key

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd CourtAI
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the root directory:
```
GROQ_API_KEY=your_groq_api_key_here
```

### Running the Game

1. Start the backend server:
```bash
# Option 1: Using the run script (recommended)
python run_server.py

# Option 2: Using the batch file (Windows)
run_server.bat

# Option 3: Manual method
cd app
python main.py
```

2. Open the frontend:
Open `frontend/index.html` in your web browser

3. Start playing:
- Click "Start Case" to begin
- Follow the case introduction and rules
- Use the action panels to call witnesses, present evidence, and get clues
- Try to win the case within the step limit!

## Game Controls

- **Witness Section**: Click on witnesses to call them to the stand
- **Evidence Section**: Click on evidence items to present them
- **Clue Section**: Click "Get Clue" to receive hints
- **Question Input**: Type questions when a witness is on the stand
- **Game Controls**: Get verdict or start a new case

## Technical Details

### Backend (Python/FastAPI)
- **Game Engine**: Manages game state and logic
- **AI Integration**: Uses Groq LLM for realistic responses
- **Vector Store**: Stores legal knowledge and case context
- **API Endpoints**: RESTful API for frontend communication

### Frontend (HTML/CSS/JavaScript)
- **Responsive Design**: Works on desktop and mobile
- **Real-time Updates**: Live game state and conversation
- **Interactive UI**: Click-based actions and real-time feedback

### AI Features
- **Witness Responses**: Contextual, personality-based responses
- **Judge Rulings**: Legal reasoning for evidence and objections
- **Verdict Generation**: Comprehensive case analysis
- **Clue Detection**: Intelligent clue revelation based on questions

## Game Strategy Tips

1. **Start with Witnesses**: Call key witnesses first to understand the case
2. **Ask Strategic Questions**: Focus on alibi, timeline, and opportunity
3. **Present Relevant Evidence**: Use evidence that supports reasonable doubt
4. **Use Clues Wisely**: Get clues when you're stuck or need direction
5. **Manage Your Steps**: Don't waste actions - plan your strategy

## Contributing

Feel free to contribute by:
- Adding new cases
- Improving the AI responses
- Enhancing the UI/UX
- Adding new game features

## License

This project is licensed under the MIT License.
