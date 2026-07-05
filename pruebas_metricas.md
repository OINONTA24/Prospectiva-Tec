---
layout: default
title: Pruebas y métricas
parent: Reporte Final
nav_order: 7
---

# Pruebas de Rendimiento y Métricas del Sistema

La viabilidad de un proyecto de robótica impulsado por Inteligencia Artificial depende de su confiabilidad y de la gestión de recursos. A continuación, se detallan las pruebas realizadas y los costos computacionales involucrados.

## 1. Fases de Pruebas Realizadas

Para garantizar que el brazo robótico no actuara de forma errática, el proyecto se dividió en cuatro fases de pruebas rigurosas:

* **Pruebas de Software Local (Unitarias):** Se probó el servidor Python de forma aislada. Se introdujeron audios pregrabados para verificar que los modelos Whisper, Llama y DALL-E se comunicaran correctamente entre sí sin interrupciones de red.
* **Pruebas de Realidad Mixta (Simulación):** Se probó la captura de audio desde las gafas Meta Quest 3. Antes de conectar el robot real, las trayectorias matemáticas generadas por OpenCV se enviaron al Gemelo Digital en Unity para asegurar que el modelo tridimensional dibujara correctamente en el entorno virtual.
* **Pruebas de Hardware en Vacio (Dry-Run):** Se conectó el brazo UR3 físico pero sin un marcador instalado. El objetivo era verificar los límites espaciales y comprobar que las coordenadas no forzaran al robot a golpear la mesa o exceder sus límites de articulación.

### Puntos que no se completaron en el proyecto

* **Pruebas de Integración Final:** La ejecución del sistema completo, desde el dictado de voz hasta el dibujo con el plumón en el pizarrón real, validando la precisión del trazo.
    * **Razon: Falta de tiempo y falta de entablar comunicación con el robot fisico.

## 2. Análisis de Latencia por Modelo

El tiempo que tarda el sistema desde que el usuario termina de hablar hasta que el robot comienza a moverse se midió durante las pruebas de integración:

| Fase | Modelo de IA / Herramienta | Función Técnica | Latencia |
| :--- | :--- | :--- | :--- |
| 1 | Whisper (base) | Transcripción de voz a texto | 0.52 s |
| 1 | Llama-3.3-70b (Groq) | Razonamiento y estructuración | 0.48 s |
| 2 | OpenAI (DALL-E 2) | Generación de la imagen base | 14.64 s |
| 3 | OpenCV (Python) | Transformación a vectores matemáticos | 0.07 s |
| **Total** | **Pipeline Completo** | **Tiempo total de espera** | **16.28 s** |

## 3. Tokenización y Costos de Inferencia

El uso de Inteligencia Artificial en la nube no es gratuito; requiere poder de cómputo que se mide y se cobra mediante un sistema llamado "Tokenización".

### ¿Qué es un Token?
Un *token* es la unidad básica de información que lee y genera un modelo de lenguaje. No siempre equivale a una palabra completa; a menudo, una palabra larga se divide en dos o tres tokens (similar a las sílabas). Cada vez que le pedimos a la IA que piense, le enviamos un número de tokens y ella nos responde con otro tanto.

### Consumo del Proyecto
Para extraer la intención del usuario y estructurar la información, nuestro modelo Llama 3.3 consumió los siguientes recursos en una iteración promedio:

* **Tokens de entrada:** 92 tokens (Esto incluye la orden del usuario y las instrucciones secretas de sistema que le dimos al modelo para que se comporte como un traductor estricto).
* **Tokens de salida:** 781 tokens (Es la respuesta matemática y estructurada que el modelo nos devuelve).
* **Total de procesamiento:** 873 tokens por ciclo.

### Costo de Inferencia Gráfica
A diferencia del texto, las imágenes consumen muchos más recursos. La generación del boceto vectorial mediante la API de OpenAI tiene un costo computacional fijo. Generar una imagen en resolución 1024x1024 píxeles representa un costo de **$0.02 USD** por cada instrucción que da el usuario. Este costo es necesario para garantizar que la traducción espacial hacia el robot sea altamente precisa.