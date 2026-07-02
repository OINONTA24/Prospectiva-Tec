---
layout: default
title: Reflexión técnica
parent: Práctica 4
nav_order: 2
---

# Reflexión técnica

---

## 1. ¿Qué perfil fue más útil y por qué?

El **Copiloto docente** fue el más útil en términos de calidad de respuesta y versatilidad. Su instrucción de adaptar el nivel de explicación al interlocutor produjo respuestas que eran al mismo tiempo rigurosas y accesibles: la respuesta sobre las estaciones del año, por ejemplo, integró inclinación axial, ángulo solar y hemisferios con un lenguaje claro y sin simplificar en exceso. La instrucción de honestidad epistémica también fue efectiva: al preguntar por los sueños, el modelo enumeró múltiples teorías sin presentar ninguna como definitiva, lo cual es correcto desde el punto de vista científico.

El **Copiloto de robótica** fue igualmente preciso dentro de su dominio. El diagnóstico del motor paso a paso fue estructurado y técnicamente sólido, y el follow-up con hardware específico (A4988 + NEMA 17) produjo recomendaciones concretas que un ingeniero podría aplicar directamente.

---

## 2. ¿Qué diferencias observaste entre el prompt genérico y el system_prompt especializado?

La diferencia más notable no fue la corrección del contenido —ambos perfiles respondieron con información válida— sino el **encuadre y la adaptación**:

- El asistente genérico responde *qué* es algo o *cómo* se hace de forma estándar.
- El copiloto especializado responde *qué* y *cómo* desde la perspectiva del dominio y del usuario.

En el ejemplo del aprendizaje del japonés, el genérico dio una lista universal de recursos (Duolingo, Memrise, etc.). Un copiloto docente habría explorado primero el nivel previo del usuario y adaptado la estrategia. En el ejemplo del motor paso a paso, el genérico habría dado pasos genéricos de troubleshooting; el copiloto de robótica pidió las especificaciones de hardware antes de asumir la causa.

---

## 3. ¿Qué instrucciones redujeron ambigüedad?

Las instrucciones que más redujeron ambigüedad fueron:

- **Política de longitud de respuesta** (*"Simple questions: 1–3 sentences"*): en el perfil Docente produjo respuestas concisas para preguntas directas y evitó el relleno innecesario.
- **Prohibición de inventar** (*"Do not invent sources, citations, studies, statistics, or references"*): en el perfil de Investigación, el modelo fue explícito sobre la ausencia de datos verificables en lugar de fabricar referencias.
- **Instrucción de pedir aclaración** (*"Ask clarifying questions when information is missing"*): en el perfil de Robótica, el modelo solicitó el hardware específico antes de dar un diagnóstico definitivo, lo cual redujo la probabilidad de respuestas incorrectas.

---

## 4. ¿Qué instrucciones hicieron la respuesta demasiado rígida?

El perfil de **Investigación** tiene estructuras de respuesta muy detalladas: evaluación de claims en 4 pasos y plan de investigación en 5 pasos. Esto llevó al modelo a aplicar esa estructura incluso en preguntas moderadas, generando respuestas de 600+ tokens cuando una respuesta de 150–200 habría sido suficiente. Las instrucciones estructurales son útiles para tareas complejas, pero se aplican sin discriminar la complejidad de la pregunta.

El perfil de Robótica también tendió a usar listas numeradas para todas las respuestas, incluyendo explicaciones conceptuales donde un párrafo fluido habría sido más legible.

---

## 5. ¿El modelo inventó información? ¿En qué caso?

No se observaron alucinaciones evidentes de contenido factual, pero sí un caso de **alucinación de recurso**:

En la respuesta al follow-up del motor paso a paso (A4988 + NEMA 17), el copiloto de robótica incluyó un enlace de GitHub a un supuesto datasheet del A4988. Ese URL no fue verificado durante las pruebas y podría no existir o apuntar a un recurso incorrecto. Esta es una forma frecuente de alucinación: el modelo *sabe* que existe un datasheet y *sabe* que podría estar en GitHub, pero inventa el path específico.

En el perfil de Investigación, el modelo respondió en inglés en al menos una ocasión a pesar de la política de idioma. Esto no es una alucinación de contenido, pero sí un fallo en la adherencia a las instrucciones del sistema.

---

## 6. ¿Qué guardrails agregarías?

| Guardrail | Problema que resuelve |
|---|---|
| Verificación de idioma post-generación | El modelo ignoró la política de idioma en el perfil de Investigación; un filtro de detección de idioma (ej. `langdetect`) podría reintentar la generación o advertir al usuario |
| Prohibición explícita de URLs | Evitaría la inclusión de enlaces no verificables; el copiloto puede indicar que el usuario busque el datasheet en la fuente oficial sin proporcionar un URL específico |
| `num_predict` dinámico por perfil | El perfil de Investigación necesita más tokens que el Docente; la selección de perfil debería configurar automáticamente el límite de tokens recomendado |
| Longitud máxima de historial | Sin un límite, el historial puede crecer hasta superar `num_ctx`; el backend debería truncar los turnos más antiguos cuando el total de tokens supere un umbral |
| Advertencia de incertidumbre | Para dominios de riesgo (robótica eléctrica, medicina), el copiloto debería añadir siempre un disclaimer cuando proporcione instrucciones de hardware o salud |

---

## 7. ¿Cómo conectarías este copiloto con documentos propios en un sistema RAG?

RAG (*Retrieval-Augmented Generation*) permite que el copiloto consulte documentos específicos antes de responder, sin modificar los pesos del modelo. La integración sobre esta arquitectura sería la siguiente:

```
Usuario envía pregunta
        │
        ▼
Backend convierte la pregunta en un vector de embedding
(ej. nomic-embed-text vía Ollama)
        │
        ▼
Búsqueda en base de datos vectorial (ChromaDB, Qdrant)
→ se recuperan los N fragmentos más relevantes del corpus
        │
        ▼
Los fragmentos se inyectan en el system_prompt como contexto:
  "Contexto relevante:\n[fragmento 1]\n[fragmento 2]\n..."
        │
        ▼
El copiloto especializado responde con base en las instrucciones del perfil
+ el contexto recuperado + el historial de conversación
```

Para el perfil de Investigación esto es especialmente valioso: en lugar de pedirle al modelo que recuerde papers o estadísticas (donde alucinará), se le proporciona el texto real del artículo y se le pide que lo analice. Para el perfil de Robótica, el corpus podría incluir los datasheets de los componentes más comunes, eliminando el riesgo de alucinación de especificaciones técnicas.

---

## Notas adicionales

### Comportamiento del idioma con `gemma3:4b`
La política de idioma (*"Respond in the same language used by the user"*) funcionó correctamente en la mayoría de los casos: el modelo respondió en español a todas las preguntas del genérico, robótica y docente. El perfil de Investigación presentó una excepción donde respondió en inglés ante una pregunta de alta densidad semántica. Esto sugiere que la instrucción de idioma tiene menor prioridad para este modelo cuando el system prompt es extenso y la pregunta es compleja. La solución correcta es un guardrail en el backend, no confiar únicamente en la instrucción de sistema.

### Sobre el `num_predict` en el perfil de Investigación
El límite por defecto de 160 tokens resulta insuficiente para el perfil de Investigación, cuyos planes de respuesta estructurados generan naturalmente 500–700 tokens. En una implementación de producción, el endpoint `/profiles` podría incluir un campo `recommended_num_predict` que el frontend aplique automáticamente al cambiar de perfil. No se implementó en esta práctica, pero queda identificado como mejora prioritaria.

### Valor del historial de conversación
La función de follow-up demostró ser la diferencia más práctica entre un chatbot aislado y un copiloto real. En las pruebas del perfil de Investigación, cuando el modelo respondió en inglés, el usuario simplemente pidió la versión en español en el turno siguiente y el modelo la proporcionó correctamente. En el perfil de Robótica, el primer turno estableció el contexto del problema y el segundo turno especificó el hardware; sin historial, ese segundo turno hubiera requerido repetir todo el contexto. El copiloto se vuelve más útil a medida que avanza la conversación.
