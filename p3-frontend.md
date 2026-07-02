---
layout: default
title: Código del frontend
parent: Práctica 3
nav_order: 2
---

# Código del frontend

El frontend está construido con **HTML, CSS y JavaScript** puros, sin frameworks externos. Mantiene el diseño minimalista de Sage con acento violeta (`#7c3aed`) y tipografía Inter. Agrega un panel lateral de configuración de parámetros y un grid de 8 métricas que aparece debajo de cada respuesta del modelo.

---

## Componentes principales

| Componente | Descripción |
|---|---|
| Header | Logo Sage, pill con modelo activo, botón de configuración (⚙), botón nueva conversación |
| Panel de configuración | Sidebar deslizable con sliders para temperature, top_p, num_predict, repeat_penalty, selector para num_ctx y model, textarea para system prompt |
| Área de mensajes | Burbujas de usuario (violeta) y del asistente (blanca con borde), pantalla de bienvenida con 4 chips de prompt rápido |
| Panel de métricas | Grid 4×2 que aparece bajo cada respuesta con las 8 métricas de inferencia |
| Footer/Compositor | Textarea auto-expandible, botón de envío, indicador de estado |

---

## `chatbot/frontend/index.html`

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Sage</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <!-- Panel de configuración lateral -->
  <aside id="settings-panel" class="settings-panel" aria-hidden="true">
    <div class="settings-header">
      <span class="settings-title">Configuración</span>
      <button id="close-settings" class="icon-btn" aria-label="Cerrar">×</button>
    </div>
    <div class="settings-body">
      <!-- Selector de modelo -->
      <div class="setting-group">
        <label for="model-select" class="setting-label">Modelo</label>
        <select id="model-select" class="setting-select">
          <option value="gemma3:4b">gemma3:4b</option>
        </select>
      </div>
      <!-- Temperature slider -->
      <div class="setting-group">
        <label class="setting-label">Temperature <span class="setting-value" id="temp-val">0.7</span></label>
        <input type="range" id="temperature" min="0" max="1.2" step="0.05" value="0.7" class="slider">
      </div>
      <!-- Top-p slider -->
      <div class="setting-group">
        <label class="setting-label">Top-p <span class="setting-value" id="topp-val">0.90</span></label>
        <input type="range" id="top_p" min="0.1" max="1.0" step="0.05" value="0.9" class="slider">
      </div>
      <!-- num_predict slider -->
      <div class="setting-group">
        <label class="setting-label">Tokens a generar <span class="setting-value" id="predict-val">160</span></label>
        <input type="range" id="num_predict" min="20" max="1000" step="10" value="160" class="slider">
      </div>
      <!-- num_ctx selector -->
      <div class="setting-group">
        <label for="num_ctx" class="setting-label">Ventana de contexto</label>
        <select id="num_ctx" class="setting-select">
          <option value="2048">2 048 tokens</option>
          <option value="4096" selected>4 096 tokens</option>
          <option value="8192">8 192 tokens</option>
        </select>
      </div>
      <!-- repeat_penalty slider -->
      <div class="setting-group">
        <label class="setting-label">Repeat penalty <span class="setting-value" id="penalty-val">1.10</span></label>
        <input type="range" id="repeat_penalty" min="1.0" max="2.0" step="0.05" value="1.1" class="slider">
      </div>
      <!-- System prompt -->
      <div class="setting-group">
        <label for="system_prompt" class="setting-label">System prompt</label>
        <textarea id="system_prompt" class="setting-textarea" rows="3">
          Eres un asistente académico claro, preciso y útil para estudiantes universitarios.
        </textarea>
      </div>
    </div>
  </aside>
  <div id="settings-overlay" class="settings-overlay"></div>

  <!-- Layout principal -->
  <div class="app">
    <header class="header">
      <div class="brand">
        <!-- SVG icon omitido por brevedad -->
        <span class="brand-name">Sage</span>
      </div>
      <div class="header-actions">
        <span class="model-pill" id="header-model">gemma3:4b</span>
        <button id="open-settings" class="icon-btn">⚙</button>
        <button id="new-chat" class="icon-btn">✎</button>
      </div>
    </header>

    <main class="messages" id="messages">
      <div class="welcome" id="welcome">
        <h1 class="welcome-title">Sage</h1>
        <p class="welcome-sub">Chatbot LLM local · Ollama · gemma3:4b</p>
        <div class="chips">
          <button class="chip">¿Qué es un LLM y cómo funciona?</button>
          <button class="chip">Explica el concepto de temperatura en IA</button>
          <button class="chip">¿Qué diferencia hay entre GPT y Gemma?</button>
          <button class="chip">¿Cómo afecta num_ctx al rendimiento?</button>
        </div>
      </div>
    </main>

    <footer class="footer">
      <div class="composer">
        <textarea id="input" class="composer-input" placeholder="Escribe un mensaje…" rows="1"></textarea>
        <button id="send" class="send-btn">▶</button>
      </div>
      <p class="footer-note" id="status-note">
        Sage · Ollama local · <span id="status-indicator">●</span> listo
      </p>
    </footer>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <script src="app.js"></script>
</body>
</html>
```

---

## `chatbot/frontend/app.js` — fragmento clave: llamada al backend

```javascript
async function sendMessage() {
  const text = inputEl.value.trim();
  if (!text || sendBtn.disabled) return;

  // Construir payload con parámetros del panel de configuración
  const payload = {
    message:        text,
    model:          modelSelect.value,
    temperature:    parseFloat(tempSlider.value),
    top_p:          parseFloat(toppSlider.value),
    num_predict:    parseInt(predictSlider.value),
    num_ctx:        parseInt(ctxSelect.value),
    repeat_penalty: parseFloat(penaltySlider.value),
    system_prompt:  systemPrompt.value.trim(),
  };

  try {
    const res = await fetch('http://localhost:8000/chat', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(payload),
    });

    const data = await res.json();
    // data.reply  → texto de la respuesta (renderizado con marked.js)
    // data.metrics → objeto con las 8 métricas → se renderiza en buildMetrics()
    renderAssistantContent(row, loading, data.reply, data.metrics);
  } catch (err) { /* manejo de error */ }
}
```

---

## `chatbot/frontend/app.js` — renderizado de métricas

```javascript
const METRIC_DEFS = [
  { key: 'wall_time_s',       label: 'Tiempo backend', fmt: v => v.toFixed(3) + ' s' },
  { key: 'total_duration_s',  label: 'Tiempo Ollama',  fmt: v => v.toFixed(3) + ' s' },
  { key: 'load_duration_s',   label: 'Carga modelo',   fmt: v => v.toFixed(3) + ' s' },
  { key: 'eval_duration_s',   label: 'Generación',     fmt: v => v.toFixed(3) + ' s' },
  { key: 'prompt_eval_count', label: 'Tokens entrada', fmt: v => v                   },
  { key: 'eval_count',        label: 'Tokens salida',  fmt: v => v                   },
  { key: 'total_tokens',      label: 'Tokens totales', fmt: v => v                   },
  { key: 'tokens_per_second', label: 'Tokens/s',       fmt: v => v.toFixed(1)        },
];

function buildMetrics(m) {
  const panel = document.createElement('div');
  panel.className = 'metrics-panel'; // grid 4 columnas

  METRIC_DEFS.forEach(def => {
    const card = document.createElement('div');
    card.className = 'metric-card';
    card.innerHTML = `
      <div class="metric-label">${def.label}</div>
      <div class="metric-value">${def.fmt(m[def.key])}</div>
    `;
    panel.appendChild(card);
  });
  return panel;
}
```

---

## Diagrama de flujo del frontend

```
Usuario escribe mensaje
        │
        ▼
sendMessage()
  ├── Leer parámetros del panel de configuración
  ├── Agregar burbuja de usuario al chat
  ├── Mostrar burbuja "cargando" (3 puntos animados)
  ├── POST /chat → esperar respuesta completa (no streaming)
  └── Respuesta recibida
        ├── Renderizar reply con marked.parse()
        └── Construir y mostrar grid de 8 métricas
```
