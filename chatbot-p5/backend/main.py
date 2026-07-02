import time
import requests
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

OLLAMA_BASE     = "http://localhost:11434"
OLLAMA_CHAT_URL = f"{OLLAMA_BASE}/api/chat"
OLLAMA_TAGS_URL = f"{OLLAMA_BASE}/api/tags"

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
GROQ_URL   = "https://api.groq.com/openai/v1/chat/completions"

PROVIDER_MODELS = {
    "gemini": ["gemini-2.5-flash", "gemini-2.0-flash"],
    "groq":   ["llama-3.3-70b-versatile", "llama3-8b-8192", "mixtral-8x7b-32768"],
}

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
        "label": "Copiloto de robótica móvil",
        "description": "Especialista en robótica, automatización, ROS2, sensores, control y mecatrónica.",
        "system_prompt": (
            "You are a robotics engineering copilot.\n\n"
            "You help students, researchers, and engineers with:\n\n"
            "- Robotics\n"
            "- Automation\n"
            "- Mechatronics\n"
            "- ROS2\n"
            "- Embedded systems\n"
            "- Arduino and microcontrollers\n"
            "- Sensors and actuators\n"
            "- Computer vision\n"
            "- Control systems\n"
            "- Industrial robotics\n"
            "- AI applications in robotics\n\n"
            "Guidelines:\n\n"
            "- Answer directly and concisely.\n"
            "- For simple questions, use 2–5 sentences.\n"
            "- For complex topics, provide structured explanations.\n"
            "- Explain concepts clearly and practically.\n"
            "- Use technical terminology when appropriate.\n"
            "- Show formulas only when they help solve the problem.\n"
            "- Ask clarifying questions when information is missing.\n"
            "- State uncertainties clearly.\n"
            "- Do not invent specifications, measurements, or facts.\n"
            "- Prioritize practical engineering solutions.\n"
            "- Focus on helping the user solve the problem efficiently.\n\n"
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
            "You can explain concepts, answer questions, solve problems, and guide learning across "
            "different subjects.\n\n"
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
            "- Do not invent facts, sources, or references.\n"
            "- Avoid unnecessary repetition and filler text.\n\n"
            "Response Length Policy:\n"
            "- Simple questions: 1–3 sentences.\n"
            "- Medium complexity: concise explanation.\n"
            "- Complex topics: structured explanation with examples.\n"
            "- Expand only when needed or requested.\n\n"
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
            "You are a research copilot that assists students, academics, and professionals with "
            "research tasks.\n\n"
            "You help with:\n\n"
            "- Literature exploration\n"
            "- Research planning\n"
            "- Topic analysis\n"
            "- Critical evaluation of information\n"
            "- Methodology selection\n"
            "- Hypothesis development\n"
            "- Data interpretation\n"
            "- Academic writing support\n"
            "- Comparative analysis\n"
            "- Evidence-based reasoning\n\n"
            "Guidelines:\n\n"
            "- Prioritize accuracy, clarity, and evidence-based reasoning.\n"
            "- Distinguish clearly between facts, interpretations, assumptions, and hypotheses.\n"
            "- Identify limitations, uncertainties, and potential biases when relevant.\n"
            "- Do not invent sources, citations, studies, statistics, or references.\n"
            "- If evidence is unavailable or uncertain, state it explicitly.\n"
            "- Ask clarifying questions when the research objective is unclear.\n"
            "- Present information in a logical and structured manner.\n"
            "- Focus on analysis and reasoning rather than unsupported conclusions.\n"
            "- Remain objective and neutral.\n"
            "- Adapt explanations to the user's level of expertise.\n\n"
            "Language Policy:\n"
            "- Respond in the same language used by the user.\n"
            "- If the user switches languages, adapt accordingly.\n"
            "- Do not translate unless requested."
        ),
    },
}

app = FastAPI(title="Sage — Chatbot híbrido con APIs externas", version="3.0.0")

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
    provider:       str                  = Field(default="ollama")
    model:          str                  = Field(default="gemma3:4b")
    api_key:        str                  = Field(default="")
    temperature:    float                = Field(default=0.7,  ge=0.0, le=2.0)
    top_p:          float                = Field(default=0.9,  ge=0.1, le=1.0)
    max_tokens:     int                  = Field(default=300,  ge=20,  le=2048)
    num_ctx:        int                  = Field(default=4096, ge=512, le=8192)
    repeat_penalty: float                = Field(default=1.1,  ge=1.0, le=2.0)
    system_prompt:  str                  = Field(default="You are a helpful, neutral, and knowledgeable AI assistant.")
    copilot_id:     str                  = Field(default="generico")


class ChatMetrics(BaseModel):
    wall_time_s:       float
    prompt_tokens:     int
    completion_tokens: int
    total_tokens:      int
    tokens_per_second: float
    eval_duration_s:   Optional[float] = None
    load_duration_s:   Optional[float] = None


class ChatResponse(BaseModel):
    provider:      str
    model:         str
    copilot_label: str
    reply:         str
    metrics:       ChatMetrics


@app.get("/")
def root():
    return {
        "message":  "Sage — Chatbot híbrido con APIs externas",
        "docs":     "/docs",
        "health":   "/health",
        "profiles": "/profiles",
        "models":   "/models",
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
    ollama_models = []
    try:
        r = requests.get(OLLAMA_TAGS_URL, timeout=10)
        r.raise_for_status()
        ollama_models = [m["name"] for m in r.json().get("models", [])]
    except Exception:
        pass
    return {
        "ollama": ollama_models,
        "gemini": PROVIDER_MODELS["gemini"],
        "groq":   PROVIDER_MODELS["groq"],
    }


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
    provider = req.provider.lower()
    if provider == "ollama":
        return _chat_ollama(req)
    elif provider == "gemini":
        return _chat_gemini(req)
    elif provider == "groq":
        return _chat_groq(req)
    else:
        raise HTTPException(status_code=400, detail=f"Proveedor desconocido: '{req.provider}'")


def _get_copilot_label(copilot_id: str) -> str:
    return PROFILES.get(copilot_id, PROFILES["generico"])["label"]


def _chat_ollama(req: ChatRequest) -> ChatResponse:
    messages = [{"role": "system", "content": req.system_prompt}]
    for h in req.history:
        messages.append({"role": h.role, "content": h.content})
    messages.append({"role": "user", "content": req.message})

    payload = {
        "model":      req.model,
        "messages":   messages,
        "stream":     False,
        "keep_alive": "5m",
        "options": {
            "temperature":    req.temperature,
            "top_p":          req.top_p,
            "num_predict":    req.max_tokens,
            "num_ctx":        req.num_ctx,
            "repeat_penalty": req.repeat_penalty,
        },
    }

    try:
        t0 = time.perf_counter()
        r  = requests.post(OLLAMA_CHAT_URL, json=payload, timeout=300)
        t1 = time.perf_counter()
        r.raise_for_status()
        data = r.json()
    except requests.exceptions.ConnectionError as exc:
        raise HTTPException(
            status_code=503,
            detail="No se pudo conectar con Ollama. Verifica que esté ejecutándose.",
        ) from exc
    except requests.exceptions.Timeout as exc:
        raise HTTPException(status_code=504, detail="La solicitud a Ollama tardó demasiado.") from exc
    except requests.exceptions.HTTPError as exc:
        raise HTTPException(status_code=r.status_code, detail=f"Error de Ollama: {r.text}") from exc

    reply             = data.get("message", {}).get("content", "")
    prompt_tokens     = data.get("prompt_eval_count", 0)
    completion_tokens = data.get("eval_count", 0)
    total_tokens      = prompt_tokens + completion_tokens
    eval_duration_s   = data.get("eval_duration", 0) / 1e9
    load_duration_s   = data.get("load_duration", 0) / 1e9
    tokens_per_second = completion_tokens / eval_duration_s if eval_duration_s > 0 else 0.0

    return ChatResponse(
        provider=      "ollama",
        model=         req.model,
        copilot_label= _get_copilot_label(req.copilot_id),
        reply=         reply,
        metrics=ChatMetrics(
            wall_time_s=       round(t1 - t0, 4),
            prompt_tokens=     prompt_tokens,
            completion_tokens= completion_tokens,
            total_tokens=      total_tokens,
            tokens_per_second= round(tokens_per_second, 2),
            eval_duration_s=   round(eval_duration_s, 4),
            load_duration_s=   round(load_duration_s, 4),
        ),
    )


def _chat_gemini(req: ChatRequest) -> ChatResponse:
    if not req.api_key.strip():
        raise HTTPException(status_code=400, detail="Se requiere una API key para usar Gemini.")

    contents = []
    for h in req.history:
        role = "model" if h.role == "assistant" else "user"
        contents.append({"role": role, "parts": [{"text": h.content}]})
    contents.append({"role": "user", "parts": [{"text": req.message}]})

    payload = {
        "system_instruction": {"parts": [{"text": req.system_prompt}]},
        "contents": contents,
        "generationConfig": {
            "temperature":     req.temperature,
            "topP":            req.top_p,
            "maxOutputTokens": req.max_tokens,
            "thinkingConfig":  {"thinkingBudget": 0},
        },
    }

    url = GEMINI_URL.format(model=req.model) + f"?key={req.api_key}"

    try:
        t0 = time.perf_counter()
        r  = requests.post(url, json=payload, timeout=60)
        t1 = time.perf_counter()
        r.raise_for_status()
        data = r.json()
    except requests.exceptions.ConnectionError as exc:
        raise HTTPException(status_code=503, detail="No se pudo conectar con Gemini API.") from exc
    except requests.exceptions.Timeout as exc:
        raise HTTPException(status_code=504, detail="La solicitud a Gemini API tardó demasiado.") from exc
    except requests.exceptions.HTTPError as exc:
        err_msg = r.json().get("error", {}).get("message", r.text)
        raise HTTPException(status_code=r.status_code, detail=f"Error de Gemini API: {err_msg}") from exc

    reply = ""
    candidates = data.get("candidates", [])
    if candidates:
        parts = candidates[0].get("content", {}).get("parts", [])
        reply = "".join(p.get("text", "") for p in parts)

    usage             = data.get("usageMetadata", {})
    prompt_tokens     = usage.get("promptTokenCount", 0)
    completion_tokens = usage.get("candidatesTokenCount", 0)
    total_tokens      = usage.get("totalTokenCount", prompt_tokens + completion_tokens)
    wall_time         = round(t1 - t0, 4)
    tokens_per_second = completion_tokens / wall_time if wall_time > 0 else 0.0

    return ChatResponse(
        provider=      "gemini",
        model=         req.model,
        copilot_label= _get_copilot_label(req.copilot_id),
        reply=         reply,
        metrics=ChatMetrics(
            wall_time_s=       wall_time,
            prompt_tokens=     prompt_tokens,
            completion_tokens= completion_tokens,
            total_tokens=      total_tokens,
            tokens_per_second= round(tokens_per_second, 2),
        ),
    )


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

    headers = {
        "Authorization": f"Bearer {req.api_key}",
        "Content-Type":  "application/json",
    }

    try:
        t0 = time.perf_counter()
        r  = requests.post(GROQ_URL, json=payload, headers=headers, timeout=60)
        t1 = time.perf_counter()
        r.raise_for_status()
        data = r.json()
    except requests.exceptions.ConnectionError as exc:
        raise HTTPException(status_code=503, detail="No se pudo conectar con Groq API.") from exc
    except requests.exceptions.Timeout as exc:
        raise HTTPException(status_code=504, detail="La solicitud a Groq API tardó demasiado.") from exc
    except requests.exceptions.HTTPError as exc:
        err_msg = r.json().get("error", {}).get("message", r.text)
        raise HTTPException(status_code=r.status_code, detail=f"Error de Groq API: {err_msg}") from exc

    reply             = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    usage             = data.get("usage", {})
    prompt_tokens     = usage.get("prompt_tokens", 0)
    completion_tokens = usage.get("completion_tokens", 0)
    total_tokens      = usage.get("total_tokens", prompt_tokens + completion_tokens)
    wall_time         = round(t1 - t0, 4)
    tokens_per_second = completion_tokens / wall_time if wall_time > 0 else 0.0

    return ChatResponse(
        provider=      "groq",
        model=         req.model,
        copilot_label= _get_copilot_label(req.copilot_id),
        reply=         reply,
        metrics=ChatMetrics(
            wall_time_s=       wall_time,
            prompt_tokens=     prompt_tokens,
            completion_tokens= completion_tokens,
            total_tokens=      total_tokens,
            tokens_per_second= round(tokens_per_second, 2),
        ),
    )
