---
layout: default
title: Tabla comparativa
parent: Práctica 1
nav_order: 5
---

# Tabla comparativa de modelos

Los datos se obtuvieron de las model cards en Hugging Face, la biblioteca de Ollama y la salida de `ollama ls` en terminal.

> El tamaño en Ollama depende de la cuantización descargada. No es equivalente al número de parámetros. El dato se obtiene con `ollama ls`.

| Modelo | Fabricante / desarrollador | Tipo | Licencia | Parámetros | Idiomas reportados | Requerimiento sugerido para clase | Comando sugerido | Tamaño en Ollama |
|---|---|---|---|---|---|---|---|---|
| `gemma3:4b` | Google DeepMind | LLM instruct multimodal (texto + imagen → texto) | Gemma License | 4B | Más de 140 idiomas | 8 GB RAM o más; Ollama 0.6 o posterior | `ollama run gemma3:4b` | 3.3 GB |
| `llama3.2:3b` | Meta | LLM instruct (texto → texto) | Llama 3.2 Community License | 3.21B | Inglés, alemán, francés, italiano, portugués, hindi, español, tailandés | 8 GB RAM o más | `ollama run llama3.2:3b` | 2.0 GB |
| `phi3.5:latest` | Microsoft | LLM instruct (texto → texto) | MIT | 3.8B | Multilingüe: árabe, chino, inglés, español, francés, alemán, japonés, y otros | 8 GB RAM; puede ejecutarse en CPU | `ollama run phi3.5:latest` | 2.2 GB |
| `qwen2.5:7b` | Qwen / Alibaba Cloud | LLM instruct (texto → texto) | Apache 2.0 | 7.61B | Más de 29 idiomas: chino, inglés, francés, español, portugués, alemán, italiano, ruso, japonés, coreano, árabe, y otros | 16 GB RAM recomendado; mejor con GPU | `ollama run qwen2.5:7b` | 4.7 GB |
| `mistral:7b` | Mistral AI | LLM instruct (texto → texto) | Apache 2.0 | 7.3B | Sin lista oficial cerrada; evaluado en inglés y español con buen desempeño | 16 GB RAM recomendado; mejor con GPU | `ollama run mistral:7b` | 4.1 GB |
| `tinyllama:1.1b-chat-v1-q8_0` | TinyLlama | LLM chat compacto (texto → texto) | Apache 2.0 | 1.1B | Principalmente inglés | Útil para equipos con recursos muy limitados; menor calidad esperada | `ollama run tinyllama:1.1b-chat-v1-q8_0` | 1.2 GB |

---

## Notas sobre los datos

**Licencias:** Gemma y Llama usan licencias propietarias que restringen redistribución y uso comercial sin autorización. Qwen, Mistral y TinyLlama usan Apache 2.0, y Phi-3.5 usa MIT — ambas permisivas para uso académico y comercial.

**Tamaños en Ollama:** Los tamaños de `qwen2.5:7b` (4.7 GB) y `mistral:7b` (4.1 GB) se obtuvieron de la captura de `ollama pull` de cada modelo.

**TinyLlama:** La variante `1.1b-chat-v1-q8_0` es una cuantización Q8_0 del modelo base de 1.1B parámetros. Pesa 1.2 GB según la biblioteca de Ollama.
