---
layout: default
title: Código del backend
parent: Práctica 5
nav_order: 1
---

# Código del backend

El backend de la Práctica 5 extiende el de la Práctica 4. El cambio central es el enrutamiento por proveedor: según el campo `provider` de la solicitud, el endpoint `/chat` delega a un handler distinto para Ollama, Gemini o Groq.

---

## Cambios respecto a la Práctica 4

| Elemento | Práctica 4 | Práctica 5 |
|---|---|---|
| Proveedor | Solo Ollama | Ollama + Gemini API + Groq API |
| Campo de tokens | `num_predict` (Ollama) | `max_tokens` (unificado) |
| Solicitud | Sin `provider` ni `api_key` | Con `provider` y `api_key` |
| Métricas | 8 (específicas de Ollama) | 7 unificadas (`eval_duration_s` es `null` para APIs remotas) |
| Versión de la app | 2.0.0 | 3.0.0 |

---

## Constantes de configuración

```python
OLLAMA_BASE     = "http://localhost:11434"
OLLAMA_CHAT_URL = f"{OLLAMA_BASE}/api/chat"
OLLAMA_TAGS_URL = f"{OLLAMA_BASE}/api/tags"

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
GROQ_URL   = "https://api.groq.com/openai/v1/chat/completions"

PROVIDER_MODELS = {
    "gemini": ["gemini-2.5-flash", "gemini-2.0-flash"],
    "groq":   ["llama-3.3-70b-versatile", "llama3-8b-8192", "mixtral-8x7b-32768"],
}
```

---

## Modelos de datos

### ChatRequest

```python
class ChatRequest(BaseModel):
    message:        str   = Field(..., min_length=1, max_length=4000)
    history:        List[HistoryMessage] = Field(default=[])
    provider:       str   = Field(default="ollama")   # ollama | gemini | groq
    model:          str   = Field(default="gemma3:4b")
    api_key:        str   = Field(default="")
    temperature:    float = Field(default=0.7,  ge=0.0, le=2.0)
    top_p:          float = Field(default=0.9,  ge=0.1, le=1.0)
    max_tokens:     int   = Field(default=300,  ge=20,  le=2048)
    num_ctx:        int   = Field(default=4096, ge=512, le=8192)  # Ollama only
    repeat_penalty: float = Field(default=1.1,  ge=1.0, le=2.0)  # Ollama only
    system_prompt:  str   = Field(default="You are a helpful, neutral, and knowledgeable AI assistant.")
    copilot_id:     str   = Field(default="generico")
```

### ChatMetrics

```python
class ChatMetrics(BaseModel):
    wall_time_s:       float           # siempre disponible
    prompt_tokens:     int             # tokens de entrada
    completion_tokens: int             # tokens de salida
    total_tokens:      int             # prompt + completion
    tokens_per_second: float           # calculado con eval_duration (Ollama) o wall_time (remoto)
    eval_duration_s:   Optional[float] # solo Ollama; null para APIs remotas
    load_duration_s:   Optional[float] # solo Ollama; null para APIs remotas
```

### ChatResponse

```python
class ChatResponse(BaseModel):
    provider:      str
    model:         str
    copilot_label: str
    reply:         str
    metrics:       ChatMetrics
```

---

## Enrutamiento por proveedor

```python
@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    provider = req.provider.lower()
    if provider == "ollama":
        return _chat_ollama(req)
    elif provider == "gemini":
        return _chat_gemini(req)
    elif provider == "groq":
        return _chat_groq(req)
    else:
        raise HTTPException(status_code=400, detail=f"Proveedor desconocido: '{req.provider}'")
```

---

## Handler: Ollama

```python
def _chat_ollama(req: ChatRequest) -> ChatResponse:
    messages = [{"role": "system", "content": req.system_prompt}]
    for h in req.history:
        messages.append({"role": h.role, "content": h.content})
    messages.append({"role": "user", "content": req.message})

    payload = {
        "model": req.model, "messages": messages, "stream": False,
        "options": {
            "temperature": req.temperature, "top_p": req.top_p,
            "num_predict": req.max_tokens,  # max_tokens → num_predict
            "num_ctx": req.num_ctx, "repeat_penalty": req.repeat_penalty,
        },
    }
    # … requests.post + manejo de errores …
    prompt_tokens     = data.get("prompt_eval_count", 0)
    completion_tokens = data.get("eval_count", 0)
    eval_duration_s   = data.get("eval_duration", 0) / 1e9
    tokens_per_second = completion_tokens / eval_duration_s if eval_duration_s > 0 else 0.0
```

---

## Handler: Gemini API

Gemini usa un formato de messages diferente al estándar: el rol del asistente es `"model"` (no `"assistant"`), y el `system_prompt` va en un campo separado `system_instruction`.

```python
def _chat_gemini(req: ChatRequest) -> ChatResponse:
    if not req.api_key.strip():
        raise HTTPException(status_code=400, detail="Se requiere una API key para usar Gemini.")

    # Convertir historial: "assistant" → "model"
    contents = []
    for h in req.history:
        role = "model" if h.role == "assistant" else "user"
        contents.append({"role": role, "parts": [{"text": h.content}]})
    contents.append({"role": "user", "parts": [{"text": req.message}]})

    payload = {
        "system_instruction": {"parts": [{"text": req.system_prompt}]},
        "contents": contents,
        "generationConfig": {
            "temperature": req.temperature,
            "topP":        req.top_p,
            "maxOutputTokens": req.max_tokens,
        },
    }

    url = GEMINI_URL.format(model=req.model) + f"?key={req.api_key}"
    # … requests.post …

    usage             = data.get("usageMetadata", {})
    prompt_tokens     = usage.get("promptTokenCount", 0)
    completion_tokens = usage.get("candidatesTokenCount", 0)
    total_tokens      = usage.get("totalTokenCount", prompt_tokens + completion_tokens)
    tokens_per_second = completion_tokens / wall_time if wall_time > 0 else 0.0
    # eval_duration_s = None (no disponible en Gemini)
```

---

## Handler: Groq API

Groq expone una API compatible con OpenAI. El formato de `messages` es idéntico al de Ollama (roles `"system"`, `"user"`, `"assistant"`).

```python
def _chat_groq(req: ChatRequest) -> ChatResponse:
    if not req.api_key.strip():
        raise HTTPException(status_code=400, detail="Se requiere una API key para usar Groq.")

    messages = [{"role": "system", "content": req.system_prompt}]
    for h in req.history:
        messages.append({"role": h.role, "content": h.content})
    messages.append({"role": "user", "content": req.message})

    payload = {
        "model":       req.model,
        "messages":    messages,
        "temperature": req.temperature,
        "top_p":       req.top_p,
        "max_tokens":  req.max_tokens,
    }
    headers = {"Authorization": f"Bearer {req.api_key}"}
    # … requests.post …

    usage             = data.get("usage", {})
    prompt_tokens     = usage.get("prompt_tokens", 0)
    completion_tokens = usage.get("completion_tokens", 0)
    total_tokens      = usage.get("total_tokens", prompt_tokens + completion_tokens)
    tokens_per_second = completion_tokens / wall_time if wall_time > 0 else 0.0
    # eval_duration_s = None (no disponible en Groq)
```

---

## Endpoint `/models`

Devuelve los modelos disponibles por proveedor. Para Ollama consulta la API local; para Gemini y Groq devuelve listas estáticas.

```python
@app.get("/models")
def list_models():
    ollama_models = []
    try:
        r = requests.get(OLLAMA_TAGS_URL, timeout=10)
        r.raise_for_status()
        ollama_models = [m["name"] for m in r.json().get("models", [])]
    except Exception:
        pass
    return {
        "ollama": ollama_models,
        "gemini": ["gemini-2.5-flash", "gemini-2.0-flash"],
        "groq":   ["llama-3.3-70b-versatile", "llama3-8b-8192", "mixtral-8x7b-32768"],
    }
```

---

## Manejo de errores

| Situación | Código HTTP | Mensaje |
|---|---|---|
| API key vacía (Gemini/Groq) | 400 | "Se requiere una API key para usar…" |
| Ollama no disponible | 503 | "No se pudo conectar con Ollama…" |
| Timeout | 504 | "La solicitud tardó demasiado" |
| Error HTTP del proveedor | Mismo que el proveedor | Mensaje del proveedor |
| Proveedor desconocido | 400 | "Proveedor desconocido: '…'" |
