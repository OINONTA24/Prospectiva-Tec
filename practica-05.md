---
layout: default
title: Práctica 5
nav_order: 6
has_children: true
---

# Práctica 5 — Chatbot híbrido con APIs externas

Esta práctica corresponde a la asignatura **Prospectiva de la Tecnología** (IE127), impartida en la Universidad Iberoamericana Ciudad de México durante el verano 2026.

El objetivo es extender el chatbot/copiloto de la Práctica 4 para que pueda conversar con un modelo local en Ollama **y** con al menos dos modelos remotos mediante APIs externas: Google Gemini y Groq.

---

## Arquitectura híbrida

```
Navegador (frontend HTML/JS)
        │  POST /chat  { provider, model, api_key, … }
        ▼
  FastAPI · Python               ← backend puerto 8000
  • Selecciona handler por provider
  • Construye messages[] según formato de cada API
  • Mide wall_time y extrae métricas de tokens
        │
        ├──[ollama]──▶  Ollama REST API  (localhost:11434)
        │                       │
        │                       ▼
        │               llama3.2:3b (local)
        │
        ├──[gemini]──▶  Gemini API  (generativelanguage.googleapis.com)
        │                       │
        │                       ▼
        │               gemini-2.5-flash
        │
        └──[groq]────▶  Groq API  (api.groq.com/openai/v1)
                                │
                                ▼
                        llama-3.3-70b-versatile
```

| Capa | Tecnología | Novedad respecto a Práctica 4 |
|---|---|---|
| Frontend | HTML · CSS · JavaScript | Selector de proveedor, campo API key, métricas unificadas |
| Backend | Python · FastAPI | Tres handlers: Ollama, Gemini, Groq; campos unificados `provider`, `max_tokens` |
| Inferencia local | Ollama | Sin cambios (nuevo modelo `llama3.2:3b`) |
| Inferencia remota | Gemini API + Groq API | Nuevo — requiere API keys externas |

---

## Proveedores implementados

| Proveedor | Tipo | Modelo probado | Requiere API key |
|---|---|---|---|
| Ollama | Local / abierto | `qwen2.5:7b` | No |
| Gemini API (Google) | Remoto / cerrado | `gemini-2.5-flash` | Sí |
| Groq API | Remoto / abierto | `llama-3.3-70b-versatile` | Sí |

---

## Formato de solicitud unificado

El endpoint `POST /chat` recibe los mismos parámetros independientemente del proveedor:

```json
{
  "message":        "…",
  "history":        [],
  "provider":       "ollama | gemini | groq",
  "model":          "nombre-del-modelo",
  "api_key":        "…  (vacío para Ollama)",
  "temperature":    0.7,
  "top_p":          0.9,
  "max_tokens":     300,
  "num_ctx":        4096,
  "repeat_penalty": 1.1,
  "system_prompt":  "…",
  "copilot_id":     "robotica"
}
```

Los parámetros `num_ctx` y `repeat_penalty` son específicos de Ollama; se ignoran para los proveedores remotos.

---

## Métricas devueltas

| Campo | Ollama | Gemini | Groq |
|---|---|---|---|
| `wall_time_s` | ✅ | ✅ | ✅ |
| `prompt_tokens` | ✅ `prompt_eval_count` | ✅ `promptTokenCount` | ✅ `prompt_tokens` |
| `completion_tokens` | ✅ `eval_count` | ✅ `candidatesTokenCount` | ✅ `completion_tokens` |
| `total_tokens` | ✅ | ✅ | ✅ |
| `tokens_per_second` | ✅ (calculado con `eval_duration`) | ~ (calculado con `wall_time`) | ~ (calculado con `wall_time`) |
| `eval_duration_s` | ✅ | N/D | N/D |
| `load_duration_s` | ✅ | N/D | N/D |

---

## Requisitos cumplidos

| # | Requisito | Estado |
|---|---|---|
| 1 | Selector de proveedor | ✅ |
| 2 | Selector de modelo | ✅ (dinámico por proveedor) |
| 3 | Selector de perfil de copiloto | ✅ (4 perfiles) |
| 4 | Edición de `system_prompt` | ✅ |
| 5 | Modificar `temperature`, `top_p` y `max_tokens` | ✅ |
| 6 | Mostrar respuesta | ✅ |
| 7 | Mostrar tokens de entrada, salida y totales | ✅ |
| 8 | Mostrar tiempo total | ✅ |
| 9 | Manejar errores de conexión o API key faltante | ✅ |
| 10 | Al menos dos proveedores remotos | ✅ (Gemini + Groq) |
| 11 | Mismo prompt en los tres proveedores | ✅ (ver Pruebas) |

---

## Ejecución

```bash
# 1. Instalar dependencias del backend
cd chatbot-p5/backend
pip install -r requirements.txt

# 2. Iniciar el backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000

# 3. Abrir el frontend
# Arrastrar chatbot-p5/frontend/index.html al navegador
```

Para usar Gemini o Groq:
1. Abre Configuración (⚙).
2. Selecciona el proveedor.
3. Ingresa tu API key en el campo correspondiente.
4. Selecciona el modelo y envía.

> Las API keys se transmiten al backend en cada solicitud y **no se almacenan** en disco ni en el navegador.

---

## Consideraciones de privacidad

Al usar Gemini o Groq, el prompt, el system prompt y el historial de conversación se envían a servidores externos. Para esta práctica académica se utilizan prompts técnicos genéricos que no contienen datos personales, institucionales ni confidenciales.
