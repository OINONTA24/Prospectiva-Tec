---
layout: default
title: Reflexión comparativa
parent: Reporte Final
nav_order: 3
---

# Reflexión Técnica, Retos y Trabajo Futuro

La construcción del proyecto integrador exigió resolver problemas de conectividad, depurar código de hardware y gestionar el comportamiento no determinista de los modelos de lenguaje.

## 1. Retos y Problemáticas Enfrentadas

* **Arquitectura y Firewall:** Establecer comunicación bidireccional entre el entorno XR (Meta Quest 3) y el servidor Flask local requirió diagnósticos de red exhaustivos, superando bloqueos de puertos y protocolos de seguridad en la red Wi-Fi universitaria.
* **Excepciones de Hardware Robótico:** En la conexión con el UR3 físico, la librería de control generó excepciones críticas de tipado (ej. el error de iteración del objeto `PoseVector`). Esto forzó una refactorización de la lógica cinemática para controlar la altura Z del efector final utilizando coordenadas absolutas y seguras.
* **Ruido en Visión Computacional:** La binarización de las imágenes generadas por IA presentaba irregularidades que el robot intentaba dibujar como trazos erráticos. Fue indispensable implementar el algoritmo de Douglas-Peucker en OpenCV con un factor estricto (`epsilon`) para simplificar y suavizar los vectores.

## 2. Reflexión sobre Modelos e Instrucciones del Sistema

Al adaptar los aprendizajes de los copilotos especializados hacia un sistema de control de hardware, observamos dinámicas cruciales:

1. **La Utilidad del Perfil Especializado:** Un asistente LLM genérico habría fracasado en esta tarea al responder de manera conversacional. El uso de un *System Prompt* altamente especializado convirtió al modelo Llama-3.3 en un traductor estricto, capaz de aislar la intención del usuario y convertirla en parámetros espaciales.
2. **Reducción de Ambigüedad vs. Rigidez:** Las instrucciones como "Output ONLY a valid JSON object" y "Translate actual object names into English" eliminaron por completo la ambigüedad, permitiendo que DALL-E recibiera *prompts* estandarizados. Sin embargo, esto volvió al sistema rígido: si el usuario dicta una orden confusa, el modelo está forzado a extraer datos en lugar de hacer preguntas aclaratorias.
3. **Alucinaciones en el Contexto Físico:** En robótica, una "alucinación" de la IA tiene consecuencias en el mundo real. Si el modelo deduce erróneamente una posición espacial, el UR3 ejecutará un movimiento no deseado. El equivalente a un enlace roto en este proyecto sería que el LLM generara coordenadas fuera del espacio de trabajo seguro del robot.

## 3. Propuesta de Guardrails y RAG

Para mitigar riesgos y mejorar la robustez, el sistema se beneficiaría de las siguientes implementaciones:

* **Filtros de Seguridad (Guardrails):** Implementar un validador de esquema JSON estricto antes de pasar a la fase de imagen. Además, incluir un *guardrail* de hardware en Python que impida enviar comandos al puerto 30002 si las coordenadas superan los 0.400 metros del área del pizarrón.
* **Integración con Sistemas RAG:** Conectar este copiloto robótico a una base de datos vectorial transformaría el proyecto. En lugar de generar imágenes desde cero (con los 14 segundos de latencia de OpenAI y el costo de $0.02 USD), el sistema podría buscar mediante *embeddings* en un catálogo propio de figuras pre-vectorizadas en SVG o consultar manuales técnicos del UR3 para resolver errores en tiempo de ejecución.

## 4. Áreas de Mejora y Reflexión Final

Si bien la arquitectura cumple los objetivos, el trabajo futuro debería enfocarse en:
* Reemplazar la API de imágenes en la nube por modelos de difusión locales (ej. Stable Diffusion) para reducir la latencia general del sistema a menos de 5 segundos.
* Integrar retroalimentación asíncrona en el frontend de Unity para indicar al usuario que el hardware está procesando su solicitud.

**Conclusión:**
Este proyecto demuestra cómo la robótica está evolucionando. Ya no dependemos exclusivamente de programar trayectorias manuales punto a punto; a través de interfaces de realidad extendida y agentes de IA orquestados, logramos traducir la intención humana directa y natural en cinemática industrial.