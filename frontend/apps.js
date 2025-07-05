// Game state variables
let gameState = null;
let currentCase = null;
let conversation = [];
let loading = false;

// DOM elements
const mainMenu = document.getElementById('main-menu');
const caseDescription = document.getElementById('case-description');
const gameRules = document.getElementById('game-rules');
const gameInterface = document.getElementById('game-interface');
const conversationLog = document.getElementById('conversation-log');
const questionInput = document.getElementById('question-input');
const askQuestionBtn = document.getElementById('ask-question-btn');
const judgeChatInput = document.getElementById('judge-chat-input');
const judgeChatBtn = document.getElementById('judge-chat-btn');
const witnessList = document.getElementById('witness-list');
const evidenceList = document.getElementById('evidence-list');
const cluesDiscovered = document.getElementById('clues-discovered');
const witnessActions = document.getElementById('witness-actions');

// New speaker display elements
const speakerImage = document.getElementById('speaker-image');
const speakerName = document.getElementById('speaker-name');
const speakerText = document.getElementById('speaker-text');

// Game status elements
const currentStepEl = document.getElementById('current-step');
const maxStepsEl = document.getElementById('max-steps');
const playerScoreEl = document.getElementById('player-score');
const targetScoreEl = document.getElementById('target-score');

// Page elements
const caseTitleEl = document.getElementById('case-title');
const caseDetailsEl = document.getElementById('case-details');
const rulesContentEl = document.getElementById('rules-content');

// Dropdown state
let dropdownStates = {
  'chat-history': false,
  'witnesses': false,
  'evidence': false,
  'judge-chat': false,
  'clues': false
};

function toggleDropdown(dropdownId) {
  const content = document.getElementById(`${dropdownId}-content`);
  const arrow = document.getElementById(`${dropdownId}-arrow`);
  
  dropdownStates[dropdownId] = !dropdownStates[dropdownId];
  
  if (dropdownStates[dropdownId]) {
    content.classList.add('open');
    arrow.textContent = '▲';
  } else {
    content.classList.remove('open');
    arrow.textContent = '▼';
  }
}

function updateSpeakerDisplay(speaker, text, imageSrc = null) {
  speakerName.textContent = speaker;
  speakerText.textContent = text;
  
  if (imageSrc) {
    // Use provided image source
    speakerImage.src = imageSrc;
  } else {
    // Get appropriate image based on speaker
    const imagePath = getSpeakerImage(speaker);
    speakerImage.src = imagePath;
    
    // Handle image loading errors
    speakerImage.onerror = function() {
      console.warn(`Image not found: ${imagePath}, using default`);
      this.src = 'images/courtroom.jpg';
    };
  }
  
  // Add to conversation history
  addMessage(speaker, text);
}

function getSpeakerImage(speaker) {
  // Map speakers to appropriate images
  const speakerImages = {
    // Court officials (place in frontend/images/)
    'Judge': 'images/judge.jpg',
    'Clerk': 'images/clerk.jpg',
    'Bailiff': 'images/bailiff.jpg',
    
    // Witnesses (place in frontend/images/ or frontend/images/witnesses/)
    'Carlos Rivera': 'images/carl.jpg',
    'Alice Monroe': 'images/alice1.jpg',
    'Detective Sarah Lin': 'images/detect.jpg',
    'Mr. Thompson': 'images/thompson.jpg',
    'Security Guard': 'images/security.jpg',
    
    // Player and system
    'You': 'images/attorney.jpg',
    'System': 'images/courtroom.jpg',
    
    // Default fallback
    'default': 'images/courtroom.jpg'
  };
  
  // Return the specific image for the speaker, or default
  return speakerImages[speaker] || speakerImages['default'];
}

function setLoading(state) {
  loading = state;
  document.body.style.cursor = loading ? 'wait' : 'default';
  
  // Disable interactive elements
  const buttons = document.querySelectorAll('button');
  const inputs = document.querySelectorAll('input');
  
  buttons.forEach(btn => btn.disabled = loading);
  inputs.forEach(input => input.disabled = loading);
}

function showError(msg) {
  conversation.push({ speaker: 'System', text: `Error: ${msg}`, type: 'error' });
  renderConversation();
}

function addMessage(speaker, text, type = 'normal') {
  conversation.push({ speaker, text, type });
  renderConversation();
}

function renderConversation() {
  conversationLog.innerHTML = conversation.map(msg => {
    const className = msg.type === 'error' ? 'error' : msg.type === 'success' ? 'success' : '';
    return `<div class="${className}"><b>${msg.speaker}:</b> ${msg.text}</div>`;
  }).join('');
  conversationLog.scrollTop = conversationLog.scrollHeight;
}

function updateGameStatus() {
  if (gameState) {
    currentStepEl.textContent = gameState.current_step;
    maxStepsEl.textContent = gameState.max_steps;
    playerScoreEl.textContent = Math.round(gameState.player_score);
    targetScoreEl.textContent = gameState.objective?.target_score || 80;
    
    // Debug logging
    console.log('Game State Updated:', {
      current_step: gameState.current_step,
      max_steps: gameState.max_steps,
      player_score: gameState.player_score,
      target_score: gameState.objective?.target_score || 80
    });
  }
}

// Navigation functions
function showMainMenu() {
  mainMenu.style.display = 'block';
  caseDescription.style.display = 'none';
  gameRules.style.display = 'none';
  gameInterface.style.display = 'none';
  
  // Reset game state
  conversation = [];
  gameState = null;
  currentCase = null;
  renderConversation();
  
  // Reset game over state
  const gameInterface = document.querySelector('.game-interface');
  if (gameInterface) {
    gameInterface.classList.remove('game-over');
  }
}

function showCaseDescription() {
  mainMenu.style.display = 'none';
  caseDescription.style.display = 'block';
  gameRules.style.display = 'none';
  gameInterface.style.display = 'none';
  
  // Reset game state
  conversation = [];
  gameState = null;
  currentCase = null;
  
  // Reset UI elements
  witnessList.innerHTML = '';
  evidenceList.innerHTML = '';
  cluesDiscovered.innerHTML = '';
  witnessActions.style.display = 'none';
  questionInput.value = '';
  judgeChatInput.value = '';
  
  // Reset game over state
  const gameInterfaceEl = document.querySelector('.game-interface');
  if (gameInterfaceEl) {
    gameInterfaceEl.classList.remove('game-over');
  }
  
  // Load case data
  loadCaseData();
}

function showGameRules() {
  mainMenu.style.display = 'none';
  caseDescription.style.display = 'none';
  gameRules.style.display = 'block';
  gameInterface.style.display = 'none';
  
  // Load rules
  loadGameRules();
}

function loadCaseData() {
  // For now, we'll use hardcoded case data
  caseTitleEl.textContent = "The Missing Necklace";
  caseDetailsEl.innerHTML = `
    <h3>Case Background</h3>
    <p>A priceless diamond necklace worth $500,000 vanished during a high-society gala at the Grand Plaza Hotel. The defendant, Carlos Rivera, a renowned caterer, is accused of theft.</p>
    
    <h3>Key Details</h3>
    <ul>
      <li>The necklace was last seen in a display case at 8:30 PM</li>
      <li>The theft was discovered at 9:15 PM</li>
      <li>Security footage has a 10-minute gap from 8:40-8:50 PM</li>
      <li>A glove was found near the kitchen entrance (size 9, but Carlos wears size 11)</li>
      <li>Mr. Thompson, a guest, was seen hurrying out at 8:55 PM</li>
    </ul>
    
    <h3>Your Role</h3>
    <p>You are the defense attorney for Carlos Rivera. Your task is to create reasonable doubt about his guilt and prove that someone else could have committed the theft.</p>
  `;
}

function loadGameRules() {
  rulesContentEl.innerHTML = `
    <h3>Game Objectives</h3>
    <p>Demonstrate that Carlos Rivera is innocent by:</p>
    <ol>
      <li>Establishing his alibi</li>
      <li>Showing others had opportunity</li>
      <li>Creating reasonable doubt about the evidence</li>
    </ol>
    
    <h3>Game Rules</h3>
    <ul>
      <li>You have <strong>8 steps</strong> to complete your case</li>
      <li>You need at least <strong>80 points</strong> to win</li>
      <li>Discover at least <strong>3 clues</strong></li>
      <li>Present at least <strong>2 pieces of evidence</strong></li>
      <li>Question at least <strong>2 witnesses</strong></li>
    </ul>
    
    <h3>Scoring System</h3>
    <ul>
      <li>Calling witnesses: 5 points</li>
      <li>Good questions: 5-25 points (based on strategy)</li>
      <li>Presenting evidence: 10-25 points (based on relevance)</li>
      <li>Discovering clues: 15-25 points (based on importance)</li>
      <li>Legal statements to judge: 5-25 points (based on legal knowledge)</li>
    </ul>
    
    <h3>Win Conditions</h3>
    <ul>
      <li>Score at least 80 points</li>
      <li>Discover at least 3 clues</li>
      <li>Present at least 2 pieces of evidence</li>
      <li>Question at least 2 witnesses</li>
    </ul>
  `;
}

function startGame() {
  setLoading(true);
  fetch('http://localhost:8000/start_case', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({})
  })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        currentCase = data.data.case_data;
        gameState = data.data.game_state;
        
        // Show game interface
        mainMenu.style.display = 'none';
        caseDescription.style.display = 'none';
        gameRules.style.display = 'none';
        gameInterface.style.display = 'block';
        
        // Load witnesses and evidence
        loadWitnesses();
        loadEvidence();
        
        // Add initial message and update speaker display
        updateSpeakerDisplay('Judge', 'Court is now in session. The defense may proceed.');
        
        updateGameStatus();
      } else {
        showError(data.message || 'Failed to start case');
      }
    })
    .catch(err => {
      showError('Failed to connect to server. Make sure the backend is running.');
      console.error(err);
    })
    .finally(() => setLoading(false));
}

function loadWitnesses() {
  fetch('http://localhost:8000/witnesses')
    .then(res => res.json())
    .then(data => {
      witnessList.innerHTML = data.witnesses.map(witness => `
        <div class="witness-item" onclick="callWitness('${witness}')">
          <strong>${witness}</strong>
        </div>
      `).join('');
    })
    .catch(err => {
      console.error('Failed to load witnesses:', err);
    });
}

function loadEvidence() {
  fetch('http://localhost:8000/evidence')
    .then(res => res.json())
    .then(data => {
      evidenceList.innerHTML = data.evidence.map(evidence => `
        <div class="evidence-item ${evidence.presented ? 'presented' : ''}" onclick="useEvidence('${evidence.id}')">
          <div class="evidence-name">${evidence.name}</div>
          <div class="evidence-points">${evidence.points_value} points</div>
          ${evidence.presented ? '<small>Presented</small>' : ''}
        </div>
      `).join('');
    })
    .catch(err => {
      console.error('Failed to load evidence:', err);
    });
}

function callWitness(witnessName) {
  if (loading) return;
  
  setLoading(true);
  fetch('http://localhost:8000/call_witness', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ witness_name: witnessName })
  })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        gameState = data.game_state;
        
        // Update witness list to show called witness
        const witnessItems = witnessList.querySelectorAll('.witness-item');
        witnessItems.forEach(item => {
          if (item.textContent.includes(witnessName)) {
            item.classList.add('called');
          }
        });
        
        // Show witness actions
        witnessActions.style.display = 'block';
        
        // Update speaker display with clerk introduction
        updateSpeakerDisplay('Clerk', data.data.introduction);
        addMessage('Judge', `${witnessName}, you may take the stand.`, 'success');
        
        // Update score
        if (data.points_earned > 0) {
          addMessage('System', `+${data.points_earned} points for calling witness`, 'success');
        }
        
        updateGameStatus();
        checkGameEnd();
      } else {
        showError(data.message || 'Failed to call witness');
      }
    })
    .catch(err => {
      showError('Failed to call witness');
      console.error(err);
    })
    .finally(() => setLoading(false));
}

function askQuestion() {
  const question = questionInput.value.trim();
  if (!question || loading) return;
  
  setLoading(true);
  fetch('http://localhost:8000/question_witness', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question: question })
  })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        gameState = data.game_state;
        
        // Update speaker display with witness response
        updateSpeakerDisplay(gameState.current_witness, data.data.witness_response.content);
        addMessage('You', question);
        
        // Check for clue revelation
        if (data.data.clues_revealed) {
          addMessage('System', `Clue discovered: ${data.data.clue_id}`, 'success');
        }
        
        // Update score
        if (data.points_earned > 0) {
          addMessage('System', `+${data.points_earned} points for good question`, 'success');
        }
        
        // Clear input
        questionInput.value = '';
        
        updateGameStatus();
        checkGameEnd();
      } else {
        showError(data.message || 'Failed to ask question');
      }
    })
    .catch(err => {
      showError('Failed to ask question');
      console.error(err);
    })
    .finally(() => setLoading(false));
}

function useEvidence(evidenceId) {
  if (loading) return;
  
  setLoading(true);
  fetch('http://localhost:8000/use_evidence', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ evidence_id: evidenceId })
  })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        gameState = data.game_state;
        
        // Update speaker display with judge response
        updateSpeakerDisplay('Judge', data.data.judge_response.content);
        addMessage('You', `I present evidence: ${data.data.evidence.name}`);
        
        // Update evidence list
        loadEvidence();
        
        // Update score
        if (data.points_earned > 0) {
          addMessage('System', `+${data.points_earned} points for presenting evidence`, 'success');
        }
        
        updateGameStatus();
        checkGameEnd();
      } else {
        showError(data.message || 'Failed to present evidence');
      }
    })
    .catch(err => {
      showError('Failed to present evidence');
      console.error(err);
    })
    .finally(() => setLoading(false));
}

function chatWithJudge() {
  const statement = judgeChatInput.value.trim();
  if (!statement || loading) return;
  
  setLoading(true);
  fetch('http://localhost:8000/judge_chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ statement: statement })
  })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        gameState = data.game_state;
        
        // Update speaker display with judge response
        updateSpeakerDisplay('Judge', data.data.judge_response.content);
        addMessage('You', statement);
        
        // Update score
        if (data.points_earned > 0) {
          addMessage('System', `+${data.points_earned} points for legal statement`, 'success');
        }
        
        // Clear input
        judgeChatInput.value = '';
        
        updateGameStatus();
        checkGameEnd();
      } else {
        showError(data.message || 'Failed to chat with judge');
      }
    })
    .catch(err => {
      showError('Failed to chat with judge');
      console.error(err);
    })
    .finally(() => setLoading(false));
}

function getClue() {
  if (loading) return;
  
  setLoading(true);
  fetch('http://localhost:8000/get_clue', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({})
  })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        gameState = data.game_state;
        
        // Add clue to discovered list
        const clueItem = document.createElement('div');
        clueItem.className = 'clue-item';
        clueItem.textContent = data.data.clue.description;
        cluesDiscovered.appendChild(clueItem);
        
        // Add message
        addMessage('System', `Clue discovered: ${data.data.clue.description}`, 'success');
        
        // Update score
        if (data.points_earned > 0) {
          addMessage('System', `+${data.points_earned} points for discovering clue`, 'success');
        }
        
        updateGameStatus();
        checkGameEnd();
      } else {
        showError(data.message || 'Failed to get clue');
      }
    })
    .catch(err => {
      showError('Failed to get clue');
      console.error(err);
    })
    .finally(() => setLoading(false));
}

function checkGameEnd() {
  // Check if game should end only after 8 steps
  if (gameState && gameState.current_step >= gameState.max_steps) {
    addMessage('Judge', 'Time is up. The court will now deliberate.', 'success');
    setTimeout(() => {
      getVerdict();
    }, 2000);
  }
}

function getVerdict() {
  if (loading) return;
  
  setLoading(true);
  fetch('http://localhost:8000/verdict')
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        const verdict = data.data;
        
        // Create comprehensive verdict text for response area
        const verdictText = `VERDICT: ${verdict.guilty ? 'GUILTY' : 'NOT GUILTY'}

${verdict.reasoning}

FINAL SCORE: ${Math.round(verdict.score)} points

${verdict.score >= 80 ? '🎉 CONGRATULATIONS! You WON the case!' : '❌ You did NOT win the case. Try again!'}

Performance Summary:
• Evidence Presented: ${verdict.player_performance.evidence_presented}
• Witnesses Examined: ${verdict.player_performance.witnesses_examined}
• Clues Discovered: ${verdict.player_performance.clues_discovered}
• Objections Raised: ${verdict.player_performance.objections_raised}`;

        // Update speaker display with verdict
        updateSpeakerDisplay('Judge', verdictText);
        
        // Add to conversation log
        addMessage('System', `Final Score: ${Math.round(verdict.score)} points`, 'success');
        
        // Disable all game actions after verdict
        disableGameActions();
        
      } else {
        showError(data.message || 'Failed to get verdict');
      }
    })
    .catch(err => {
      showError('Failed to get verdict');
      console.error(err);
    })
    .finally(() => setLoading(false));
}

function disableGameActions() {
  // Disable all interactive elements
  const buttons = document.querySelectorAll('button:not(.game-controls button)');
  const inputs = document.querySelectorAll('input');
  
  buttons.forEach(btn => btn.disabled = true);
  inputs.forEach(input => input.disabled = true);
  
  // Add visual indication that game is over
  document.querySelector('.game-interface').classList.add('game-over');
}

// Event listeners
askQuestionBtn.addEventListener('click', askQuestion);
questionInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') {
    askQuestion();
  }
});

judgeChatBtn.addEventListener('click', chatWithJudge);
judgeChatInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') {
    chatWithJudge();
  }
});

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  // Show main menu by default
  showMainMenu();
}); 