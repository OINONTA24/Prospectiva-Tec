const API = 'http://localhost:8000';

/* ── DOM refs ─────────────────────────────────────── */
const messagesEl    = document.getElementById('messages');
const welcomeEl     = document.getElementById('welcome');
const inputEl       = document.getElementById('input');
const sendBtn       = document.getElementById('send');
const newChatBtn    = document.getElementById('new-chat');
const statusNote    = document.getElementById('status-indicator');
const providerNote  = document.getElementById('provider-note');
const headerProvider= document.getElementById('header-provider');
const headerModel   = document.getElementById('header-model');
const headerCopilot = document.getElementById('header-copilot');

// Settings panel
const openSettings  = document.getElementById('open-settings');
const closeSettings = document.getElementById('close-settings');
const panel         = document.getElementById('settings-panel');
const overlay       = document.getElementById('settings-overlay');

// Controls
const providerSelect= document.getElementById('provider-select');
const apiKeyGroup   = document.getElementById('api-key-group');
const apiKeyInput   = document.getElementById('api-key');
const ollamaSettings= document.getElementById('ollama-settings');
const copilotSelect = document.getElementById('copilot-select');
const copilotDesc   = document.getElementById('copilot-desc');
const modelSelect   = document.getElementById('model-select');
const tempSlider    = document.getElementById('temperature');
const tempVal       = document.getElementById('temp-val');
const toppSlider    = document.getElementById('top_p');
const toppVal       = document.getElementById('topp-val');
const tokensSlider  = document.getElementById('max_tokens');
const tokensVal     = document.getElementById('tokens-val');
const ctxSelect     = document.getElementById('num_ctx');
const penaltySlider = document.getElementById('repeat_penalty');
const penaltyVal    = document.getElementById('penalty-val');
const systemPrompt  = document.getElementById('system_prompt');

/* ── Static model lists for remote providers ──────── */
const REMOTE_MODELS = {
  gemini: ['gemini-2.5-flash', 'gemini-2.0-flash'],
  groq:   ['llama-3.3-70b-versatile', 'llama3-8b-8192', 'mixtral-8x7b-32768'],
};

const PROVIDER_LABELS = {
  ollama: 'Ollama local',
  gemini: 'Gemini API',
  groq:   'Groq API',
};

/* ── Marked config ────────────────────────────────── */
marked.setOptions({ breaks: true, gfm: true });

/* ── Conversation history ─────────────────────────── */
let conversationHistory = [];
let ollamaModels        = [];

/* ── Provider change ──────────────────────────────── */
function onProviderChange() {
  const provider = providerSelect.value;

  // Show/hide API key input
  apiKeyGroup.style.display = provider === 'ollama' ? 'none' : '';

  // Show/hide Ollama-specific settings
  ollamaSettings.style.display = provider === 'ollama' ? '' : 'none';

  // Update model list
  if (provider === 'ollama') {
    populateModelSelect(ollamaModels, ollamaModels[0] || 'gemma3:4b');
  } else {
    populateModelSelect(REMOTE_MODELS[provider], REMOTE_MODELS[provider][0]);
  }

  // Update header + footer
  const label = PROVIDER_LABELS[provider] || provider;
  headerProvider.textContent = label;
  providerNote.textContent   = label;
  providerNote.className     = `provider-${provider}`;
}

providerSelect.addEventListener('change', onProviderChange);

/* ── Load models ──────────────────────────────────── */
function populateModelSelect(models, defaultModel) {
  if (!models || !models.length) return;
  modelSelect.innerHTML = '';
  models.forEach(m => {
    const opt = document.createElement('option');
    opt.value = m;
    opt.textContent = m;
    if (m === defaultModel) opt.selected = true;
    modelSelect.appendChild(opt);
  });
  syncModelPill();
}

async function loadModels() {
  try {
    const r    = await fetch(`${API}/models`);
    const data = await r.json();
    ollamaModels = data.ollama || [];
    if (providerSelect.value === 'ollama') {
      populateModelSelect(ollamaModels, ollamaModels.find(m => m.startsWith('gemma3')) || ollamaModels[0]);
    }
  } catch (_) { /* Ollama may not be running */ }
}

function syncModelPill() {
  headerModel.textContent = modelSelect.value;
}

modelSelect.addEventListener('change', syncModelPill);

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
  } catch (_) { /* backend may not be running */ }
}

function applyProfile() {
  const p = profilesData.find(p => p.id === copilotSelect.value);
  if (!p) return;
  systemPrompt.value        = p.system_prompt;
  copilotDesc.textContent   = p.description;
  headerCopilot.textContent = p.label;
}

copilotSelect.addEventListener('change', applyProfile);

/* ── Slider live values ───────────────────────────── */
tempSlider.addEventListener('input',    () => { tempVal.textContent    = parseFloat(tempSlider.value).toFixed(2); });
toppSlider.addEventListener('input',    () => { toppVal.textContent    = parseFloat(toppSlider.value).toFixed(2); });
tokensSlider.addEventListener('input',  () => { tokensVal.textContent  = tokensSlider.value; });
penaltySlider.addEventListener('input', () => { penaltyVal.textContent = parseFloat(penaltySlider.value).toFixed(2); });

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
    inputEl.value = chip.textContent.trim();
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

/* ── Status helpers ───────────────────────────────── */
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

/* ── Message bubble builders ──────────────────────── */
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

function renderAssistantContent(row, loading, reply, metrics, copilotLabel, provider) {
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
    row.appendChild(buildMetrics(metrics, provider));
  }
  scrollBottom();
}

/* ── Metrics panel ────────────────────────────────── */
const METRIC_DEFS = [
  { key: 'wall_time_s',       label: 'Tiempo total',   fmt: v => v != null ? v.toFixed(3) + ' s' : 'N/D', highlight: false },
  { key: 'prompt_tokens',     label: 'Tokens entrada', fmt: v => v != null ? v : 'N/D',                   highlight: false },
  { key: 'completion_tokens', label: 'Tokens salida',  fmt: v => v != null ? v : 'N/D',                   highlight: false },
  { key: 'total_tokens',      label: 'Tokens totales', fmt: v => v != null ? v : 'N/D',                   highlight: false },
  { key: 'tokens_per_second', label: 'Tokens/s',       fmt: v => v != null ? v.toFixed(1) : 'N/D',        highlight: true  },
  { key: 'eval_duration_s',   label: 'T. generación',  fmt: v => v != null ? v.toFixed(3) + ' s' : 'N/D', highlight: false },
];

function buildMetrics(m, provider) {
  const panel = document.createElement('div');
  panel.className = 'metrics-panel';

  METRIC_DEFS.forEach(def => {
    // Skip eval_duration_s for remote providers (null value)
    const val = m[def.key];

    const card = document.createElement('div');
    card.className = 'metric-card' + (def.highlight ? ' highlight' : '');

    const label = document.createElement('div');
    label.className = 'metric-label';
    label.textContent = def.label;

    const value = document.createElement('div');
    value.className = 'metric-value' + (val == null ? ' muted' : '');
    value.textContent = def.fmt(val);

    card.appendChild(label);
    card.appendChild(value);
    panel.appendChild(card);
  });

  return panel;
}

/* ── Send message ─────────────────────────────────── */
async function sendMessage() {
  const text = inputEl.value.trim();
  if (!text || sendBtn.disabled) return;

  // Validate API key for remote providers
  const provider = providerSelect.value;
  if (provider !== 'ollama' && !apiKeyInput.value.trim()) {
    alert(`Ingresa tu API key de ${PROVIDER_LABELS[provider]} en Configuración antes de enviar.`);
    return;
  }

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
    provider:       provider,
    model:          modelSelect.value,
    api_key:        apiKeyInput.value.trim(),
    temperature:    parseFloat(tempSlider.value),
    top_p:          parseFloat(toppSlider.value),
    max_tokens:     parseInt(tokensSlider.value),
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
    renderAssistantContent(row, loading, data.reply, data.metrics, data.copilot_label, data.provider);
    setStatus('ready');

  } catch (err) {
    row.removeChild(loading);
    const bubble = document.createElement('div');
    bubble.className = 'bubble error-bubble';
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
