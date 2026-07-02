const API = 'http://localhost:8000';

/* ── DOM refs ─────────────────────────────────────── */
const messagesEl    = document.getElementById('messages');
const welcomeEl     = document.getElementById('welcome');
const inputEl       = document.getElementById('input');
const sendBtn       = document.getElementById('send');
const newChatBtn    = document.getElementById('new-chat');
const statusNote    = document.getElementById('status-indicator');
const headerModel   = document.getElementById('header-model');
const headerCopilot = document.getElementById('header-copilot');

// Settings
const openSettings  = document.getElementById('open-settings');
const closeSettings = document.getElementById('close-settings');
const panel         = document.getElementById('settings-panel');
const overlay       = document.getElementById('settings-overlay');

// Parameter controls
const modelSelect   = document.getElementById('model-select');
const tempSlider    = document.getElementById('temperature');
const tempVal       = document.getElementById('temp-val');
const toppSlider    = document.getElementById('top_p');
const toppVal       = document.getElementById('topp-val');
const predictSlider = document.getElementById('num_predict');
const predictVal    = document.getElementById('predict-val');
const ctxSelect     = document.getElementById('num_ctx');
const penaltySlider = document.getElementById('repeat_penalty');
const penaltyVal    = document.getElementById('penalty-val');
const systemPrompt  = document.getElementById('system_prompt');

// Copilot profile
const copilotSelect = document.getElementById('copilot-select');
const copilotDesc   = document.getElementById('copilot-desc');

/* ── Marked config ────────────────────────────────── */
marked.setOptions({ breaks: true, gfm: true });

/* ── Conversation history ─────────────────────────── */
let conversationHistory = [];

/* ── Profiles ─────────────────────────────────────── */
let profilesData = [];

async function loadProfiles() {
  try {
    const r    = await fetch(`${API}/profiles`);
    const data = await r.json();
    profilesData = data.profiles || [];

    copilotSelect.innerHTML = '';
    profilesData.forEach(p => {
      const opt = document.createElement('option');
      opt.value = p.id;
      opt.textContent = p.label;
      copilotSelect.appendChild(opt);
    });

    applyProfile();
  } catch (_) { /* backend may not be running yet */ }
}

function applyProfile() {
  const p = profilesData.find(p => p.id === copilotSelect.value);
  if (!p) return;
  systemPrompt.value      = p.system_prompt;
  copilotDesc.textContent = p.description;
  headerCopilot.textContent = p.label;
}

copilotSelect.addEventListener('change', applyProfile);

/* ── Load models ──────────────────────────────────── */
async function loadModels() {
  try {
    const r    = await fetch(`${API}/models`);
    const data = await r.json();
    const models = data.models || [];
    if (!models.length) return;

    modelSelect.innerHTML = '';
    models.forEach(m => {
      const opt = document.createElement('option');
      opt.value = m;
      opt.textContent = m;
      if (m.startsWith('gemma3:4b')) opt.selected = true;
      modelSelect.appendChild(opt);
    });
    syncModelPill();
  } catch (_) { /* Ollama may not be running yet */ }
}

function syncModelPill() {
  headerModel.textContent = modelSelect.value;
}

/* ── Slider live values ───────────────────────────── */
tempSlider.addEventListener('input',    () => { tempVal.textContent    = parseFloat(tempSlider.value).toFixed(2); });
toppSlider.addEventListener('input',    () => { toppVal.textContent    = parseFloat(toppSlider.value).toFixed(2); });
predictSlider.addEventListener('input', () => { predictVal.textContent = predictSlider.value; });
penaltySlider.addEventListener('input', () => { penaltyVal.textContent = parseFloat(penaltySlider.value).toFixed(2); });
modelSelect.addEventListener('change',  syncModelPill);

/* ── Settings panel toggle ────────────────────────── */
openSettings.addEventListener('click', () => {
  panel.classList.add('open');
  panel.setAttribute('aria-hidden', 'false');
  overlay.classList.add('active');
});

function closePanel() {
  panel.classList.remove('open');
  panel.setAttribute('aria-hidden', 'true');
  overlay.classList.remove('active');
}
closeSettings.addEventListener('click', closePanel);
overlay.addEventListener('click', closePanel);

/* ── Textarea auto-resize ─────────────────────────── */
inputEl.addEventListener('input', () => {
  inputEl.style.height = 'auto';
  inputEl.style.height = Math.min(inputEl.scrollHeight, 120) + 'px';
});

inputEl.addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
});

/* ── Chips ────────────────────────────────────────── */
document.querySelectorAll('.chip').forEach(chip => {
  chip.addEventListener('click', () => {
    inputEl.value = chip.textContent;
    inputEl.dispatchEvent(new Event('input'));
    sendMessage();
  });
});

/* ── New chat ─────────────────────────────────────── */
newChatBtn.addEventListener('click', () => {
  messagesEl.innerHTML = '';
  messagesEl.appendChild(welcomeEl);
  welcomeEl.style.display = '';
  inputEl.value = '';
  conversationHistory = [];
  setStatus('ready');
});

/* ── Helpers ──────────────────────────────────────── */
function setStatus(state) {
  if (state === 'ready') {
    statusNote.textContent = '●';
    statusNote.className   = '';
    statusNote.nextSibling.textContent = ' listo';
  } else if (state === 'loading') {
    statusNote.textContent = '●';
    statusNote.className   = 'loading';
    statusNote.nextSibling.textContent = ' generando…';
  } else if (state === 'error') {
    statusNote.textContent = '●';
    statusNote.className   = 'error';
    statusNote.nextSibling.textContent = ' error';
  }
}

function scrollBottom() {
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function appendUserBubble(text) {
  welcomeEl.style.display = 'none';

  const row    = document.createElement('div');
  row.className = 'msg-row user';
  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.textContent = text;
  row.appendChild(bubble);
  messagesEl.appendChild(row);
  scrollBottom();
  return row;
}

function appendAssistantRow() {
  const row = document.createElement('div');
  row.className = 'msg-row assistant';

  const loading = document.createElement('div');
  loading.className = 'bubble loading-bubble';
  loading.innerHTML = '<div class="dot"></div><div class="dot"></div><div class="dot"></div>';
  row.appendChild(loading);

  messagesEl.appendChild(row);
  scrollBottom();
  return { row, loading };
}

function renderAssistantContent(row, loading, reply, metrics, copilotLabel) {
  row.removeChild(loading);

  if (copilotLabel) {
    const tag = document.createElement('div');
    tag.className = 'sender-label';
    tag.textContent = copilotLabel;
    row.appendChild(tag);
  }

  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.innerHTML = marked.parse(reply);
  row.appendChild(bubble);

  if (metrics) {
    const metricsPanel = buildMetrics(metrics);
    row.appendChild(metricsPanel);
  }
  scrollBottom();
}

/* ── Metrics panel ────────────────────────────────── */
const METRIC_DEFS = [
  { key: 'wall_time_s',       label: 'Tiempo backend', fmt: v => v.toFixed(3) + ' s', highlight: false },
  { key: 'total_duration_s',  label: 'Tiempo Ollama',  fmt: v => v.toFixed(3) + ' s', highlight: false },
  { key: 'load_duration_s',   label: 'Carga modelo',   fmt: v => v.toFixed(3) + ' s', highlight: false },
  { key: 'eval_duration_s',   label: 'Generación',     fmt: v => v.toFixed(3) + ' s', highlight: false },
  { key: 'prompt_eval_count', label: 'Tokens entrada', fmt: v => v,                   highlight: false },
  { key: 'eval_count',        label: 'Tokens salida',  fmt: v => v,                   highlight: false },
  { key: 'total_tokens',      label: 'Tokens totales', fmt: v => v,                   highlight: false },
  { key: 'tokens_per_second', label: 'Tokens/s',       fmt: v => v.toFixed(1),        highlight: true  },
];

function buildMetrics(m) {
  const metricsPanel = document.createElement('div');
  metricsPanel.className = 'metrics-panel';

  METRIC_DEFS.forEach(def => {
    const card = document.createElement('div');
    card.className = 'metric-card' + (def.highlight ? ' highlight' : '');

    const label = document.createElement('div');
    label.className = 'metric-label';
    label.textContent = def.label;

    const value = document.createElement('div');
    value.className = 'metric-value';
    value.textContent = def.fmt(m[def.key]);

    card.appendChild(label);
    card.appendChild(value);
    metricsPanel.appendChild(card);
  });

  return metricsPanel;
}

/* ── Send message ─────────────────────────────────── */
async function sendMessage() {
  const text = inputEl.value.trim();
  if (!text || sendBtn.disabled) return;

  sendBtn.disabled     = true;
  inputEl.disabled     = true;
  inputEl.style.height = 'auto';
  inputEl.value        = '';
  setStatus('loading');

  appendUserBubble(text);
  const { row, loading } = appendAssistantRow();

  const payload = {
    message:        text,
    history:        conversationHistory,
    model:          modelSelect.value,
    temperature:    parseFloat(tempSlider.value),
    top_p:          parseFloat(toppSlider.value),
    num_predict:    parseInt(predictSlider.value),
    num_ctx:        parseInt(ctxSelect.value),
    repeat_penalty: parseFloat(penaltySlider.value),
    system_prompt:  systemPrompt.value.trim(),
    copilot_id:     copilotSelect.value,
  };

  try {
    const res = await fetch(`${API}/chat`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(payload),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || res.statusText);
    }

    const data = await res.json();
    conversationHistory.push({ role: 'user',      content: text });
    conversationHistory.push({ role: 'assistant', content: data.reply });
    renderAssistantContent(row, loading, data.reply, data.metrics, data.copilot_label);
    setStatus('ready');

  } catch (err) {
    row.removeChild(loading);
    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    bubble.style.color = '#ef4444';
    bubble.textContent = `Error: ${err.message}`;
    row.appendChild(bubble);
    setStatus('error');
  } finally {
    sendBtn.disabled  = false;
    inputEl.disabled  = false;
    inputEl.focus();
  }
}

sendBtn.addEventListener('click', sendMessage);

/* ── Init ─────────────────────────────────────────── */
loadModels();
loadProfiles();
inputEl.focus();
