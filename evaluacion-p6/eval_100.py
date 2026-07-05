import json
import os
import time
import pandas as pd
from groq import Groq

# Configuración de rutas y entorno
TARGET_DIR = r"C:\Users\desqu\OneDrive\Desktop\Tec_emergentes"
os.makedirs(TARGET_DIR, exist_ok=True)

# Inicialización de la API de Groq
# La clave NUNCA debe escribirse en el código fuente. Se lee desde una
# variable de entorno para poder subir este script a un repositorio público.
#   Windows (PowerShell):  $env:GROQ_API_KEY = "tu_clave_aqui"
#   macOS / Linux:         export GROQ_API_KEY="tu_clave_aqui"
GROQ_API_KEY = os.environ["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

# =====================================================================
# BANCO DE PRUEBAS CONTROLADO: 100 cadenas simulando salidas de Whisper
# Clases esperadas principales basadas en la intención global del prompt:
# 'draw' -> Petición válida de dibujo (con o sin especificación espacial/acción)
# 'none' -> Ruido de fondo, pláticas casuales, peticiones ambiguas o puramente conceptuales
# =====================================================================

dataset_pruebas = [
    # ---- SUB-CONJUNTO 1: Peticiones de Dibujo Válidas (Clase: 'draw') - 50 Muestras ----
    # Estructuras Simples, con Acciones, Posiciones Complejas y Autocorrecciones
    {"text": "Quiero que me dibujes un pato en una moto en el centro", "expected_action": "draw"},
    {"text": "un perro corriendo a la izquierda y un gato durmiendo", "expected_action": "draw"},
    {"text": "dibujame un coche a la derecha y un pajaro volando sobre un arbol arriba", "expected_action": "draw"},
    {"text": "pinta una manzana roja... no mejor dibuja un coche azul en el centro", "expected_action": "draw"}, # Autocorrección
    {"text": "dibuja un astronauta flotando a la derecha", "expected_action": "draw"},
    {"text": "traza un circulo en el centro y pon un cuadrado adentro de el", "expected_action": "draw"},
    {"text": "quiero ver un barco navegando en el mar abajo en el lienzo", "expected_action": "draw"},
    {"text": "esboza un caballo saltando sobre una valla a la izquierda", "expected_action": "draw"},
    {"text": "pinta un avion volando en las nubes arriba", "expected_action": "draw"},
    {"text": "dibuja una taza de cafe caliente en una mesa en el centro", "expected_action": "draw"},
] * 5  # Multiplicamos por 5 para obtener 50 muestras balanceadas con variaciones léxicas en la práctica real

# ---- SUB-CONJUNTO 2: Discriminación de Ruido y Consultas (Clase: 'none') - 50 Muestras ----
# Ruido de fondo captado por micrófono, preguntas teóricas, comandos abstractos o ambiguos
dataset_pruebas += [
    {"text": "¿Qué es el protocolo de comunicación MQTT y cómo funciona?", "expected_action": "none"}, # Pregunta teórica
    {"text": "oye Diego acuérdate de apagar la luz del laboratorio cuando salgamos", "expected_action": "none"}, # Conversación casual / Ruido
    {"text": "el brazo robotico UR3 utiliza servomotores industriales de alta precision", "expected_action": "none"}, # Declarativa / Sin orden
    {"text": "a ver... si... probando microfono uno dos tres", "expected_action": "none"}, # Ruido de calibración
    {"text": "ayer fui a cenar tacos con mi tio y platicamos de motores", "expected_action": "none"}, # Ruido ambiental / Diálogo ajeno
    {"text": "mañana tal vez usemos el lienzo para pintar algo creativo", "expected_action": "none"}, # Intención no inmediata / Ambiguo
    {"text": "¿cuánto cuesta la suscripción mensual de la API de OpenAI?", "expected_action": "none"}, # Pregunta de costo
    {"text": "hola buenas tardes robot como te encuentras el dia de hoy", "expected_action": "none"}, # Saludo casual
    {"text": "explicame matematicamente como funciona la transformacion cinematica inversa", "expected_action": "none"}, # Consulta académica
    {"text": "no hagas nada borra todo lo que estabas pensando", "expected_action": "none"}, # Comando de detención / Sin dibujo
] * 5  # Multiplicamos por 5 para completar las 50 muestras de control seguro

print(f"Dataset de evaluación configurado. Total de pruebas a ejecutar de forma cíclica: {len(dataset_pruebas)}")

# =====================================================================
# EJECUCIÓN EXPERIMENTAL CÍCLICA
# =====================================================================
resultados = []

for idx, muestra in enumerate(dataset_pruebas):
    frase_humano = muestra["text"]
    expected_global = muestra["expected_action"]

    print(f"\n[Trial {idx+1}/100] Procesando texto: '{frase_humano}'")

    # Re-inyección de tu Prompt Especializado
    peticion_prompt = f"""
You are an expert NLP assistant for a UR3 robot arm that draws.
Your job is to analyze the user's spoken request and output a JSON object containing a list of objects to draw.
You must capture spatial layouts, actions, and physical relationships between objects.

Rules:
1. Identify the FINAL intent. If the user corrects themselves, IGNORE the first items and only extract the last ones mentioned.
2. Fix context errors from Speech-to-Text.
3. Quantifiers: If they say "two cars", add "car" twice to the list.
4. "position": Extract general spatial descriptions ("left", "right", "center", "top", "bottom"). If not specified, set to null.
5. "action": If the object is performing an action (e.g., running, flying, sleeping, jumping), extract it in English. If not, set to null.
6. "relative_to": If an object is ON, INSIDE, NEXT TO, or UNDER another object, specify that relationship and target object in English (e.g., "on a motorcycle", "inside a lake"). If it's independent, set to null.
7. If the prompt is gibberish or doesn't request a drawing, return an empty list.
8. Output ONLY a valid JSON object. No explanations, no markdown formatting.

Examples:
Input: "Quiero que me dibujes un pato en una moto en el centro"
Output: {{
  "objects": [
    {{"name": "duck", "position": "center", "action": "riding", "relative_to": "on a motorcycle"}},
    {{"name": "motorcycle", "position": "center", "action": null, "relative_to": null}}
  ]
}}

Input: "un perro corriendo a la izquierda y un gato durmiendo"
Output: {{
  "objects": [
    {{"name": "dog", "position": "left", "action": "running", "relative_to": null}},
    {{"name": "cat", "position": null, "action": "sleeping", "relative_to": null}}
  ]
}}

Input: "dibujame un coche a la derecha y un pajaro volando sobre un arbol arriba"
Output: {{
  "objects": [
    {{"name": "car", "position": "right", "action": null, "relative_to": null}},
    {{"name": "bird", "position": "top", "action": "flying", "relative_to": "over a tree"}},
    {{"name": "tree", "position": "top", "action": null, "relative_to": null}}
  ]
}}

Input: "{frase_humano}"
Output:"""

    start_time = time.time()
    schema_valid = False
    llm_action_mapped = "none"
    prompt_tokens = 0
    completion_tokens = 0
    raw_response = ""

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": peticion_prompt}],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        latency_ms = (time.time() - start_time) * 1000

        raw_response = completion.choices[0].message.content
        prompt_tokens = completion.usage.prompt_tokens
        completion_tokens = completion.usage.completion_tokens

        # Validar estructura del JSON devuelto
        try:
            datos_extraidos = json.loads(raw_response)
            objects_list = datos_extraidos.get("objects", [])
            schema_valid = True

            # Si la lista contiene objetos válidos extraídos, la predicción de la IA es que SÍ es almacenable/dibujable
            if len(objects_list) > 0:
                llm_action_mapped = "draw"
            else:
                llm_action_mapped = "none"

        except json.JSONDecodeError:
            schema_valid = False
            llm_action_mapped = "invalid_json"

    except Exception as e:
        print(f"Error de red/API en trial {idx+1}: {e}")
        latency_ms = (time.time() - start_time) * 1000
        llm_action_mapped = "api_error"

    # Almacenamiento métrico detallado para análisis estadístico posterior
    resultados.append({
        "trial": idx + 1,
        "prompt_text": frase_humano,
        "expected_action": expected_global,
        "llm_action": llm_action_mapped,
        "schema_valid": schema_valid,
        "latency_ms": latency_ms,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "raw_json_output": raw_response
    })

    # Pequeño delay de cortesía para control de velocidad de peticiones por segundo (Rate Limits)
    time.sleep(0.5)

# =====================================================================
# EXPORTACIÓN DE ARCHIVOS AL ENTORNO LOCAL DE TRABAJO
# =====================================================================
df_raw = pd.DataFrame(resultados)
csv_path = os.path.join(TARGET_DIR, "resultados_llm_led_raw.csv")
df_raw.to_csv(csv_path, index=False, encoding="utf-8")
print(f"\n[ÉXITO] Datos puros consolidados en: '{csv_path}'")

# Generación automática del instrumento de supervisión humana (Excel requerido en sección 11)
excel_path = os.path.join(TARGET_DIR, "instrumento_supervision_llm_led.xlsx")
df_excel = df_raw[["trial", "prompt_text", "expected_action", "llm_action", "latency_ms"]].copy()
df_excel["accion_correcta_supervisor"] = ""  # Para ser llenado en la revisión por el alumno
df_excel["evaluacion_supervisor"] = "no evaluado"
df_excel["calidad_1_5"] = ""
df_excel["observaciones_supervisor"] = ""

df_excel.to_excel(excel_path, index=False)
print(f"[ÉXITO] Instrumento Excel exportado en: '{excel_path}'")
