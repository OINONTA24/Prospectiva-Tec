---
title: Reporte Final
layout: default
has_children: true
nav_order: 7
---

## INTEGRANTES DEL EQUIPO

Diego Marquez

Haili Avila

José Antonio Reyes

# Proyecto Final: Integración de Gemelo Digital, IA y Robótica Física

Este proyecto integrador demuestra la construcción de un **Gemelo Digital** (*Digital Twin*), una tecnología que consiste en crear una réplica virtual exacta de un sistema físico. Esto permite simular, monitorear y controlar hardware del mundo real a través de un entorno digital inmersivo, logrando que la intención humana se traduzca en movimiento mecánico de forma natural.

A continuación, se ilustra la arquitectura de red y el flujo de datos entre los distintos modelos de inteligencia artificial y los componentes de hardware:

![Diagrama de Arquitectura de IA y UR3](assets/img/Drawing Robot.png)

## Presentacion de proyecto

https://canva.link/jua2qk0v30hi4yb

## Hardware Utilizado

El sistema opera mediante la comunicación de dos componentes de hardware principales:

* **Meta Quest 3 (Front End):** Gafas de realidad mixta que sirven como la interfaz principal del usuario. Capturan las instrucciones de voz mediante su micrófono integrado y simulan el entorno virtual del robot utilizando el motor gráfico Unity.
* **Brazo Robótico UR3 (Sistema Físico):** Un brazo robótico industrial de la serie CB3 encargado de recibir la trayectoria calculada y ejecutar físicamente el dibujo sobre un pizarrón utilizando un marcador como efector final.

## Pipeline de Inteligencia Artificial (Back End)

Para lograr que el robot "entienda" al usuario, el audio capturado pasa por una secuencia de modelos de Inteligencia Artificial alojados en el servidor:

* **Whisper AI:** Modelo encargado del proceso **STT** (*Speech-To-Text* o conversión de voz a texto). Su función es transcribir el audio del usuario a lenguaje natural escrito de alta precisión.
* **Llama 3.3:** Modelo de Lenguaje Grande (LLM) que recibe la transcripción y la procesa para extraer la intención del usuario. Transforma esta petición en un formato de datos estructurado (JSON).
* **OpenAI (Generador de Imágenes):** Recibe las instrucciones estructuradas del LLM y genera una representación visual (silueta) del objeto que el usuario solicitó dibujar.
* **OpenCV:** Herramienta de visión computacional que procesa la imagen generada por OpenAI, segmentando los trazos y transformando los píxeles de la imagen en coordenadas m