---
title: Reporte Final y Reflexión
layout: default
parent: Evaluación y Métricas
nav_order: 3
---

# Reporte Final: Integración de Gemelo Digital, IA y Robótica Física

Este documento consolida los resultados finales, métricas de rendimiento y la reflexión general sobre la construcción del sistema que integra las gafas Meta Quest 3, modelos de Inteligencia Artificial y el brazo robótico UR3.

## 1. Análisis de Latencia por Modelo

Durante las pruebas finales de integración, se midieron los tiempos de respuesta de cada modelo involucrado en el *pipeline* tras recibir un comando de voz (ej. "Dibujé un perro"). Los resultados son los siguientes:

| Modelo / Proceso | Función | Latencia (segundos) |
| :--- | :--- | :--- |
| **Whisper (base)** | Speech-to-Text (STT) | 0.52 s |
| **Llama-3.3-70b (Groq)** | Procesamiento de Lenguaje Natural (LLM) | 0.48 s |
| **DALL-E 2 (OpenAI)** | Generación de Imagen | 14.64 s |
| **OpenCV** | Procesamiento y cálculo de coordenadas UV | 0.07 s |
| **Total del Pipeline** | **Tiempo desde la voz hasta el envío al robot** | **16.28 s** |

### Justificación de Latencia
Como se observa, el cuello de botella del sistema es la generación de la imagen mediante DALL-E (14.64 segundos). A pesar de esto, se decidió mantener este modelo debido a su superioridad en la **calidad semántica y comprensión espacial**. Para el éxito del proyecto, era más crítico que el robot dibujara exactamente lo que el usuario pidió (y en la posición correcta) que sacrificar precisión por unos segundos de velocidad. Los modelos locales (Whisper y OpenCV) y el LLM acelerado por LPU (Groq) demostraron ser extremadamente eficientes, ejecutándose en fracciones de segundo.

## 2. Análisis de Tokenización y Costos

El uso de modelos de lenguaje en la nube implica un costo computacional medido en "tokens". Para el procesamiento de las instrucciones mediante la API:

*   **Tokens de entrada (Prompt):** 92 tokens.
*   **Tokens de salida (Respuesta JSON):** 781 tokens.
*   **Total:** 873 tokens por iteración.

**Costo de Generación de Imagen:**
La generación de cada silueta vectorial mediante la API de OpenAI (modelo `gpt-image-2` a resolución 1024x1024) tiene un costo aproximado de **$0.02 USD** por imagen. Este costo es altamente justificable dado que la imagen es el puente vital entre la intención del usuario y la matriz de coordenadas que el robot necesita para moverse.

## 3. Retos y Problemáticas Enfrentadas

Durante el desarrollo, nos enfrentamos a desafíos técnicos significativos:

1.  **Arquitectura de Red y Firewall:** Lograr que las Meta Quest 3 (en una red Wi-Fi universitaria pública) se comunicaran con el servidor Flask local requirió diagnósticos de red exhaustivos y la configuración de excepciones en el Firewall de Windows.
2.  **Sintaxis y Tipos de Datos en Robótica:** En la integración con el hardware físico, la librería `urx` presentó errores de tipado (ej. tratar de iterar un objeto `PoseVector`). Esto exigió refactorizar la lógica de movimiento para asegurar que el efector final (el plumón) se levantara y bajara usando coordenadas XYZ absolutas en lugar de referencias relativas.
3.  **Filtrado de Contornos:** OpenCV detectaba inicialmente demasiado "ruido" en las imágenes generadas por IA. Fue necesario implementar el algoritmo de Douglas-Peucker con una tolerancia específica (`epsilon = 0.001`) y lógica para ignorar trazos duplicados o demasiado pequeños.

## 4. Áreas de Mejora y Trabajo Futuro

Si bien el sistema es funcional, existen áreas claras para iteraciones futuras:

*   **Sustitución de DALL-E:** Explorar modelos de difusión locales (como Stable Diffusion optimizado con TensorRT) para reducir los 14 segundos de latencia y eliminar el costo de $0.02 USD por llamada a la API.
*   **Feedback Visual en Tiempo Real:** Mejorar el Gemelo Digital en Unity para que muestre el estado de "Procesando..." mientras espera la respuesta del servidor, mejorando la experiencia del usuario (UX) en las Meta Quest.
*   **Calibración Dinámica:** Actualmente, las medidas del pizarrón y el espacio de trabajo del UR3 están *hardcodeadas* (quemadas en el código). Implementar una rutina de calibración visual mediante la cámara del robot lo haría adaptable a cualquier entorno.

## 5. Reflexión Final

Este proyecto demostró con éxito la viabilidad de crear interfaces humano-máquina verdaderamente naturales. Al combinar la inmersión de la Realidad Extendida (XR), el razonamiento de los Modelos de Lenguaje Grande (LLMs) y la precisión de la robótica industrial, logramos un sistema donde la voz se convierte en movimiento físico. 

El mayor aprendizaje de esta integración fue comprender que **la robótica moderna ya no depende solo de programar trayectorias manuales**, sino de orquestar flujos de datos donde las IAs actúan como traductores entre la intención humana y el código de máquina. El éxito del Gemelo Digital y la ejecución física en el UR3 validan esta arquitectura híbrida como un modelo a seguir para futuros proyectos de automatización inteligente.