---
layout: default
title: Prompt 2 — Embeddings
parent: Práctica 1
nav_order: 2
---

# Prompt 2 — Embeddings

## Prompt utilizado

```
Dame un ejemplo sencillo de uso de embeddings en una búsqueda semántica
dentro de un repositorio de documentos académicos.
```

---

## llama3.2:3b

![Respuesta de llama3.2:3b al prompt 2 — parte 1](assets/img/practica1/llama2.png)

![Respuesta de llama3.2:3b al prompt 2 — parte 2](assets/img/practica1/llama2.1.png)

**Figuras 7 y 8.** Respuesta de `llama3.2:3b` al prompt 2.

Respondió con cuatro pasos estructurados (preprocesamiento, creación de embeddings, similitud, re-ranking) y código en Python usando NumPy. El enfoque fue pedagógico y orientado al proceso paso a paso.

---

## phi3.5:latest

![Respuesta de phi3.5 al prompt 2 — parte 1](assets/img/practica1/phi2.png)

![Respuesta de phi3.5 al prompt 2 — parte 2](assets/img/practica1/phi2.1.png)

**Figuras 9 y 10.** Respuesta de `phi3.5:latest` al prompt 2.

Ofreció un ejemplo más completo usando `gensim` y `Word2Vec`. Incluyó representación vectorial de documentos, cálculo de similitud coseno y recuperación del documento más relevante.

---

## gemma3:4b

![Respuesta de gemma3:4b al prompt 2 — parte 1](assets/img/practica1/gemma2.png)

![Respuesta de gemma3:4b al prompt 2 — parte 2](assets/img/practica1/gemma2.1.png)

![Respuesta de gemma3:4b al prompt 2 — parte 3](assets/img/practica1/gemma2.2.png)

**Figuras 11, 12 y 13.** Respuesta de `gemma3:4b` al prompt 2.

Fue el más detallado de los modelos de 4B. Explicó el proceso en cuatro etapas e incluyó código con `sentence-transformers` y `faiss`, mencionando herramientas de nivel de producción.

---

## qwen2.5:7b

![Respuesta de qwen2.5:7b al prompt 2](assets/img/practica1/qwen2.jpeg)

**Figura 14.** Respuesta de `qwen2.5:7b` al prompt 2.

Respondió con cuatro pasos bien diferenciados y código en Python usando `gensim` y `Word2Vec`. Fue claro en la explicación del cálculo de similitud coseno e incluyó el ranking de documentos.

---

## mistral:7b

![Respuesta de mistral:7b al prompt 2](assets/img/practica1/mistral2.jpeg)

**Figura 15.** Respuesta de `mistral:7b` al prompt 2.

Respondió sin código, con una explicación conceptual en prosa. Describió correctamente el proceso pero no incluyó un ejemplo práctico implementable. Fue el más conciso en este prompt.

---

## tinyllama:1.1b-chat-v1-q8_0

![Respuesta de tinyllama al prompt 2](assets/img/practica1/tiny2.jpeg)

**Figura 16.** Respuesta de `tinyllama:1.1b-chat-v1-q8_0` al prompt 2.

Respondió con un ejemplo muy breve y superficial. Fabricó un enlace de imagen que no existe (alucinación). Evidencia clara de las limitaciones de los modelos de 1B para tareas que requieren precisión técnica.
