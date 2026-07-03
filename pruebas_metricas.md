---
layout: default
title: Pruebas y métricas
parent: proyecto_final
nav_order: 1
---

# Pruebas de Rendimiento y Métricas del Sistema

Para evaluar la viabilidad de la arquitectura del Gemelo Digital y la comunicación en tiempo real con el hardware físico, se realizaron pruebas sistemáticas midiendo la latencia de red y el costo computacional de los modelos de Inteligencia Artificial.

## 1. Análisis de Latencia por Modelo

Durante los ciclos de prueba, se cronometró el tiempo de respuesta de cada componente del *pipeline* tras recibir un comando de voz. Los resultados de ejecución son los siguientes:

| Fase | Modelo / Herramienta | Función | Latencia |
| :--- | :--- | :--- | :--- |
| 1 | Whisper (base) | Speech-to-Text (STT) | 0.52 s |
| 1 | Llama-3.3-70b (Groq) | Extracción de JSON (LLM) | 0.48 s |
| 2 | OpenAI (DALL-E 2) | Generación de silueta vectorial | 14.64 s |
| 3 | OpenCV | Procesamiento y segmentación UV | 0.07 s |
| **Total** | **Pipeline Completo** | **Desde la voz hasta la ejecución** | **16.28 s** |

## 2. Tokenización y Costos de Inferencia

El uso de modelos alojados en la nube requiere una gestión eficiente para escalar el proyecto. Para el procesamiento de las instrucciones espaciales se registró el siguiente consumo:

* **Tokens de entrada (Prompt del Sistema + Usuario):** 92 tokens.
* **Tokens de salida (Objeto JSON estructurado):** 781 tokens.
* **Total:** 873 tokens por iteración.

**Costo de Generación Visual:**
La generación de cada imagen mediante la API de OpenAI (modelo `gpt-image-2` a resolución 1024x1024) tiene un costo de **$0.02 USD** por llamada.