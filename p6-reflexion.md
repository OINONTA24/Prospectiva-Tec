---
layout: default
title: Reflexión comparativa
parent: Práctica 6
nav_order: 4
---

# Reflexión comparativa

Datos registrados sobre 100 pruebas cíclicas contra `llama-3.3-70b-versatile` (Groq Cloud API), `temperature = 0.1`, `response_format = json_object`:

| Métrica | Valor |
| --- | --- |
| Accuracy | **1.0000** |
| Macro F1-score | **1.0000** |
| JSON validity rate | **1.0000** |
| Latencia media | 2236.90 ms |
| Latencia P95 / P99 | 3640.23 ms / 3764.02 ms |

---

## 1. ¿Qué clase tuvo mayor número de errores?

Ninguna. Según `classification_report.csv` y la matriz de confusión, el modelo obtuvo accuracy y F1-score de 1.0000 (100 %) tanto para `draw` como para `none`. Las 50 muestras de intenciones de dibujo y las 50 de ruido/consultas se clasificaron sin un solo error, por lo que el conteo de errores en ambas clases fue cero.

---

## 2. ¿El modelo confundió instrucciones ambiguas con comandos reales?

No. Prompts de control diseñados para forzar el error — como *"mañana tal vez usemos el lienzo para pintar algo creativo"* o *"no hagas nada borra todo lo que estabas pensando"* — fueron absorbidos correctamente por la clase `none`. La temperatura baja (0.1) minimizó la aleatoriedad del modelo, obligándolo a ceñirse a las 8 reglas del prompt de sistema en vez de improvisar.

---

## 3. ¿Qué fue más crítico: calidad de clasificación o validez del JSON?

En un sistema ciberfísico como el UR3, ambos factores son críticos, pero en capas distintas:

- **La validez del JSON** es crítica para la estabilidad del software: si el JSON es inválido, el backend colapsaría por un `JSONDecodeError`, deteniendo el hilo de ejecución.
- **La calidad de clasificación** es crítica para la seguridad del hardware: si el JSON es válido pero la clasificación es errónea (un falso positivo de `draw`), el sistema enviaría un comando ejecutable incorrecto al robot, con riesgo de colisiones físicas o daño al lienzo y al actuador.

En esta corrida ambos factores fueron perfectos (1.0000), por lo que no hubo forma de determinar empíricamente cuál habría fallado primero bajo estrés — algo a explorar con un dataset más adversarial.

---

## 4. ¿La latencia fue estable durante las 100 pruebas?

Parcialmente. La media (2236.90 ms) es consistente con lo esperado para un modelo de 70B parámetros con un prompt few-shot denso, pero el rango real (328 ms – 4097 ms) muestra variación real trial a trial, típica de una API remota en la nube donde la latencia de red se suma a la de inferencia. No se observaron fallas ni *timeouts*, pero "estable" en el sentido estricto de baja varianza no describe estos datos — ver la pregunta 5.

---

## 5. ¿Qué ocurrió con P95 y P99?

El P95 fue de 3640.23 ms y el P99 de 3764.02 ms, ambos notablemente por encima de la media (2236.90 ms) y cerca del máximo observado (4096.89 ms). A diferencia de un pipeline con cola de latencia plana, aquí el 5 % de las peticiones más lentas tardó entre 1.6× y 1.8× el promedio. Esto es relevante para ingeniería: si el UR3 dependiera de esta latencia para control síncrono, el peor caso (percentil 99) casi duplica el tiempo esperado, lo cual debe considerarse al dimensionar *timeouts* o colas de comandos en el backend.

---

## 6. ¿El backend publicó mensajes MQTT solo cuando correspondía?

No aplica directamente: en esta versión aislada de evaluación no se implementó un backend FastAPI ni un broker MQTT — el pipeline se limitó a la lógica de extracción y guardado en archivos planos (`resultados_llm_led_raw.csv`). Conceptualmente, la arquitectura del Proyecto Final restringiría la publicación al bróker únicamente cuando `llm_action = draw`, bloqueando cualquier payload hacia el robot si la salida cae en `none`. Validar esto empíricamente requeriría levantar el backend y el broker, que queda como extensión de esta práctica.

---

## 7. ¿Qué cambios harías al prompt de sistema?

Aunque el rendimiento actual es del 100 %, el prompt consume 630.3 tokens de entrada en promedio por petición — la mayoría del costo de cada llamada. Una optimización razonable sería consolidar las 8 reglas y reducir los ejemplos few-shot (de 3 a 2, o comprimir su formato) para bajar el consumo a menos de 400 tokens de entrada, lo que impactaría directamente la latencia media sin sacrificar la calidad de extracción observada.

---

## 8. ¿Qué modelo tuvo mejor relación entre calidad y latencia?

El modelo evaluado, Llama 3.3 70B vía Groq, mostró calidad perfecta (100 % de efectividad semántica y estructural) con una latencia media de ~2.24 s. Comparado con modelos locales más pequeños en Ollama (Llama 3.2 3B o Qwen 2.5 7B, que suelen dar latencias por debajo de 1 s pero con mayor riesgo de errores de clasificación o de validez JSON), Llama 3.3 en Groq ofrece la mejor relación cuando la precisión del trazo y la seguridad del brazo UR3 son prioritarias sobre la respuesta instantánea.

---

## 9. ¿Qué riesgos existirían si se conectara un actuador real?

Si el UR3 se conectara directamente a las salidas del LLM sin capas de protección:

- **Activación por falsos positivos:** una conversación casual o ruido de fondo mal interpretado podría generar un arreglo de objetos y mover el robot sin instrucción real del usuario.
- **Saturación de comandos:** la variabilidad de latencia (hasta ~4.1 s en el peor caso) podría acumular peticiones en la cola del broker MQTT, provocando que el robot ejecute movimientos desfasados en el tiempo (comandos obsoletos).
- **Ausencia de límites de espacio:** posiciones semánticas como `"left"` o `"top"` podrían llevar al robot a intentar alcanzar coordenadas fuera de su espacio de trabajo físico, provocando singularidad cinemática o sobrecorriente en los servomotores.

## Conclusión del experimento

El análisis de rendimiento señala dos puntos a vigilar antes de escalar esta arquitectura a producción:

1. **Latencia y su variabilidad.** La media de 2236.90 ms —y sobre todo el P99 de 3764.02 ms, cerca del máximo observado (4096.89 ms)— hacen que este pipeline sea adecuado para despacho de tareas por lotes, pero no para control síncrono en tiempo real estricto.
2. **Tamaño real del banco de pruebas.** El 100 % de accuracy se midió sobre 20 enunciados únicos repetidos 5 veces cada uno, no sobre 100 formulaciones distintas. El resultado confirma consistencia del modelo, pero una siguiente iteración debería usar paráfrasis reales para medir generalización.

Para producción se sugiere: (a) evaluar la destilación hacia un modelo local más compacto (Llama 3.2 3B) que reduzca la dependencia de latencia de red, (b) comprimir el prompt few-shot para bajar el consumo de tokens de entrada (630.3 en promedio), y (c) levantar el backend y el broker MQTT reales para medir `mqtt_publish_rate` y `architecture_success_rate` de punta a punta, no solo la capa semántica aislada evaluada aquí.
