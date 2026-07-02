---
layout: default
title: Parte A — Matriz de decisión
parent: Práctica 2
nav_order: 1
---

# Parte A — Matriz de decisión de modelos

La matriz de decisión permite justificar la selección de modelos para cada componente del pipeline del proyecto, considerando criterios técnicos, de rendimiento y de viabilidad para el entorno de ejecución.

---

## Pipeline del proyecto

El sistema de generación de sketches por voz tiene tres componentes de IA:

```
Voz del usuario
      ↓
[STT] Transcripción de audio a texto
      ↓
[LLM] Interpretación y generación de JSON con características del sketch
      ↓
[Generador de imagen] Producción del sketch en estilo coloring book
      ↓
Sketch final
```

Todos los modelos corren en **GPU local**.

---

## Criterios de evaluación

Los criterios utilizados para comparar modelos en cada componente fueron:

- **Precisión** — qué tan bien cumple la tarea principal del componente
- **Velocidad** — latencia aceptable para una interacción en tiempo real
- **Tamaño** — que quepa en la VRAM disponible
- **Licencia** — compatible con uso académico y potencialmente comercial
- **Soporte de idioma** — debe funcionar en español

---

## Selección por componente

### Componente 1 — STT (Speech-to-Text)

| Modelo | Fabricante | Precisión en español | Velocidad | Tamaño | Licencia | Seleccionado |
|---|---|---|---|---|---|---|
| Whisper large-v3-turbo | OpenAI | Muy alta | Alta (turbo) | ~1.5 GB | MIT | ✓ |
| Whisper large-v3 | OpenAI | Muy alta | Media | ~3 GB | MIT | — |
| Whisper medium | OpenAI | Alta | Alta | ~800 MB | MIT | — |

**Modelo seleccionado: `openai/whisper-large-v3-turbo`**

Es la variante optimizada para velocidad del modelo large-v3. Mantiene precisión comparable al modelo completo en español con menor latencia, lo que es crítico para mantener la experiencia fluida del pipeline.

---

### Componente 2 — LLM (Interpretación y generación de JSON)

| Modelo | Fabricante | Generación de JSON | Velocidad | Tamaño | Licencia | Seleccionado |
|---|---|---|---|---|---|---|
| `gemma3:4b` | Google DeepMind | Muy alta | Alta (~21 tok/s) | 3.3 GB | Gemma License | ✓ |
| `phi3.5:latest` | Microsoft | Media | Alta (~31 tok/s) | 2.2 GB | MIT | — |
| `qwen2.5:7b` | Alibaba Cloud | Muy alta | Media (~12 tok/s) | 4.7 GB | Apache 2.0 | — |

**Modelo seleccionado: `gemma3:4b`**

El benchmark de la Parte B confirmó que gemma3:4b obtuvo calidad perfecta (10/10) en todos los ciclos: siempre generó JSON válido con los cuatro campos requeridos sin texto adicional. Su tiempo promedio de 2.69 s fue el más bajo del grupo y sus respuestas son consistentes en longitud (desviación estándar de apenas 0.27 tokens de salida). Para un sistema en tiempo real donde la salida debe ser JSON parseable de forma confiable, la consistencia de gemma3:4b es más valiosa que la velocidad en tokens/s de phi3.5.

---

### Componente 3 — Generador de imagen (Sketch en estilo coloring book)

| Modelo | Fabricante | Calidad de line art | Velocidad | VRAM requerida | Licencia | Seleccionado |
|---|---|---|---|---|---|---|
| *(por definir)* | — | — | — | — | — | — |

> Esta sección se completará después de realizar las pruebas comparativas de generación de imagen con los modelos candidatos.

---

## Configuración final del pipeline

| Componente | Modelo seleccionado | Ejecución |
|---|---|---|
| STT | `openai/whisper-large-v3-turbo` | GPU local |
| LLM | `gemma3:4b` | GPU local (Ollama) |
| Generador de imagen | *(por definir)* | GPU local |
