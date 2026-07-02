---
layout: default
title: Práctica 4
nav_order: 5
has_children: true
---

# Práctica 4 — Diseño de un copiloto especializado

Esta práctica corresponde a la asignatura **Prospectiva de la Tecnología** (IE127), impartida en la Universidad Iberoamericana Ciudad de México durante el verano 2026.

El objetivo es extender el chatbot construido en la Práctica 3 para convertirlo en un **copiloto especializado**: un asistente cuyo comportamiento está definido por instrucciones de sistema persistentes (system prompts) que delimitan su dominio, audiencia, formato de respuesta y reglas de seguridad.

---

## Del chatbot genérico al copiloto especializado

Un chatbot genérico responde con base en el conocimiento general del modelo. Un copiloto especializado agrega una capa de instrucción que define quién es el asistente, qué puede y qué no puede hacer, y cómo debe comunicarse:

```
Chatbot genérico       = modelo base + prompt de usuario
Copiloto especializado = instrucción de sistema + historial de conversación + prompt de usuario
```

La diferencia no está en el modelo (es el mismo `gemma3:4b`) sino en el **contexto persistente** que se envía en cada solicitud.

---

## Arquitectura

```
Navegador (frontend HTML/JS)
        │  POST /chat  { message, history[], system_prompt, copilot_id, … }
        ▼
  FastAPI · Python               ← backend puerto 8000
  • Selecciona perfil por copilot_id
  • Construye messages[] con historial completo
  • Mide wall_time con perf_counter
        │  POST /api/chat  (messages: [system, …history, user])
        ▼
  Ollama REST API                ← puerto 11434  (stream: false)
        │
        ▼
  gemma3:4b (local)              ← modelo LLM · 3.3 GB
```

| Capa | Tecnología | Novedad respecto a Práctica 3 |
|---|---|---|
| Frontend | HTML · CSS · JavaScript | Selector de perfil, pill de copiloto activo, etiqueta de sender |
| Backend | Python · FastAPI · uvicorn | `PROFILES` dict, `HistoryMessage`, endpoint `/profiles`, historial en `/chat` |
| Inferencia | Ollama | Sin cambios |
| Modelo | `gemma3:4b` | Sin cambios |

---

## Perfiles implementados

Se diseñaron cuatro perfiles, seleccionables desde el frontend. Sus system prompts están escritos en inglés para maximizar la adherencia del modelo, con una política de lenguaje que le indica responder en el idioma del usuario.

| ID | Etiqueta | Dominio |
|---|---|---|
| `generico` | Asistente genérico | Sin especialización — línea base de comparación |
| `robotica` | Copiloto de robótica | Robótica, automatización, ROS2, sensores, control, Arduino |
| `docente` | Copiloto docente | Explicación pedagógica adaptada al nivel del estudiante |
| `investigacion` | Copiloto de investigación | Literatura, metodología, análisis crítico, RAG-readiness |

### Asistente genérico
Responde de forma neutral y directa, sin especialización de dominio. Sirve como punto de comparación para evaluar el impacto de los system prompts especializados. Su instrucción principal es ser conciso por defecto y adaptar el nivel de detalle a la complejidad de la pregunta.

### Copiloto de robótica
Asiste a estudiantes e ingenieros con robótica, mecatrónica, ROS2, sistemas embebidos, Arduino, sensores, visión por computadora y control. Prioriza soluciones prácticas, usa terminología técnica apropiada y pide aclaración cuando falta información (por ejemplo, especificaciones de hardware). No inventa medidas ni especificaciones.

### Copiloto docente
Ayuda a estudiantes a comprender temas académicos de cualquier disciplina. Adapta las explicaciones al nivel del interlocutor, parte de la idea principal antes de agregar detalles y usa ejemplos cuando mejoran la comprensión. Para preguntas simples responde en 1–3 oraciones; para temas complejos estructura la explicación paso a paso.

### Copiloto de investigación
Asiste en tareas de investigación académica: exploración de literatura, planeación, análisis crítico, selección de metodología, desarrollo de hipótesis e interpretación de datos. Distingue explícitamente entre hechos, interpretaciones y supuestos. No inventa fuentes, citas ni estadísticas. Cuando evalúa un claim, sigue una estructura de cuatro pasos: enunciar → analizar evidencia → identificar limitaciones → conclusión balanceada.

---

## Requisitos cumplidos

| # | Requisito | Estado |
|---|---|---|
| 1 | Selector de perfil de copiloto en frontend | ✅ |
| 2 | Al menos 3 perfiles de copiloto | ✅ (4 perfiles) |
| 3 | Campo editable para `system_prompt` | ✅ |
| 4 | Backend usa `system_prompt` en `messages[0]` | ✅ |
| 5 | Endpoint `/profiles` | ✅ |
| 6 | Visualización de respuesta y métricas | ✅ (8 métricas) |
| 7 | Comparación entre asistente genérico y copiloto especializado | ✅ (ver Tabla de pruebas) |
| 8 | Pruebas con mínimo 3 prompts por perfil | ✅ (3 prompts + follow-up por perfil) |
| 9 | Reflexión sobre calidad, utilidad, límites y riesgos | ✅ (ver Reflexión técnica) |

---

## Ejecución

```bash
# 1. Instalar dependencias del backend
cd chatbot-p4/backend
pip install -r requirements.txt

# 2. Iniciar el backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000

# 3. Abrir el frontend
# Arrastrar chatbot-p4/frontend/index.html al navegador
```

> El frontend no requiere servidor web — basta con abrir el archivo HTML directamente en el navegador. El backend debe estar corriendo en `http://localhost:8000`.

---

## Notas técnicas

### Idioma de respuesta
Los system prompts incluyen una política de lenguaje explícita: *"Respond in the same language used by the user."* En la mayoría de las pruebas `gemma3:4b` respeta esta instrucción y responde en español cuando el usuario escribe en español. Sin embargo, en preguntas de alta densidad semántica (especialmente con el perfil de Investigación), el modelo ocasionalmente respondió en inglés. Este comportamiento es un límite conocido de la instrucción de sistema: el modelo no siempre aplica la política de idioma con consistencia absoluta. Se documentó en la Tabla de pruebas y se discute en la Reflexión técnica.

### Longitud de respuesta en el perfil de Investigación
El perfil de Investigación tiene instrucciones estructurales detalladas (evaluación de claims en 4 pasos, plan de investigación en 5 pasos) que llevan al modelo a generar respuestas de 600+ tokens incluso para preguntas moderadas. El parámetro `num_predict` por defecto (160) resulta insuficiente para este perfil; sería recomendable aumentarlo a 400–600 al seleccionar ese perfil. Esta configuración no se implementó por diseño, pero queda documentada como área de mejora.

### Historial de conversación
A partir de esta práctica el backend recibe un array `history[]` con los turnos anteriores de la conversación. Cada turno exitoso se almacena en el frontend y se envía en el siguiente request, permitiendo follow-ups contextuales. El historial se resetea al presionar el botón de nueva conversación. El crecimiento acumulativo de tokens de entrada (visible en la tabla de métricas) confirma que el historial se transmite correctamente.
