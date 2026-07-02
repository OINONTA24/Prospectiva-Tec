---
layout: default
title: Código del frontend
parent: Práctica 4
nav_order: 4
---

# Código del frontend

El frontend de la Práctica 4 extiende la interfaz de la Práctica 3. Los cambios principales son: el selector de perfil de copiloto en el panel de configuración, el pill verde en el header que indica el perfil activo, la etiqueta de sender sobre cada respuesta del asistente, y la lógica de historial de conversación en JavaScript.

---

## Cambios respecto a la Práctica 3

| Elemento | Práctica 3 | Práctica 4 |
|---|---|---|
| Identificación del asistente | Sin etiqueta | Etiqueta verde con nombre del perfil activo |
| Perfil de copiloto | Campo de texto libre | Selector que carga perfiles desde `/profiles` |
| Historial | Sin historial | `conversationHistory[]` acumulado por sesión |
| Header | Pill con modelo | Pill de modelo + pill de copiloto activo |

---

## Selector de perfiles — `index.html`

Se añadió un bloque `.setting-group` al inicio del panel de configuración, antes del selector de modelo:

```html
<!-- Selector de perfil de copiloto -->
<div class="setting-group">
  <label for="copilot-select" class="setting-label">Perfil de copiloto</label>
  <select id="copilot-select" class="setting-select">
    <!-- poblado por JS desde GET /profiles -->
  </select>
  <p id="copilot-desc" class="profile-desc"></p>
</div>
```

El campo `<p id="copilot-desc">` muestra la descripción del perfil seleccionado en tiempo real.

---

## Pill de copiloto activo — `index.html`

En el header se añadió un segundo badge junto al pill del modelo:

```html
<span class="model-pill" id="header-model">gemma3:4b</span>
<span class="copilot-pill" id="header-copilot">Asistente genérico</span>
```

El pill verde se actualiza automáticamente al cambiar de perfil.

---

## Carga de perfiles — `app.js`

Al iniciar la página, se llama a `GET /profiles` para obtener la lista de perfiles y poblar el selector:

```javascript
let profilesData = [];

async function loadProfiles() {
  try {
    const r    = await fetch(`${API}/profiles`);
    const data = await r.json();
    profilesData = data.profiles || [];

    copilotSelect.innerHTML = '';
    profilesData.forEach(p => {
      const opt = document.createElement('option');
      opt.value       = p.id;
      opt.textContent = p.label;
      copilotSelect.appendChild(opt);
    });

    applyProfile();
  } catch (_) { /* backend puede no estar corriendo aún */ }
}

function applyProfile() {
  const p = profilesData.find(p => p.id === copilotSelect.value);
  if (!p) return;
  systemPrompt.value        = p.system_prompt;   // autocompletado del textarea
  copilotDesc.textContent   = p.description;     // descripción debajo del selector
  headerCopilot.textContent = p.label;           // pill del header
}

copilotSelect.addEventListener('change', applyProfile);
```

Cuando el usuario cambia de perfil, el campo `system_prompt` del panel se actualiza automáticamente. El usuario puede editarlo manualmente si desea un prompt personalizado.

---

## Historial de conversación — `app.js`

```javascript
let conversationHistory = [];

// En sendMessage(), al recibir una respuesta exitosa:
conversationHistory.push({ role: 'user',      content: text });
conversationHistory.push({ role: 'assistant', content: data.reply });

// En el payload enviado al backend:
const payload = {
  message:        text,
  history:        conversationHistory,   // ← array de turnos anteriores
  copilot_id:     copilotSelect.value,
  system_prompt:  systemPrompt.value.trim(),
  // ... parámetros del modelo
};

// Al presionar "Nueva conversación":
newChatBtn.addEventListener('click', () => {
  conversationHistory = [];   // ← historial reiniciado
  // ...
});
```

El historial crece con cada turno exitoso. Si el backend retorna un error, ese turno no se agrega al historial para evitar inconsistencias.

---

## Etiqueta de sender — `app.js`

Cada respuesta del asistente muestra el nombre del perfil activo sobre la burbuja:

```javascript
function renderAssistantContent(row, loading, reply, metrics, copilotLabel) {
  row.removeChild(loading);

  if (copilotLabel) {
    const tag = document.createElement('div');
    tag.className   = 'sender-label';
    tag.textContent = copilotLabel;
    row.appendChild(tag);
  }

  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.innerHTML = marked.parse(reply);
  row.appendChild(bubble);

  if (metrics) row.appendChild(buildMetrics(metrics));
  scrollBottom();
}
```

El valor de `copilotLabel` viene del campo `copilot_label` de la respuesta del backend, no del frontend. Esto garantiza que la etiqueta refleja el perfil que realmente procesó la solicitud.

---

## Estilos nuevos — `style.css`

```css
/* Pill verde del header — indica el perfil activo */
.copilot-pill {
  font-size: 11px;
  font-weight: 500;
  color: var(--green);
  background: var(--green-soft);
  border: 1px solid var(--green-mid);
  border-radius: 20px;
  padding: 3px 10px;
  max-width: 180px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Etiqueta sobre la burbuja del asistente */
.sender-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--green);
  letter-spacing: .3px;
  padding: 0 2px;
  display: flex;
  align-items: center;
  gap: 5px;
}
.sender-label::before {
  content: '';
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--green);
  flex-shrink: 0;
}

/* Descripción del perfil bajo el selector */
.profile-desc {
  font-size: 12px;
  color: var(--text-muted);
  line-height: 1.5;
  font-style: italic;
}
```

El verde (`--green: #059669`) diferencia visualmente los elementos de copiloto del acento violeta (`--accent: #7c3aed`) que ya existía en la Práctica 3.
