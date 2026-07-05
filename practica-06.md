---
layout: default
title: Práctica 6
nav_order: 7
has_children: true
---

# Práctica 6 — Evaluación de arquitectura LLM: clasificación semántica para el brazo robótico UR3

Esta práctica corresponde a la asignatura **Prospectiva de la Tecnología** (IE127), impartida en la Universidad Iberoamericana Ciudad de México durante el verano 2026.

El objetivo es aplicar la metodología de *Evaluación de arquitecturas LLM aplicadas: backend, JSON y MQTT* al caso de estudio del **Proyecto Final** de esta asignatura: un gemelo digital que controla un brazo robótico UR3 para dibujar a partir de instrucciones de voz. En lugar del caso de referencia (clasificación `on / off / none` para un LED), esta evaluación mide la capa semántica real del proyecto: decidir si una transcripción de voz es una **instrucción de dibujo válida** (`draw`) o **ruido / conversación ajena** (`none`), y extraer la intención en un JSON estructurado con posición, acción y relaciones espaciales.

---

## Adaptación respecto al caso de estudio de referencia

| Elemento | Caso de referencia (guía) | Esta práctica (UR3) |
| --- | --- | --- |
| Clases | `on`, `off`, `none` | `draw`, `none` |
| Modelo | Ollama local (`llama3.2:3b`) | Groq Cloud API (`llama-3.3-70b-versatile`) |
| Salida del LLM | `{action, confidence, reason}` | `{objects: [{name, position, action, relative_to}]}` |
| Backend / MQTT | FastAPI + `paho-mqtt` publicando a un broker | No implementado en esta evaluación — ver nota de alcance |
| Actuador físico | ESP32 + LED | UR3 (fuera del alcance de esta prueba aislada) |

**Nota de alcance:** esta evaluación aísla deliberadamente la capa de *interpretación semántica* (LLM → JSON) del resto de la arquitectura del Proyecto Final. No se levantó un backend FastAPI ni un broker MQTT: `eval_100.py` llama directamente a la API de Groq y guarda los resultados en archivos planos. Esto permite repetir las 100 pruebas cíclicas sin depender del hardware ni de la disponibilidad de un broker, tal como sugiere la guía de la práctica. La validación de backend y la publicación MQTT quedan como trabajo futuro sobre el mismo dataset.

---

## Caso de estudio: clasificación de intención de dibujo

| Clase | Significado | Acción asociada |
| --- | --- | --- |
| `draw` | El usuario pide dibujar uno o más objetos, con o sin posición/acción/relación espacial | Extraer objetos y enviarlos al pipeline de dibujo |
| `none` | Ruido de fondo, plática casual, pregunta teórica o instrucción no inmediata/ambigua | No generar ningún objeto; el UR3 no se mueve |

Ejemplos del banco de pruebas:

| Prompt (simulando salida de Whisper) | Etiqueta esperada |
| --- | --- |
| `dibuja un astronauta flotando a la derecha` | `draw` |
| `pinta una manzana roja... no mejor dibuja un coche azul en el centro` | `draw` (autocorrección) |
| `¿Qué es el protocolo de comunicación MQTT y cómo funciona?` | `none` |
| `mañana tal vez usemos el lienzo para pintar algo creativo` | `none` (intención no inmediata) |

---

## Arquitectura evaluada

```
Transcripción simulada de Whisper (texto)
        │
        ▼
  eval_100.py  ──▶  Groq Cloud API
                     • modelo: llama-3.3-70b-versatile
                     • temperature = 0.1
                     • response_format = json_object
                     • prompt few-shot (8 reglas + 3 ejemplos)
        │
        ▼
  Validación JSON (json.loads) ──▶ schema_valid
        │
        ▼
  ¿objects.length > 0?  ──▶  llm_action = "draw" | "none"
        │
        ▼
  resultados_llm_led_raw.csv  +  instrumento_supervision_llm_led.xlsx
        │
        ▼
  analizar_resultados.py  ──▶  classification_report.csv + confusion_matrix.png
```

El backend (validación de esquema + publicación MQTT + envío al UR3) existe conceptualmente en el Proyecto Final, pero no se ejecuta en esta prueba: la "validación de backend" se simula con `json.loads()` dentro del propio script de evaluación.

---

## Resumen ejecutivo

| Elemento | Resultado |
| --- | --- |
| Modelo usado | Llama 3.3 70B (`llama-3.3-70b-versatile`) vía Groq Cloud API |
| Número de pruebas | 100 (50 `draw` / 50 `none`) |
| Accuracy | 1.0000 |
| Macro F1-score | 1.0000 |
| JSON validity rate (`schema_valid`) | 1.0000 |
| MQTT publish rate | N/D — no implementado en esta evaluación aislada |
| Latencia media | 2236.90 ms |
| Latencia P95 / P99 | 3640.23 ms / 3764.02 ms |
| Tokens de entrada promedio | 630.3 |
| Tokens de salida promedio | 32.8 |
| Costo estimado | No calculado (Groq free tier) |
| Principal error observado | Ninguno — 0 falsos positivos y 0 falsos negativos en 100 pruebas |
| Mejora propuesta | Reducir el prompt few-shot (~630 → <400 tokens de entrada) y ampliar el dataset con paráfrasis reales |

---