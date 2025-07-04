const conversationLog = document.getElementById('conversation-log');
const playerInput = document.getElementById('player-input');
const sendBtn = document.getElementById('send-btn');
const sceneImage = document.getElementById('scene-image');

// Example scenes
const scenes = {
  courtroom: 'scenes/courtroom.jpg',
  witness: 'scenes/witness_stand.jpg',
  // Add more scenes as needed
};
let currentScene = 'courtroom';

// Example conversation state
let conversation = [
  { speaker: 'Judge', text: 'Welcome to the courtroom. The trial is about to begin.' }
];

let loading = false;

function setLoading(state) {
  loading = state;
  playerInput.disabled = loading;
  sendBtn.disabled = loading;
  document.body.style.cursor = loading ? 'wait' : 'default';
}

function showError(msg) {
  conversation.push({ speaker: 'System', text: msg });
  renderConversation();
}

function startOrResetCase() {
  setLoading(true);
  fetch('http://localhost:8000/start_case', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({})
  })
    .then(res => res.json())
    .then(data => {
      conversation = [{ speaker: 'Judge', text: 'Case started: ' + (data.data?.case_name || 'New Case') }];
      renderConversation();
    })
    .catch(() => showError('Error starting case.'))
    .finally(() => setLoading(false));
}

function getVerdict() {
  setLoading(true);
  fetch('http://localhost:8000/verdict')
    .then(res => res.json())
    .then(data => {
      conversation.push({ speaker: 'Judge', text: 'Verdict: ' + (data.data?.verdict || '[No verdict]') });
      renderConversation();
    })
    .catch(() => showError('Error getting verdict.'))
    .finally(() => setLoading(false));
}

// Render conversation
function renderConversation() {
  conversationLog.innerHTML = conversation.map(
    msg => `<div><b>${msg.speaker}:</b> ${msg.text}</div>`
  ).join('');
  conversationLog.scrollTop = conversationLog.scrollHeight;
}

// Handle send
sendBtn.onclick = () => {
  const text = playerInput.value.trim();
  if (!text) return;
  conversation.push({ speaker: 'You', text });
  playerInput.value = '';
  renderConversation();
  setLoading(true);
  fetch('http://localhost:8000/ask_question', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question: text, witness_name: 'Alice Monroe' })
  })
    .then(res => res.json())
    .then(data => {
      const aiText = data.data?.witness_response?.content || '[No response]';
      conversation.push({ speaker: 'Witness', text: aiText });
      renderConversation();
    })
    .catch(() => showError('Error contacting server.'))
    .finally(() => setLoading(false));
};

// Example action handlers
function presentEvidence() {
  setLoading(true);
  const evidenceId = prompt('Enter evidence ID:');
  const description = prompt('Describe the evidence:');
  if (!evidenceId || !description) {
    setLoading(false);
    return;
  }
  fetch('http://localhost:8000/present_evidence', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ evidence_id: evidenceId, description })
  })
    .then(res => res.json())
    .then(data => {
      conversation.push({ speaker: 'You', text: `[You present evidence: ${description}]` });
      conversation.push({ speaker: 'Judge', text: data.message || '[No response]' });
      renderConversation();
    })
    .catch(() => showError('Error presenting evidence.'))
    .finally(() => setLoading(false));
}

function nextTurn() {
  setLoading(true);
  fetch('http://localhost:8000/next_turn', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action_type: 'next', details: {} })
  })
    .then(res => res.json())
    .then(data => {
      conversation.push({ speaker: 'Judge', text: data.message || 'Next turn.' });
      renderConversation();
    })
    .catch(() => showError('Error processing next turn.'))
    .finally(() => setLoading(false));
}

// Change scene example
function changeScene(scene) {
  currentScene = scene;
  sceneImage.src = scenes[scene] || scenes['courtroom'];
}

// Initial render
renderConversation();
// Optionally, auto-start a case on load
document.addEventListener('DOMContentLoaded', startOrResetCase); 