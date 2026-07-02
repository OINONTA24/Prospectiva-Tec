---
layout: default
title: Código del frontend
parent: Práctica 5
nav_order: 2
---

# Código del frontend

El frontend de la Práctica 5 extiende el de la Práctica 4 con un selector de proveedor, un campo de API key y métricas unificadas.

---

## Cambios respecto a la Práctica 4

| Elemento | Práctica 4 | Práctica 5 |
|---|---|---|
| Selector de proveedor | No | ✅ (Ollama / Gemini / Groq) |
| Campo de API key | No | ✅ (visible solo para APIs remotas) |
| Lista de modelos | Dinámica (solo Ollama) | Dinámica para Ollama; estática para Gemini y Groq |
| Configuración Ollama | Siempre visible | Ocultable (sección "Solo Ollama") |
| Pill de proveedor en header | No | ✅ |
| Métricas | 8 (específicas de Ollama) | 6 unificadas (N/D para campos no disponibles) |

---

## Estructura del panel de configuración

```
┌─────────────────────────┐
│  Configuración          │
├─────────────────────────┤
│  Proveedor              │  ← selector: Ollama / Gemini / Groq
│  API Key                │  ← visible solo si proveedor ≠ ollama
│  Perfil de copiloto     │
│  Modelo                 │  ← lista dinámica según proveedor
│  Temperature     [0.70] │
│  Top-p           [0.90] │
│  Tokens máximos  [300]  │
├─── Solo Ollama ─────────┤  ← oculto para APIs remotas
│  Ventana de contexto    │
│  Repeat penalty  [1.10] │
├─────────────────────────┤
│  System prompt          │
└─────────────────────────┘
```

---

## Cambio de proveedor

Cuando el usuario cambia el selector de proveedor, la función `onProviderChange()` ejecuta cuatro acciones:

```javascript
function onProviderChange() {
  const provider = providerSelect.value;

  // 1. Mostrar/ocultar campo de API key
  apiKeyGroup.style.display = provider === 'ollama' ? 'none' : '';

  // 2. Mostrar/ocultar parámetros exclusivos de Ollama
  ollamaSettings.style.display = provider === 'ollama' ? '' : 'none';

  // 3. Actualizar lista de modelos
  if (provider === 'ollama') {
    populateModelSelect(ollamaModels, ollamaModels[0] || 'gemma3:4b');
  } else {
    populateModelSelect(REMOTE_MODELS[provider], REMOTE_MODELS[provider][0]);
  }

  // 4. Actualizar pills del header y nota del footer
  const label = PROVIDER_LABELS[provider] || provider;
  headerProvider.textContent = label;
  providerNote.textContent   = label;
}
```

Las listas de modelos remotos están definidas como constantes:

```javascript
const REMOTE_MODELS = {
  gemini: ['gemini-2.5-flash', 'gemini-2.0-flash'],
  groq:   ['llama-3.3-70b-versatile', 'llama3-8b-8192', 'mixtral-8x7b-32768'],
};
```

---

## Construcción del payload

El payload enviado al backend incluye los nuevos campos:

```javascript
const payload = {
  message:        text,
  history:        conversationHistory,
  provider:       providerSelect.value,         // nuevo
  model:          modelSelect.value,
  api_key:        apiKeyInput.value.trim(),     // nuevo
  temperature:    parseFloat(tempSlider.value),
  top_p:          parseFloat(toppSlider.value),
  max_tokens:     parseInt(tokensSlider.value), // renombrado de num_predict
  num_ctx:        parseInt(ctxSelect.value),
  repeat_penalty: parseFloat(penaltySlider.value),
  system_prompt:  systemPrompt.value.trim(),
  copilot_id:     copilotSelect.value,
};
```

Si el proveedor no es Ollama y el campo `api_key` está vacío, se muestra un `alert` antes de enviar.

---

## Panel de métricas unificado

Las métricas se definen como un array que maneja valores `null` (cuando el proveedor no los proporciona):

```javascript
const METRIC_DEFS = [
  { key: 'wall_time_s',       label: 'Tiempo total',   fmt: v => v != null ? v.toFixed(3) + ' s' : 'N/D' },
  { key: 'prompt_tokens',     label: 'Tokens entrada', fmt: v => v != null ? v : 'N/D'                   },
  { key: 'completion_tokens', label: 'Tokens salida',  fmt: v => v != null ? v : 'N/D'                   },
  { key: 'total_tokens',      label: 'Tokens totales', fmt: v => v != null ? v : 'N/D'                   },
  { key: 'tokens_per_second', label: 'Tokens/s',       fmt: v => v != null ? v.toFixed(1) : 'N/D', highlight: true },
  { key: 'eval_duration_s',   label: 'T. generación',  fmt: v => v != null ? v.toFixed(3) + ' s' : 'N/D' },
];
```

Los valores `null` (campo `eval_duration_s` en Gemini y Groq) se muestran como `N/D` con estilo atenuado.

---

## Validación antes de enviar

```javascript
async function sendMessage() {
  const text = inputEl.value.trim();
  if (!text || sendBtn.disabled) return;

  const provider = providerSelect.value;
  if (provider !== 'ollama' && !apiKeyInput.value.trim()) {
    alert(`Ingresa tu API key de ${PROVIDER_LABELS[provider]} en Configuración.`);
    return;
  }
  // …
}
```

---

## Interfaz

La interfaz mantiene la misma estructura de la Práctica 4 con tres adiciones visibles:

1. **Pill de proveedor** en el header (gris, izquierda del pill de modelo).
2. **Campo API key** en el panel de configuración, visible solo para Gemini y Groq.
3. **Sección "Solo Ollama"** con separador, que se oculta al cambiar de proveedor.
