---
layout: default
title: Reflexión comparativa
parent: Práctica 5
nav_order: 4
---

# Reflexión comparativa

Datos registrados con el prompt de odometría diferencial (temperature = 0.7, top_p = 0.9, max_tokens = 300, perfil: Asistente genérico):

| Métrica | Ollama · qwen2.5:7b | Gemini · gemini-2.5-flash | Groq · llama-3.3-70b-versatile |
|---|---|---|---|
| Tiempo total | 39.178 s | 3.809 s | **1.943 s** |
| Tokens/s | 17.8 | 174.0 | **145.1** |
| Tokens salida | 470 | **663** | 282 |

---

## 1. ¿Qué modelo respondió más rápido?

**Groq** con `llama-3.3-70b-versatile` respondió en 1.943 s, seguido de Gemini con 3.809 s, y Ollama local con 39.178 s — veinte veces más lento que el peor de los remotos.

El resultado es contraintuitivo: el modelo de 70B parámetros en Groq fue más rápido que el de 7B corriendo localmente en un MacBook. Esto se explica por el hardware LPU (*Language Processing Unit*) de Groq, diseñado específicamente para inferencia de LLMs, frente a la CPU local que no dispone de GPU dedicada.

Importante: el tokens/s de Gemini (174.0) y Groq (145.1) incluyen la latencia de red en el denominador (se calcula con `wall_time`). El de Ollama (17.8) refleja el throughput puro de generación medido con `eval_duration` = 26.464 s. No son valores comparables directamente.

---

## 2. ¿Qué modelo generó la mejor explicación técnica?

**Gemini** con `gemini-2.5-flash` produjo la respuesta más completa y técnicamente correcta:

- Incluyó la corrección del ángulo medio en las ecuaciones de posición: Δx = v·cos(θ + Δθ/2)·Δt, que es la formulación kinematicamente más precisa para intervalos de tiempo finitos.
- El ejemplo numérico (R = 0.05 m, L = 0.2 m, velocidades 10 y 12 rad/s) es consistente y verificable paso a paso.
- Identificó tres fuentes de error distintas: deslizamiento de ruedas, imprecisión en parámetros R y L, y cuantificación de encoders.

Groq generó una respuesta clara y bien estructurada, pero omitió las ecuaciones de actualización de pose (Δx, Δy) y su ejemplo numérico presenta inconsistencias al verificar los cálculos.

Ollama generó la respuesta más extensa en tokens (470), pero con un error técnico significativo en la ecuación Δθ = |D_R − D_L|/r (usa el radio de rueda en el denominador en lugar del ancho del eje L), y un ejemplo con Δθ = 5π rad (≈ 900°) físicamente irreal.

---

## 3. ¿El modelo más grande fue siempre mejor?

No. El ranking en calidad técnica fue **Gemini > Groq > Ollama**, mientras que en parámetros el ranking es **Groq (70B) > Ollama (7B) > Gemini (no divulgado)**. Groq, con el modelo más grande en parámetros conocidos, no produjo la mejor respuesta.

Esto evidencia que el tamaño en parámetros no determina sólo la calidad. El proceso de fine-tuning por instrucciones, el RLHF y la arquitectura del modelo también son factores clave. Gemini-2.5-flash está altamente optimizado para seguimiento de instrucciones y respuestas estructuradas, lo que explica su desempeño superior a pesar de que Google no divulga su arquitectura.

Asimismo, `qwen2.5:7b` a pesar de tener menos parámetros que `llama-3.3-70b-versatile`, generó una respuesta más larga y con más contenido, aunque con errores técnicos.

---

## 4. ¿Qué diferencia hubo entre ejecutar localmente y usar una API?

La diferencia más visible fue el tiempo de respuesta: Ollama tardó **39 segundos** frente a menos de 4 segundos de los proveedores remotos. En términos de experiencia de usuario, una espera de 39 s es inaceptable para una aplicación de chatbot.

| Aspecto | Ollama local | API remota |
|---|---|---|
| Tiempo de respuesta | 39.178 s (lento por hardware) | 1.9 – 3.8 s (infraestructura dedicada) |
| Privacidad | Total — prompt no sale del equipo | Prompt viaja a servidores externos |
| Costo monetario | Sin costo por token | Puede tener costo en planes de pago |
| Control del modelo | Completo (versión, parámetros) | Limitado a lo que expone el proveedor |
| Disponibilidad offline | Sí | No — requiere internet |
| Configuración inicial | Instalar Ollama + descargar modelo | Crear cuenta + API key (minutos) |

La privacidad es la diferencia más relevante para datos sensibles: con Ollama el prompt nunca sale del equipo, mientras que con Gemini y Groq el contenido completo (mensaje, historial, system prompt) pasa por servidores de terceros.

---

## 5. ¿Qué riesgos aparecen al enviar datos a un proveedor externo?

- **Confidencialidad:** el prompt, el system prompt y el historial completo se transmiten a servidores del proveedor. Datos sensibles (médicos, estudiantiles, empresariales) quedan expuestos a terceros.
- **Uso de datos para entrenamiento:** dependiendo de los términos de servicio, el proveedor puede usar los prompts para mejorar sus modelos. Es obligatorio leer la política de datos antes de enviar información de usuarios.
- **Regulaciones:** en contextos sujetos a GDPR (Europa) o normativas equivalentes, enviar datos personales a APIs externas puede implicar obligaciones contractuales o ser ilegal sin acuerdos específicos.
- **Dependencia de disponibilidad:** si el servicio experimenta una interrupción, la aplicación falla completamente. Ollama local no tiene este riesgo.
- **Interceptación en red:** aunque las APIs usan HTTPS, en configuraciones de red inseguras o corporativas con inspección TLS existe riesgo de intercepción.

Para esta práctica estos riesgos se mitigan usando exclusivamente prompts técnicos genéricos sin datos personales ni institucionales.

---

## 6. ¿Qué pasaría si la API cambia de precio o deja de estar disponible?

Si la aplicación dependiera exclusivamente de una API remota, un cambio de precios o una discontinuación del servicio detendría su funcionamiento. Esto se denomina **lock-in de proveedor**.

La arquitectura implementada en esta práctica mitiga ese riesgo de forma intencional: el campo `provider` abstrae el proveedor detrás de una interfaz unificada. Cambiar de Gemini a Groq, o a cualquier API compatible con OpenAI, requiere únicamente actualizar el selector en el frontend, sin reescribir la lógica del backend. Ollama local actúa como fallback gratuito.

En producción, la estrategia recomendada es mantener al menos dos proveedores activos y un modelo local como respaldo, con un umbral de costo que active el fallback automáticamente.

---

## 7. ¿En qué casos conviene usar Ollama local?

- Cuando los datos contienen información sensible, personal o confidencial.
- Cuando se requiere operar sin conexión a internet.
- Cuando el presupuesto no permite el costo por token de APIs externas.
- Para prototipado y experimentación sin riesgo de costo inesperado.
- Cuando se necesita control total sobre la versión exacta del modelo y sus parámetros.
- En entornos educativos o corporativos donde los datos no deben salir de la institución.

La limitación principal para esta práctica fue el hardware: sin GPU dedicada, `qwen2.5:7b` tardó 39 s por respuesta, lo que hace inviable el uso interactivo. Con una GPU discreta, el mismo modelo correría en 3–5 s.

---

## 8. ¿En qué casos conviene usar una API externa?

- Cuando se necesita capacidad de razonamiento superior a la que ofrece el hardware local disponible.
- Cuando la velocidad de respuesta es crítica para la experiencia del usuario (< 5 s).
- Cuando el proyecto requiere capacidades especiales: visión por computadora, audio, búsqueda web.
- Para producción con múltiples usuarios concurrentes, donde el escalado automático del proveedor es necesario.
- Cuando el equipo no puede gestionar infraestructura de inferencia (actualizaciones, disponibilidad, monitoreo).
- Para evaluar modelos de frontera sin invertir en hardware dedicado.

---

## 9. ¿Qué proveedor fue más fácil de integrar?

**Groq** resultó el más directo: su API es completamente compatible con el estándar OpenAI. El mismo código que integra GPT-4 funciona con Groq cambiando únicamente el endpoint (`api.groq.com`) y el header de autenticación. Campos como `messages`, `temperature`, `top_p`, `max_tokens` y la estructura de `usage` son idénticos.

**Gemini** requirió tres adaptaciones específicas: el rol del asistente es `"model"` en lugar de `"assistant"`, el system prompt va en un campo separado `system_instruction`, y los parámetros usan `camelCase` (`topP`, `maxOutputTokens`). Además fue necesario desactivar el modo de razonamiento interno (`thinkingBudget: 0`) porque sin esta configuración los tokens de "pensamiento" internos consumían el presupuesto y la respuesta visible quedaba truncada con solo 39 tokens visibles de 1 269 totales.

**Ollama** es el más simple en configuración inicial (sin cuenta, sin API key), pero su formato no sigue el estándar OpenAI, por lo que no es intercambiable directamente con los otros dos sin adaptación de código.

---

## 10. ¿Qué información técnica no fue publicada por el proveedor?

- **Google (Gemini):** no divulga el número de parámetros, la arquitectura ni los datos de entrenamiento. El comportamiento del "pensamiento interno" (thinking tokens) tampoco está completamente documentado. Esta práctica encontró empíricamente que sin `thinkingBudget: 0` el modelo consumía ~957 tokens de razonamiento interno y dejaba solo 39 tokens para la respuesta visible, a pesar de tener `maxOutputTokens: 300`.

- **Groq:** el hardware LPU es propiedad intelectual de la empresa. Los modelos que sirve son abiertos (Llama, Mixtral), pero la infraestructura de inferencia no lo es. Los tokens/s del servidor (separados de la latencia de red) no se exponen en la respuesta de la API.

- **En todos los casos:** la latencia de servidor aislada de la latencia de red no es accesible desde la API. Los valores de tokens/s calculados para Gemini (174.0) y Groq (145.1) en esta práctica incluyen la latencia de red en el tiempo base, por lo que son aproximaciones del throughput percibido por el usuario, no mediciones precisas de la velocidad de inferencia del modelo.
