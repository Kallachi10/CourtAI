# CourtroomAI: Legal Minds

An interactive AI-driven legal simulation game where you play as a defense attorney.

## Features

### New UI Layout (Updated)
- **Main Chat Area**: Displays the current speaker's image and response in a prominent box
- **Speaker Display**: Shows the current speaker's image and their response text
- **Dropdown Sections**: All game elements are organized in collapsible dropdown sections:
  - **Chat History**: Complete conversation log
  - **Witnesses**: Available witnesses and questioning interface
  - **Evidence**: Evidence items that can be presented
  - **Chat to Judge**: Legal statements and judge communication
  - **Clues**: Discovered clues and clue discovery button

### Game Mechanics
- **Interactive Courtroom**: Real-time conversation with AI-powered witnesses and judge
- **Evidence System**: Present relevant evidence to build your case
- **Witness Examination**: Question witnesses to uncover the truth
- **Scoring System**: Earn points through strategic legal actions
- **Clue Discovery**: Uncover hidden clues to strengthen your defense

## How to Run

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Backend Server**:
   ```bash
   python run_server.py
   ```

3. **Open the Frontend**:
   - Navigate to `frontend/index.html` in your web browser
   - Or serve the frontend directory using a local server

## Game Flow

1. **Case Introduction**: Read the case details and understand your role
2. **Game Rules**: Review objectives and scoring system
3. **Courtroom Session**: 
   - Call witnesses and ask questions
   - Present evidence to the court
   - Make legal statements to the judge
   - Discover clues to strengthen your case
4. **Verdict**: Receive the final verdict based on your performance

## UI Features

### Speaker Display
- Large image area showing the current speaker
- Prominent text box displaying the speaker's response
- Automatic updates when different characters speak

### Dropdown Organization
- **Chat History**: Click to view complete conversation log
- **Witnesses**: Click to see available witnesses and call them to the stand
- **Evidence**: Click to view and present evidence items
- **Chat to Judge**: Click to make legal statements to the judge
- **Clues**: Click to view discovered clues and get new ones

### Responsive Design
- Works on desktop and mobile devices
- Collapsible sidebar on smaller screens
- Touch-friendly interface

## Scoring System

- **Calling Witnesses**: 5 points
- **Good Questions**: 5-25 points (based on strategy)
- **Presenting Evidence**: 10-25 points (based on relevance)
- **Discovering Clues**: 15-25 points (based on importance)
- **Legal Statements**: 5-25 points (based on legal knowledge)

## Win Conditions

- Score at least 80 points
- Discover at least 3 clues
- Present at least 2 pieces of evidence
- Question at least 2 witnesses

## Technical Details

- **Backend**: Python with FastAPI
- **Frontend**: HTML, CSS, JavaScript
- **AI Integration**: OpenAI GPT models for dynamic responses
- **Real-time Updates**: Live conversation and scoring updates

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
