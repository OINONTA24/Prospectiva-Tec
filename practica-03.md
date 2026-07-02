---
layout: default
title: Práctica 3
nav_order: 4
has_children: true
---

# Práctica 3 — Implementación de chatbot web con LLM local

Esta práctica corresponde a la asignatura **Prospectiva de la Tecnología** (IE127), impartida en la Universidad Iberoamericana Ciudad de México durante el verano 2026.

El objetivo es diseñar e implementar un chatbot web completo que integre un LLM local ejecutándose con Ollama, con un backend en Python/FastAPI y un frontend HTML/CSS/JS que permita visualizar métricas de inferencia y controlar parámetros del modelo en tiempo real.

---

## Arquitectura general

```
Navegador (frontend HTML/JS)
        │  HTTP POST /chat
        ▼
  FastAPI · Python               ← backend (puerto 8000)
  • Valida parámetros             
  • Mide wall_time con perf_counter
        │  HTTP POST /api/chat
        ▼
  Ollama REST API                ← motor de inferencia (puerto 11434)
  • stream: false → respuesta completa + métricas
        │
        ▼
  gemma3:4b (local)              ← modelo LLM (3.3 GB)
```

| Capa | Tecnología | Función |
|---|---|---|
| Frontend | HTML · CSS · JavaScript | Interfaz de chat con controles de parámetros y panel de métricas |
| Backend | Python · FastAPI · uvicorn | API REST, medición de tiempo y extracción de métricas de Ollama |
| Inferencia | Ollama | Ejecución local del modelo, retorna estadísticas detalladas |
| Modelo | `gemma3:4b` | Google Gemma 3, 4B parámetros, Gemma License |

---

## Parámetros configurables

| Parámetro | Rango | Efecto |
|---|---|---|
| `temperature` | 0.0 – 1.2 | Controla la aleatoriedad: más alto = más creativo |
| `top_p` | 0.1 – 1.0 | Muestreo por nucleus: filtra tokens de baja probabilidad |
| `num_predict` | 20 – 1000 | Número máximo de tokens a generar |
| `num_ctx` | 512 – 8192 | Tamaño de la ventana de contexto |
| `repeat_penalty` | 1.0 – 2.0 | Penaliza repetición de tokens ya generados |

---

## Métricas visualizadas

| Métrica | Fuente | Descripción |
|---|---|---|
| `wall_time_s` | Backend Python | Tiempo total medido en el servidor |
| `total_duration_s` | Ollama | Duración total reportada por Ollama |
| `load_duration_s` | Ollama | Tiempo de carga del modelo en memoria |
| `eval_duration_s` | Ollama | Tiempo de generación de tokens |
| `prompt_eval_count` | Ollama | Tokens del prompt de entrada |
| `eval_count` | Ollama | Tokens generados en la respuesta |
| `total_tokens` | Backend | Suma de tokens entrada + salida |
| `tokens_per_second` | Backend | Velocidad de generación (`eval_count / eval_duration_s`) |

---

## Requisitos

- [Ollama](https://ollama.com/) instalado y en ejecución local
- Python 3.11 o superior
- El modelo `gemma3:4b` descargado:

```bash
ollama pull gemma3:4b
```

---

## Instalación y ejecución

```bash
# 1. Instalar dependencias del backend
cd chatbot/backend
pip install -r requirements.txt

# 2. Iniciar el backend
uvicorn main:app --host 0.0.0.0 --port 8000

# 3. Abrir el frontend
# Abrir chatbot/frontend/index.html en el navegador
```
