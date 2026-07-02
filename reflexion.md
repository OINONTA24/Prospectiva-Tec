---
layout: default
title: Reflexión
parent: Práctica 1
nav_order: 6
---

# Reflexión

Las siguientes preguntas se responden con base en la experiencia del equipo durante la instalación, ejecución y comparación de los seis modelos.

---

## ¿Qué modelo fue más fácil de instalar y ejecutar?

Los seis modelos se instalaron con el mismo comando `ollama pull`, sin diferencias en el proceso. La variable más notable fue el tiempo de descarga, que depende directamente del tamaño. `tinyllama:1.1b-chat-v1-q8_0` fue el más rápido con 1.2 GB, seguido de `llama3.2:3b` con 2.0 GB. Los modelos de 7B (`qwen2.5:7b` con 4.7 GB y `mistral:7b` con 4.1 GB) tomaron considerablemente más tiempo.

---

## ¿Qué modelo respondió mejor en español?

`gemma3:4b` y `qwen2.5:7b` produjeron el español más natural y contextualizado. `mistral:7b` también respondió correctamente, aunque con siglas en inglés. `llama3.2:3b` y `phi3.5:latest` respondieron bien con tono más técnico. `tinyllama:1.1b-chat-v1-q8_0` fue el de peor desempeño: respondió en español pero con contenido incorrecto y fuera de tema en varios prompts.

---

## ¿Qué diferencia observaste entre un modelo pequeño y uno más grande?

La diferencia más clara se observó en precisión y coherencia temática. Los modelos de 7B mantuvieron consistencia en todos los prompts: respondieron lo que se les preguntó con ejemplos relevantes. Los modelos de 3–4B tuvieron un desempeño aceptable con algunas variaciones. `tinyllama:1.1b`, el más pequeño, falló en el prompt 3 respondiendo algo completamente diferente a lo pedido, y en el prompt 2 fabricó un enlace inexistente (alucinación).

Más parámetros no garantizan perfección, pero sí mayor estabilidad ante instrucciones complejas.

---

## ¿Qué importancia tiene la licencia del modelo?

La licencia define qué puede hacerse con el modelo fuera del uso personal. En esta práctica usamos seis modelos con tres tipos de licencia:

- **Gemma License / Llama 3.2 Community License** (propietarias): permiten uso académico y personal, pero restringen redistribución y uso comercial sin autorización expresa.
- **Apache 2.0** (qwen2.5, mistral, tinyllama): permisiva, permite uso libre incluyendo modificación y redistribución en proyectos comerciales, con atribución.
- **MIT** (phi3.5): la más permisiva, sin restricciones relevantes para uso académico o comercial.

En un contexto académico la diferencia suele ser irrelevante. En un proyecto profesional o startup, usar un modelo con licencia restrictiva sin leer las condiciones puede tener consecuencias legales.

---

## ¿Por qué no debe usarse un LLM como única fuente académica?

Los LLM generan respuestas estadísticamente plausibles, no verificadas. Durante esta práctica observamos ejemplos concretos: `tinyllama` respondió el prompt 3 con información completamente fuera de tema y fabricó un enlace de imagen inexistente en el prompt 2. Incluso modelos más capaces pueden cometer errores en conceptos específicos o datos factuales.

Ninguno de los seis modelos citó fuentes. Toda la información que generaron requiere verificación independiente. Usar un LLM como fuente primaria equivale a citar una fuente que no puede consultarse ni rastrearse.

---

## ¿Qué ventajas y limitaciones tiene ejecutar modelos localmente?

**Ventajas:**

- Los datos no salen del equipo (privacidad total).
- Sin costo por uso de API ni dependencia de conexión a internet.
- Control total sobre la versión, cuantización y configuración del modelo.
- Útil para prototipado rápido sin restricciones de cuota.

**Limitaciones:**

- Consume RAM y almacenamiento considerables. Los modelos de 7B requieren al menos 8–16 GB de RAM para correr con fluidez.
- En equipos sin GPU dedicada, la velocidad de respuesta puede ser significativamente menor que en plataformas en la nube.
- La calidad de los modelos locales pequeños es inferior a la de los modelos de la nube de mayor escala.
- La instalación y configuración inicial, aunque simple con Ollama, requiere conocimiento técnico básico.
