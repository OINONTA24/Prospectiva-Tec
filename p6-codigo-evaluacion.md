---
layout: default
title: Código de evaluación
parent: Práctica 6
nav_order: 1
---

# Código de evaluación

`eval_100.py` automatiza la inyección secuencial de 100 prompts simulando la salida del pipeline de voz-a-texto (Whisper) del Proyecto Final, y registra cómo el LLM clasifica e interpreta cada uno.

Código completo: [`evaluacion-p6/eval_100.py`](https://github.com/oinonta24/Prospectiva-Tec/blob/main/evaluacion-p6/eval_100.py)

---

## Propósito

Automatizar la inyección cíclica de 100 prompts balanceados (50 instrucciones de dibujo y 50 de ruido/control), capturando en cada ejecución la latencia, el consumo de tokens y la validez estructural del JSON generado por el modelo.

---

## Banco de pruebas

El dataset se construye a partir de 10 plantillas de `draw` y 10 de `none`, cada una repetida 5 veces, para llegar a 100 muestras balanceadas:

```python
dataset_pruebas = [
    {"text": "Quiero que me dibujes un pato en una moto en el centro", "expected_action": "draw"},
    {"text": "un perro corriendo a la izquierda y un gato durmiendo", "expected_action": "draw"},
    {"text": "pinta una manzana roja... no mejor dibuja un coche azul en el centro", "expected_action": "draw"},  # Autocorrección
    # ... 7 plantillas más
] * 5  # 50 muestras de la clase draw

dataset_pruebas += [
    {"text": "¿Qué es el protocolo de comunicación MQTT y cómo funciona?", "expected_action": "none"},
    {"text": "a ver... si... probando microfono uno dos tres", "expected_action": "none"},
    {"text": "mañana tal vez usemos el lienzo para pintar algo creativo", "expected_action": "none"},
    # ... 7 plantillas más
] * 5  # 50 muestras de la clase none
```

Las 10 plantillas de `draw` cubren estructuras simples, órdenes con acción (`corriendo`, `flotando`, `volando`), posiciones espaciales compuestas y una autocorrección explícita (*"pinta una manzana roja... no mejor dibuja un coche azul"*). Las 10 plantillas de `none` cubren ruido de calibración de micrófono, conversación ajena, preguntas teóricas/de costo, saludos casuales y comandos de detención.

> **Nota metodológica:** al repetir cada plantilla 5 veces sin generar paráfrasis reales, el banco de pruebas contiene únicamente **20 enunciados únicos**, no 100 formulaciones distintas. Esto explica en parte por qué el modelo alcanzó accuracy perfecta: el experimento mide muy bien la *consistencia* del modelo ante la misma entrada repetida, pero no mide tan bien su capacidad de *generalización* ante paráfrasis nuevas. Una mejora natural para una siguiente iteración es sustituir la repetición literal por variaciones léxicas reales (sinónimos, reordenamientos, ruido de transcripción distinto en cada repetición).

---

## Prompt de sistema (few-shot)

El prompt reutiliza el rol de "asistente NLP para un brazo UR3 que dibuja" con 8 reglas y 3 ejemplos few-shot:

```python
peticion_prompt = f"""
You are an expert NLP assistant for a UR3 robot arm that draws.
Your job is to analyze the user's spoken request and output a JSON object containing a list of objects to draw.
You must capture spatial layouts, actions, and physical relationships between objects.

Rules:
1. Identify the FINAL intent. If the user corrects themselves, IGNORE the first items and only extract the last ones mentioned.
2. Fix context errors from Speech-to-Text.
3. Quantifiers: If they say "two cars", add "car" twice to the list.
4. "position": Extract general spatial descriptions (...). If not specified, set to null.
5. "action": If the object is performing an action (...), extract it in English. If not, set to null.
6. "relative_to": If an object is ON, INSIDE, NEXT TO, or UNDER another object, specify that relationship (...).
7. If the prompt is gibberish or doesn't request a drawing, return an empty list.
8. Output ONLY a valid JSON object. No explanations, no markdown formatting.

Examples:
Input: "Quiero que me dibujes un pato en una moto en el centro"
Output: {{"objects": [{{"name": "duck", "position": "center", "action": "riding", "relative_to": "on a motorcycle"}}, ...]}}
# ... 2 ejemplos más

Input: "{{frase_humano}}"
Output:"""
```

La regla 1 (ignorar los primeros ítems si el usuario se autocorrige) y la regla 7 (lista vacía si no hay petición de dibujo) son las que separan directamente la clase `draw` de `none` en el paso de validación.

---

## Llamada al modelo y validación del JSON

```python
completion = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": peticion_prompt}],
    temperature=0.1,
    response_format={"type": "json_object"}
)

raw_response = completion.choices[0].message.content
prompt_tokens = completion.usage.prompt_tokens
completion_tokens = completion.usage.completion_tokens

try:
    datos_extraidos = json.loads(raw_response)
    objects_list = datos_extraidos.get("objects", [])
    schema_valid = True
    llm_action_mapped = "draw" if len(objects_list) > 0 else "none"
except json.JSONDecodeError:
    schema_valid = False
    llm_action_mapped = "invalid_json"
```

`response_format={"type": "json_object"}` fuerza el modo JSON de Groq: si el modelo produce texto fuera de esquema, `json.loads` lanza `JSONDecodeError` y el trial se marca como `invalid_json` en vez de detener la ejecución completa (`try/except` a nivel de trial).

---

## Variables capturadas

| Variable | Descripción |
| --- | --- |
| `latency_ms` | Tiempo de respuesta de la API de Groq, medido con `time.time()` |
| `prompt_tokens` / `completion_tokens` | Consumo de tokens de entrada/salida reportado por `completion.usage` |
| `schema_valid` | `True` si `raw_response` es JSON parseable |
| `llm_action` | `draw`, `none`, `invalid_json` o `api_error` |

---

## Artefactos generados

1. `resultados_llm_led_raw.csv` — base de datos cruda con las 100 filas (prompt, etiquetas esperada/predicha, latencia, tokens y el JSON crudo de cada respuesta).
2. `instrumento_supervision_llm_led.xlsx` — matriz para auditoría *human-in-the-loop*: agrega las columnas `accion_correcta_supervisor`, `evaluacion_supervisor`, `calidad_1_5` y `observaciones_supervisor`, inicialmente vacías, para que un supervisor humano revise cada trial de forma independiente al criterio automático.

```python
df_excel = df_raw[["trial", "prompt_text", "expected_action", "llm_action", "latency_ms"]].copy()
df_excel["accion_correcta_supervisor"] = ""
df_excel["evaluacion_supervisor"] = "no evaluado"
df_excel["calidad_1_5"] = ""
df_excel["observaciones_supervisor"] = ""
df_excel.to_excel(excel_path, index=False)
```

---

## Adaptación respecto al script de referencia

A diferencia del `eval_100.py` de la guía (que llama a un backend FastAPI local que a su vez llama a Ollama y publica en MQTT), esta versión llama **directamente** a la API de Groq desde el propio script de evaluación, sin backend intermedio ni broker MQTT. Es una evaluación de la capa semántica en aislamiento, consistente con la nota de alcance descrita en la [página principal de la práctica]({% link practica-06.md %}).

**Seguridad:** la clave de la API de Groq se lee con `os.environ["GROQ_API_KEY"]` en vez de escribirse en el código fuente, precisamente porque este script se publica en un repositorio público.
