---
layout: default
title: Inicio
nav_order: 1
---

# Portafolio — Prospectiva de la Tecnología

Este repositorio documenta las prácticas y el proyecto integrador del curso **Prospectiva de la Tecnología** (IE127), impartido en la Universidad Iberoamericana Ciudad de México durante el verano 2026.

---

## Prácticas

### [Práctica 1 — Instalación y comparación de modelos LLM locales](practica-01.md)

Instalación de Ollama, ejecución de seis modelos LLM con cuatro prompts de prueba, tabla comparativa de modelos y reflexión sobre la experiencia.

### [Práctica 2 — Selección de modelos y benchmark de rendimiento](practica-02.md)

Matriz de decisión para el proyecto integrador, benchmark de tres modelos LLM con 100 ciclos cada uno, y análisis del efecto de parámetros de inferencia sobre calidad y latencia.

### [Práctica 3 — Implementación de chatbot web con LLM local](practica-03.md)

Chatbot web completo con backend FastAPI y frontend HTML/CSS/JS. Incluye panel de controles de parámetros del modelo y visualización en tiempo real de 8 métricas de inferencia de Ollama.

### [Práctica 4 — Diseño de un copiloto especializado](practica-04.md)

Extensión del chatbot de la Práctica 3 para convertirlo en un copiloto especializado. Implementa cuatro perfiles con system prompts diseñados por dominio (asistente genérico, robótica, docente e investigación), historial de conversación multi-turno, endpoint `/profiles` y comparación sistemática entre respuestas genéricas y especializadas.

### [Práctica 5 — Chatbot híbrido con APIs externas](practica-05.md)

Extensión del copiloto de la Práctica 4 para soportar tres proveedores: Ollama local (`qwen2.5:7b`), Gemini API (`gemini-2.5-flash`) y Groq API (`llama-3.3-70b-versatile`). Incluye selector de proveedor, campo de API key, métricas unificadas y comparación cuantitativa y cualitativa del mismo prompt en los tres proveedores.
