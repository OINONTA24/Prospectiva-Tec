---
title: Reflexión y Retos Técnicos
layout: default
parent: Reporte Final
nav_order: 5
---

# Reflexión Técnica, Retos y Trabajo Futuro

El desarrollo del pipeline de Inteligencia Artificial y la integración robótica requirió sortear múltiples obstáculos de red, restricciones de hardware y comportamiento no determinista de los modelos.

## 1. Problemáticas Enfrentadas

* **Restricciones de Tiempo:** La calendarización del desarrollo limitó la posibilidad de implementar una arquitectura de microservicios más robusta.
* **Protocolos de Comunicación (UR3):** Se experimentaron problemas críticos en la conexión con el controlador del robot debido a la falta de protocolos de mensajería ligera, como MQTT. El uso de conexiones TCP directas generó cuellos de botella en la transmisión de las coordenadas.
* **Alucinaciones y Dataset Propio:** En la fase de generación gráfica, se intentó construir y entrenar un modelo propio mediante la creación de un dataset personalizado. El entrenamiento falló, produciendo imágenes con alucinaciones severas y trazos discontinuos que OpenCV no lograba segmentar de forma segura para el hardware.
* **Latencia vs. Nube:** Debido al fallo del modelo local, se optó por implementar la API de OpenAI. Aunque esto resolvió la fidelidad geométrica de los trazos, introdujo una latencia considerable (aproximadamente 14 segundos) al depender del procesamiento en servidores externos.

## 2. Áreas de Mejora y Escalabilidad

Para optimizar el código en futuras iteraciones, se proponen las siguientes directrices técnicas:

* **Migración a Ecosistema Local:** La solución definitiva a la latencia consiste en ejecutar todos los modelos (STT, LLM y Generación de Imagen) de forma estricta en hardware local (Edge AI), erradicando la dependencia de componentes cerrados como OpenAI.
* **Implementación de MQTT:** Refactorizar la capa de red del UR3 para utilizar un *broker* MQTT. Esto permitirá publicar y suscribir los waypoints de forma asíncrona, estabilizando la comunicación con el brazo robótico.
* **Optimización de Modelos Gráficos:** Retomar el entrenamiento de un modelo de generación local (ej. Stable Diffusion) aplicando técnicas de *Fine-Tuning* para asegurar salidas vectoriales optimizadas desde el primer ciclo de inferencia.