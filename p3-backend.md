---
layout: default
title: Código del backend
parent: Práctica 3
nav_order: 1
---

# Código del backend

El backend está implementado en **Python** con el framework **FastAPI**. Se conecta a Ollama directamente mediante HTTP (`requests`) con `stream: false` para obtener la respuesta completa junto con todas las métricas de inferencia en un solo objeto JSON.

---

## Estructura del endpoint `/chat`

```
POST /chat
├── Valida parámetros con Pydantic Field (rangos estrictos)
├── Construye el payload para Ollama /api/chat
├── Mide wall_time con time.perf_counter()
├── Llama a http://localhost:11434/api/chat (stream: false)
├── Extrae métricas del JSON de respuesta
└── Retorna ChatResponse {model, reply, metrics}
```

---

## `chatbot/backend/main.py`

```python
import time
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

OLLAMA_BASE     = "http://localhost:11434"
OLLAMA_CHAT_URL = f"{OLLAMA_BASE}/api/chat"
OLLAMA_TAGS_URL = f"{OLLAMA_BASE}/api/tags"

app = FastAPI(title="Sage — Chatbot LLM local", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message:       str   = Field(..., min_length=1, max_length=4000)
    model:         str   = Field(default="gemma3:4b")
    temperature:   float = Field(default=0.7,  ge=0.0,  le=1.2)
    top_p:         float = Field(default=0.9,  ge=0.1,  le=1.0)
    num_predict:   int   = Field(default=160,  ge=20,   le=1000)
    num_ctx:       int   = Field(default=4096, ge=512,  le=8192)
    repeat_penalty:float = Field(default=1.1,  ge=1.0,  le=2.0)
    system_prompt: str   = Field(
        default="Eres un asistente académico claro, preciso y útil para estudiantes universitarios."
    )


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
    model:   str
    reply:   str
    metrics: ChatMetrics


@app.get("/")
def root():
    return {"message": "Sage — Chatbot LLM local", "docs": "/docs", "health": "/health"}


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


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    payload = {
        "model": req.model,
        "messages": [
            {"role": "system", "content": req.system_prompt},
            {"role": "user",   "content": req.message},
        ],
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
        t0 = time.perf_counter()
        response = requests.post(OLLAMA_CHAT_URL, json=payload, timeout=300)
        t1 = time.perf_counter()
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.ConnectionError as exc:
        raise HTTPException(
            status_code=503,
            detail="No se pudo conectar con Ollama. Verifica que esté ejecutándose.",
        ) from exc
    except requests.exceptions.Timeout as exc:
        raise HTTPException(status_code=504, detail="La solicitud a Ollama tardó demasiado.") from exc
    except requests.exceptions.HTTPError as exc:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Error de Ollama: {response.text}",
        ) from exc

    reply             = data.get("message", {}).get("content", "")
    total_duration_s  = data.get("total_duration",  0) / 1e9
    load_duration_s   = data.get("load_duration",   0) / 1e9
    prompt_eval_count = data.get("prompt_eval_count", 0)
    eval_count        = data.get("eval_count",        0)
    eval_duration_s   = data.get("eval_duration",   0) / 1e9
    total_tokens      = prompt_eval_count + eval_count
    tokens_per_second = eval_count / eval_duration_s if eval_duration_s > 0 else 0.0

    return ChatResponse(
        model=req.model,
        reply=reply,
        metrics=ChatMetrics(
            wall_time_s=       round(t1 - t0,            4),
            total_duration_s=  round(total_duration_s,   4),
            load_duration_s=   round(load_duration_s,    4),
            prompt_eval_count= prompt_eval_count,
            eval_count=        eval_count,
            total_tokens=      total_tokens,
            eval_duration_s=   round(eval_duration_s,    4),
            tokens_per_second= round(tokens_per_second,  2),
        ),
    )
```

---

## `chatbot/backend/requirements.txt`

```
fastapi==0.115.5
uvicorn[standard]==0.32.1
requests==2.32.3
python-dotenv==1.0.1
```

---

## Endpoints disponibles

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/` | Mensaje de bienvenida y enlaces útiles |
| `GET` | `/health` | Estado de conexión con Ollama |
| `GET` | `/models` | Lista de modelos instalados en Ollama |
| `POST` | `/chat` | Chat con un mensaje, retorna respuesta + métricas |

---

## Modelo de respuesta `/chat`

```json
{
  "model": "gemma3:4b",
  "reply": "Un LLM (Large Language Model) es...",
  "metrics": {
    "wall_time_s": 5.8913,
    "total_duration_s": 3.8046,
    "load_duration_s": 0.1957,
    "prompt_eval_count": 37,
    "eval_count": 80,
    "total_tokens": 117,
    "eval_duration_s": 2.4551,
    "tokens_per_second": 32.59
  }
}
```

> Los tiempos de Ollama (`total_duration`, `load_duration`, `eval_duration`) se obtienen del JSON de respuesta en nanosegundos y se dividen entre `1e9` para convertirlos a segundos. `tokens_per_second` se calcula como `eval_count / eval_duration_s`.
