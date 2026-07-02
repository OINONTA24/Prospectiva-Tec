---
layout: default
title: Reflexión técnica
parent: Práctica 3
nav_order: 4
---

# Reflexión técnica

---

## 1. ¿Qué modelo local utilizaste?

Se utilizó **`gemma3:4b`** de Google DeepMind (familia Gemma 3, 4 mil millones de parámetros, licencia Gemma). Es un modelo equilibrado para hardware de consumo: ocupa 3.3 GB en disco, corre en CPU sin necesidad de GPU dedicada y genera respuestas coherentes en español con latencias de entre 3 y 15 segundos dependiendo del contexto y de si el modelo ya está cargado en memoria.

---

## 2. ¿Qué parámetros configuraste desde el frontend?

La interfaz expone cinco parámetros ajustables en tiempo real:

| Parámetro | Valor por defecto | Rango |
|---|---|---|
| `temperature` | 0.7 | 0.0 – 1.2 |
| `top_p` | 0.9 | 0.1 – 1.0 |
| `num_predict` | 160 | 20 – 1000 |
| `num_ctx` | 4096 | 2048 / 4096 / 8192 |
| `repeat_penalty` | 1.1 | 1.0 – 2.0 |

Además se puede modificar el `system_prompt` para cambiar el comportamiento del modelo sin reiniciar el servidor.

---

## 3. ¿Qué ocurre al aumentar `num_predict`?

Al aumentar `num_predict` el modelo puede generar respuestas más largas y completas. Se observa un incremento proporcional en `eval_count`, `eval_duration_s` y `wall_time_s`, ya que el modelo necesita más ciclos de inferencia. Sin embargo, más tokens no siempre implica mejor calidad: el modelo puede comenzar a repetirse o divagar si el prompt no está bien acotado. En nuestras pruebas, pasar de 160 a 400 tokens casi triplicó el tiempo de respuesta.

---

## 4. ¿Qué ocurre al modificar `temperature`?

La temperatura controla la distribución de probabilidad sobre los tokens candidatos en cada paso de generación:

- **Temperature baja (0.0 – 0.3):** respuestas más deterministas, concisas y repetibles. Útil para tareas de extracción o resumen.
- **Temperature media (0.5 – 0.8):** balance entre coherencia y variedad. Apropiado para respuestas académicas o conversacionales.
- **Temperature alta (1.0 – 1.2):** respuestas más creativas y diversas, pero con mayor riesgo de incoherencias o alucinaciones.

En términos de métricas, la temperatura no afecta `eval_duration_s` ni `tokens_per_second` significativamente, ya que el costo computacional por token es constante.

---

## 5. ¿Por qué es útil mostrar tokens y latencia?

Las métricas de inferencia son útiles por varias razones:

1. **Diagnóstico de rendimiento:** `load_duration_s` alto indica que el modelo no estaba en memoria, mientras que `eval_duration_s` alto indica que la generación fue lenta (probablemente por contención de CPU).
2. **Costo operativo:** en producción, los tokens consumidos se traducen directamente en costo de API o en uso de GPU. Conocer `total_tokens` permite estimar presupuesto.
3. **Optimización de prompts:** si `prompt_eval_count` es muy alto en relación con `eval_count`, el prompt es demasiado largo. Reducirlo mejora la latencia.
4. **Comparación de modelos:** `tokens_per_second` permite comparar la velocidad de distintos modelos de manera objetiva.

---

## 6. ¿Por qué se recomienda usar un backend en vez de conectar el navegador directamente a Ollama?

Conectar el navegador directamente a Ollama (`http://localhost:11434`) presentaría varios problemas:

- **CORS:** por defecto Ollama no permite peticiones desde orígenes arbitrarios. El backend actúa como proxy que sí puede configurar los headers CORS.
- **Validación:** el backend valida y sanitiza los parámetros antes de enviárselos a Ollama, evitando valores fuera de rango que podrían causar errores o comportamientos inesperados.
- **Seguridad:** exponer el puerto de Ollama al navegador en un entorno de producción permitiría a cualquier página web de terceros llamarlo. El backend puede agregar autenticación sin modificar Ollama.
- **Métricas y logging:** el backend es el lugar natural para agregar instrumentación (`wall_time`, logs, monitoreo) sin depender de lo que Ollama exponga en su API.
- **Desacoplamiento:** si en el futuro se migra de Ollama a otro motor (OpenAI, LiteLLM, vLLM), solo se modifica el backend; el frontend no cambia.

---

## 7. ¿Cómo extenderías este chatbot para tu proyecto?

Para el proyecto integrador de Prospectiva de la Tecnología, el chatbot podría extenderse en varias dimensiones:

1. **Historial multi-turno persistente:** almacenar el contexto de conversación en el payload (`messages[]`) para que el modelo recuerde mensajes anteriores de la misma sesión.
2. **Base de conocimiento local (RAG):** conectar un vector store (ChromaDB, FAISS) con documentos del dominio del proyecto para que el modelo pueda citar fuentes específicas en sus respuestas.
3. **Selección dinámica de modelo:** comparar automáticamente respuestas de varios modelos instalados y mostrar las métricas en paralelo para elegir el mejor para cada tipo de consulta.
4. **Sistema multi-agente:** dividir tareas complejas entre agentes especializados (uno para investigación, otro para síntesis, otro para evaluación crítica).
5. **Interfaz de evaluación:** agregar un botón de feedback (👍/👎) que registre las respuestas en un archivo CSV para análisis posterior y fine-tuning.
