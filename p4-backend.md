---
layout: default
title: Código del backend
parent: Práctica 4
nav_order: 3
---

# Código del backend

El backend de la Práctica 4 extiende el de la Práctica 3. Los cambios principales son: el diccionario de perfiles (`PROFILES`), el modelo de datos para el historial (`HistoryMessage`), el campo `history[]` en la solicitud, y el nuevo endpoint `GET /profiles`.

---

## Cambios respecto a la Práctica 3

| Elemento | Práctica 3 | Práctica 4 |
|---|---|---|
| System prompt | Campo libre en el frontend | Seleccionable por perfil + editable |
| Historial | Sin historial (pregunta aislada) | `history[]` acumulado turno a turno |
| Perfiles | N/A | `PROFILES` dict + endpoint `/profiles` |
| Respuesta | `model`, `reply`, `metrics` | Agrega `copilot_label` |

---

## Diccionario de perfiles

```python
PROFILES = {
    "generico": {
        "label": "Asistente genérico",
        "description": "Asistente neutral sin especialización. Sirve como línea base de comparación.",
        "system_prompt": (
            "You are a helpful, neutral, and knowledgeable AI assistant.\n\n"
            "Instructions:\n"
            "- Answer the user's question directly.\n"
            "- Be concise by default.\n"
            # ... (instrucciones completas en main.py)
        ),
    },
    "robotica": {
        "label": "Copiloto de robótica",
        "description": "Especialista en robótica, automatización, ROS2, sensores, control y mecatrónica.",
        "system_prompt": ( "..." ),
    },
    "docente": {
        "label": "Copiloto docente",
        "description": "Asistente educativo que adapta explicaciones al nivel del estudiante.",
        "system_prompt": ( "..." ),
    },
    "investigacion": {
        "label": "Copiloto de investigación",
        "description": "Asistente para exploración de literatura, metodología y razonamiento basado en evidencia.",
        "system_prompt": ( "..." ),
    },
}
```

---

## Modelos de datos

### `HistoryMessage` — nuevo en Práctica 4

```python
class HistoryMessage(BaseModel):
    role:    str = Field(..., pattern="^(user|assistant)$")
    content: str = Field(..., min_length=1)
```

Cada objeto representa un turno de conversación: `role` puede ser `"user"` o `"assistant"`.

### `ChatRequest` — campo `history` y `copilot_id` añadidos

```python
class ChatRequest(BaseModel):
    message:        str                  = Field(..., min_length=1, max_length=4000)
    history:        List[HistoryMessage] = Field(default=[])      # ← nuevo
    model:          str                  = Field(default="gemma3:4b")
    temperature:    float                = Field(default=0.7,  ge=0.0,  le=1.2)
    top_p:          float                = Field(default=0.9,  ge=0.1,  le=1.0)
    num_predict:    int                  = Field(default=160,  ge=20,   le=1000)
    num_ctx:        int                  = Field(default=4096, ge=512,  le=8192)
    repeat_penalty: float                = Field(default=1.1,  ge=1.0,  le=2.0)
    system_prompt:  str                  = Field(default="You are a helpful, neutral, and knowledgeable AI assistant.")
    copilot_id:     str                  = Field(default="generico")  # ← nuevo
```

### `ChatResponse` — campo `copilot_label` añadido

```python
class ChatResponse(BaseModel):
    model:         str
    copilot_label: str        # ← nuevo: etiqueta del perfil activo
    reply:         str
    metrics:       ChatMetrics
```

---

## Endpoint `/profiles` — nuevo

```python
@app.get("/profiles")
def list_profiles():
    return {
        "profiles": [
            {
                "id":            pid,
                "label":         p["label"],
                "description":   p["description"],
                "system_prompt": p["system_prompt"],
            }
            for pid, p in PROFILES.items()
        ]
    }
```

Devuelve la lista completa de perfiles con sus IDs, etiquetas, descripciones y system prompts. El frontend lo consume al cargar la página para poblar el selector de perfiles.

---

## Endpoint `/chat` — construcción del historial

La diferencia principal con la Práctica 3 está en cómo se construye el array `messages` antes de enviarlo a Ollama:

```python
@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    profile       = PROFILES.get(req.copilot_id, PROFILES["generico"])
    copilot_label = profile["label"]

    # Construir messages[] con historial completo
    messages = [{"role": "system", "content": req.system_prompt}]
    for h in req.history:
        messages.append({"role": h.role, "content": h.content})
    messages.append({"role": "user", "content": req.message})

    payload = {
        "model":    req.model,
        "messages": messages,        # ← historial completo enviado a Ollama
        "stream":     False,
        "keep_alive": "5m",
        "options": {
            "temperature":    req.temperature,
            "top_p":          req.top_p,
            "num_predict":    req.num_predict,
            "num_ctx":        req.num_ctx,
            "repeat_penalty": req.repeat_penalty,
        },
    }
    # ... (manejo de errores y extracción de métricas sin cambios)
```

El array `messages` que recibe Ollama tiene la siguiente estructura por turno:

```
[
  { "role": "system",    "content": "<system_prompt del perfil>" },
  { "role": "user",      "content": "<turno 1 del usuario>" },
  { "role": "assistant", "content": "<turno 1 del asistente>" },
  { "role": "user",      "content": "<turno 2 del usuario>" },
  { "role": "assistant", "content": "<turno 2 del asistente>" },
  ...
  { "role": "user",      "content": "<mensaje actual>" }
]
```

Esto permite que el modelo responda con contexto de toda la conversación previa.

---

## Código completo — `main.py`

```python
import time
import requests
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

OLLAMA_BASE     = "http://localhost:11434"
OLLAMA_CHAT_URL = f"{OLLAMA_BASE}/api/chat"
OLLAMA_TAGS_URL = f"{OLLAMA_BASE}/api/tags"

PROFILES = {
    "generico": {
        "label": "Asistente genérico",
        "description": "Asistente neutral sin especialización. Sirve como línea base de comparación.",
        "system_prompt": (
            "You are a helpful, neutral, and knowledgeable AI assistant.\n\n"
            "Instructions:\n"
            "- Answer the user's question directly.\n"
            "- Be concise by default.\n"
            "- Use short responses for simple questions.\n"
            "- Provide more detail only when the user asks for it or when the topic requires it.\n"
            "- Avoid unnecessary introductions, conclusions, disclaimers, and repetition.\n"
            "- Stay neutral and objective.\n"
            "- If information is uncertain, say so clearly.\n"
            "- Do not invent facts.\n"
            "- Use clear and natural language.\n"
            "- Focus on solving the user's request efficiently.\n\n"
            "Adapt the level of detail to the complexity of the question."
        ),
    },
    "robotica": {
        "label": "Copiloto de robótica",
        "description": "Especialista en robótica, automatización, ROS2, sensores, control y mecatrónica.",
        "system_prompt": (
            "You are a robotics engineering copilot.\n\n"
            "You help students, researchers, and engineers with:\n\n"
            "- Robotics\n- Automation\n- Mechatronics\n- ROS2\n"
            "- Embedded systems\n- Arduino and microcontrollers\n"
            "- Sensors and actuators\n- Computer vision\n"
            "- Control systems\n- Industrial robotics\n"
            "- AI applications in robotics\n\n"
            "Guidelines:\n\n"
            "- Answer directly and concisely.\n"
            "- For simple questions, use 2–5 sentences.\n"
            "- For complex topics, provide structured explanations.\n"
            "- Use technical terminology when appropriate.\n"
            "- Show formulas only when they help solve the problem.\n"
            "- Ask clarifying questions when information is missing.\n"
            "- State uncertainties clearly.\n"
            "- Do not invent specifications, measurements, or facts.\n"
            "- Prioritize practical engineering solutions.\n\n"
            "Language Policy:\n"
            "- Respond in the same language used by the user.\n"
            "- If the user switches languages, adapt accordingly.\n"
            "- Do not translate unless requested."
        ),
    },
    "docente": {
        "label": "Copiloto docente",
        "description": "Asistente educativo que adapta explicaciones al nivel del estudiante.",
        "system_prompt": (
            "You are an educational copilot that helps students learn and understand academic topics.\n\n"
            "Guidelines:\n\n"
            "- Answer clearly, accurately, and directly.\n"
            "- Adapt explanations to the student's level.\n"
            "- Start with the main idea before adding details.\n"
            "- Use examples when they improve understanding.\n"
            "- For simple questions, respond briefly.\n"
            "- For complex topics, organize the explanation step by step.\n"
            "- Encourage understanding instead of memorization.\n"
            "- Ask clarifying questions when necessary.\n"
            "- If information is uncertain, say so clearly.\n"
            "- Do not invent facts, sources, or references.\n\n"
            "Response Length Policy:\n"
            "- Simple questions: 1–3 sentences.\n"
            "- Medium complexity: concise explanation.\n"
            "- Complex topics: structured explanation with examples.\n\n"
            "Language Policy:\n"
            "- Respond in the same language used by the user.\n"
            "- If the user switches languages, adapt accordingly.\n"
            "- Do not translate unless requested."
        ),
    },
    "investigacion": {
        "label": "Copiloto de investigación",
        "description": "Asistente para exploración de literatura, metodología y razonamiento basado en evidencia.",
        "system_prompt": (
            "You are a research copilot that assists students, academics, and professionals "
            "with research tasks.\n\n"
            "You help with: literature exploration, research planning, topic analysis, "
            "critical evaluation, methodology selection, hypothesis development, "
            "data interpretation, academic writing, comparative analysis, "
            "and evidence-based reasoning.\n\n"
            "Guidelines:\n\n"
            "- Prioritize accuracy, clarity, and evidence-based reasoning.\n"
            "- Distinguish clearly between facts, interpretations, assumptions, and hypotheses.\n"
            "- Do not invent sources, citations, studies, statistics, or references.\n"
            "- If evidence is unavailable or uncertain, state it explicitly.\n"
            "- Ask clarifying questions when the research objective is unclear.\n"
            "- Remain objective and neutral.\n\n"
            "When evaluating claims:\n"
            "1. State the claim.\n"
            "2. Analyze available evidence.\n"
            "3. Identify limitations or uncertainties.\n"
            "4. Present a balanced conclusion.\n\n"
            "Language Policy:\n"
            "- Respond in the same language used by the user.\n"
            "- If the user switches languages, adapt accordingly.\n"
            "- Do not translate unless requested."
        ),
    },
}

app = FastAPI(title="Sage — Copilotos especializados", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class HistoryMessage(BaseModel):
    role:    str = Field(..., pattern="^(user|assistant)$")
    content: str = Field(..., min_length=1)


class ChatRequest(BaseModel):
    message:        str                  = Field(..., min_length=1, max_length=4000)
    history:        List[HistoryMessage] = Field(default=[])
    model:          str                  = Field(default="gemma3:4b")
    temperature:    float                = Field(default=0.7,  ge=0.0,  le=1.2)
    top_p:          float                = Field(default=0.9,  ge=0.1,  le=1.0)
    num_predict:    int                  = Field(default=160,  ge=20,   le=1000)
    num_ctx:        int                  = Field(default=4096, ge=512,  le=8192)
    repeat_penalty: float                = Field(default=1.1,  ge=1.0,  le=2.0)
    system_prompt:  str                  = Field(default="You are a helpful, neutral, and knowledgeable AI assistant.")
    copilot_id:     str                  = Field(default="generico")


class ChatMetrics(BaseModel):
    wall_time_s:       float
    total_duration_s:  float
    load_duration_s:   float
    prompt_eval_count: int
    eval_count:        int
    total_tokens:      int
    eval_duration_s:   float
    tokens_per_second: float


class ChatResponse(BaseModel):
    model:         str
    copilot_label: str
    reply:         str
    metrics:       ChatMetrics


@app.get("/")
def root():
    return {
        "message": "Sage — Copilotos especializados",
        "docs":     "/docs",
        "health":   "/health",
        "profiles": "/profiles",
    }


@app.get("/health")
def health():
    try:
        r = requests.get(OLLAMA_TAGS_URL, timeout=5)
        r.raise_for_status()
        return {"status": "ok", "ollama": "connected"}
    except Exception:
        return {"status": "degraded", "ollama": "unavailable"}


@app.get("/models")
def list_models():
    try:
        r = requests.get(OLLAMA_TAGS_URL, timeout=10)
        r.raise_for_status()
        models = [m["name"] for m in r.json().get("models", [])]
        return {"models": models}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Ollama no disponible: {exc}")


@app.get("/profiles")
def list_profiles():
    return {
        "profiles": [
            {
                "id":            pid,
                "label":         p["label"],
                "description":   p["description"],
                "system_prompt": p["system_prompt"],
            }
            for pid, p in PROFILES.items()
        ]
    }


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    profile       = PROFILES.get(req.copilot_id, PROFILES["generico"])
    copilot_label = profile["label"]

    messages = [{"role": "system", "content": req.system_prompt}]
    for h in req.history:
        messages.append({"role": h.role, "content": h.content})
    messages.append({"role": "user", "content": req.message})

    payload = {
        "model":    req.model,
        "messages": messages,
        "stream":     False,
        "keep_alive": "5m",
        "options": {
            "temperature":    req.temperature,
            "top_p":          req.top_p,
            "num_predict":    req.num_predict,
            "num_ctx":        req.num_ctx,
            "repeat_penalty": req.repeat_penalty,
        },
    }

    try:
        t0       = time.perf_counter()
        response = requests.post(OLLAMA_CHAT_URL, json=payload, timeout=300)
        t1       = time.perf_counter()
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.ConnectionError as exc:
        raise HTTPException(status_code=503,
            detail="No se pudo conectar con Ollama. Verifica que esté ejecutándose.") from exc
    except requests.exceptions.Timeout as exc:
        raise HTTPException(status_code=504,
            detail="La solicitud a Ollama tardó demasiado.") from exc
    except requests.exceptions.HTTPError as exc:
        raise HTTPException(status_code=response.status_code,
            detail=f"Error de Ollama: {response.text}") from exc

    reply             = data.get("message", {}).get("content", "")
    total_duration_s  = data.get("total_duration",  0) / 1e9
    load_duration_s   = data.get("load_duration",   0) / 1e9
    prompt_eval_count = data.get("prompt_eval_count", 0)
    eval_count        = data.get("eval_count",        0)
    eval_duration_s   = data.get("eval_duration",   0) / 1e9
    total_tokens      = prompt_eval_count + eval_count
    tokens_per_second = eval_count / eval_duration_s if eval_duration_s > 0 else 0.0

    return ChatResponse(
        model=         req.model,
        copilot_label= copilot_label,
        reply=         reply,
        metrics=ChatMetrics(
            wall_time_s=       round(t1 - t0,           4),
            total_duration_s=  round(total_duration_s,  4),
            load_duration_s=   round(load_duration_s,   4),
            prompt_eval_count= prompt_eval_count,
            eval_count=        eval_count,
            total_tokens=      total_tokens,
            eval_duration_s=   round(eval_duration_s,   4),
            tokens_per_second= round(tokens_per_second, 2),
        ),
    )
```
