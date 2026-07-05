---
title: Como construye
layout: default
parent: Reporte Final
nav_order: 7
---

# Código: Servidor de IA (`servidor_ia.py`)

Este módulo es el núcleo computacional del proyecto. Funciona como un segundo servidor independiente que procesa la carga intensiva de Inteligencia Artificial y Visión Computacional.

## ¿Qué hace este código?
1. **Pipeline Generativo:** Integra Whisper para la transcripción de audio, un LLM de Groq (Llama 3.3) para el razonamiento semántico y la API de OpenAI (DALL-E) para la generación visual.
2. **Transformación Espacial:** Utiliza OpenCV para detectar los contornos de la imagen generada, filtrar trazos duplicados mediante el algoritmo de *Douglas-Peucker* y mapearlos en coordenadas XY.
3. **Control Físico Directo:** Ejecuta la librería `urx` para conectarse por Ethernet a la IP del brazo robótico (192.168.3.75) y mover físicamente el efector final mediante comandos absolutos de la API nativa de Universal Robots.

```python
import os
import json
import base64
import requests
import cv2
import numpy as np
import whisper
import time 
from groq import Groq
from dotenv import load_dotenv
from openai import OpenAI
from flask import Flask, request, jsonify

# CONFIGURACIÓN INICIAL
app = Flask(__name__)

load_dotenv("openai.env") 
client_openai = OpenAI()
client_groq = Groq(api_key="TU_GROQ_API_KEY") 
os.environ["PATH"] += os.pathsep + r"C:\ffmpeg\bin"

URL_COMPANERA_TRAYECTORIA = "[http://127.0.0.1:5050/trayectoria](http://127.0.0.1:5050/trayectoria)"

print("\nCargando modelo de voz Whisper en memoria...")
modelo_voz = whisper.load_model("base")
print("Modelo cargado exitosamente.")

@app.route('/recibir-orden', methods=['POST'])
def procesar_orden():
    print("\n" + "="*50)
    print("🎯 ¡PETICIÓN RECIBIDA DESDE EL SERVIDOR 1!")
    print("="*50)

    if 'audio' not in request.files:
        return jsonify({"error": "No se encontró audio"}), 400

    archivo = request.files['audio']
    ARCHIVO_AUDIO = "audio_recibido.mp3.mpeg"
    archivo.save(ARCHIVO_AUDIO)

    try:
        tiempo_inicio_total = time.time()

        # FASE 1: STT Y EXTRACCIÓN LLM
        print("\n[FASE 1] Transcribiendo audio...")
        t_inicio_whisper = time.time() 
        resultado_stt = modelo_voz.transcribe(ARCHIVO_AUDIO, language="es")
        t_fin_whisper = time.time()
        
        frase_humano = resultado_stt["text"]
        print(f"-> [STT] Escuchado: '{frase_humano}'")

        peticion_prompt = f"""
        You are an expert NLP assistant for a UR3 robot arm that draws. 
        Your job is to analyze the user's spoken request and output a JSON object containing a list of objects to draw.
        CRITICAL: Output ONLY a valid JSON object.
        Input: "{frase_humano}"
        Output:"""

        print("\nEnviando a Groq (Llama-3.3-70b)...")
        completion = client_groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": peticion_prompt}],
            temperature=2.0,
            response_format={"type": "json_object"} 
        )
        
        datos_extraidos = json.loads(completion.choices[0].message.content)
        objects_list = [obj for obj in datos_extraidos.get("objects", []) if obj.get('name')]
        
        if not objects_list:
            return jsonify({"error": "No se entendieron objetos dibujables"}), 400

        # FASE 2: COMPOSICIÓN Y DALL-E
        print("\n[FASE 2] Solicitando imagen a OpenAI...")
        MASTER_PROMPT = f"A single cohesive solid black silhouette scene containing {objects_list[0].get('name')}. Pure white background, completely flat."

        response = client_openai.images.generate(model="gpt-image-2", prompt=MASTER_PROMPT, size="1024x1024", n=1)
        datos_imagen = response.data[0]
        
        img_data = requests.get(datos_imagen.url).content
        with open("1_silueta_ia.png", "wb") as h:
            h.write(img_data)

        # FASE 3: OPENCV Y ENVÍO DE TRAYECTORIA
        print("\n[FASE 3] Calculando trayectoria y coordenadas UV...")
        opencv_image = cv2.imread("1_silueta_ia.png")
        gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        contours_robot, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        
        trazos_coordenadas_robot = []
        perimetros_procesados = []
        TOLERANCIA_EPSILON = 0.001

        for cnt in contours_robot:
            perimetro = cv2.arcLength(cnt, True)
            if perimetro < 20: continue 
                
            es_duplicado = any(abs(perimetro - p) / p < 0.05 for p in perimetros_procesados)
            if es_duplicado: continue
            
            perimetros_procesados.append(perimetro)
            approx = cv2.approxPolyDP(cnt, TOLERANCIA_EPSILON * perimetro, True)
            
            puntos_trazo = [[int(pt[0][0]), int(pt[0][1])] for pt in approx]
            trazos_coordenadas_robot.append(puntos_trazo)

        alto_imagen, ancho_imagen = opencv_image.shape[:2]
        datos_trayectoria = {
            "image_width": ancho_imagen,
            "image_height": alto_imagen,
            "strokes": []
        }

        for trazo in trazos_coordenadas_robot:
            if len(trazo) < 2: continue
            lista_puntos = [{"u": round(x/ancho_imagen, 4), "v": round(1.0 - (y/alto_imagen), 4)} for (x, y) in trazo]
            datos_trayectoria["strokes"].append({"points": lista_puntos})

        try:
            requests.post(URL_COMPANERA_TRAYECTORIA, json=datos_trayectoria, timeout=10)
        except Exception as red_err:
            print(f"⚠️ Error de red al enviar al Servidor 1: {red_err}")

        # FASE 4: MOVER EL ROBOT FÍSICO DESDE PYTHON
        print("\n[FASE 4] Conectando al UR3 físico y ejecutando movimientos...")
        try:
            import urx
            IP_ROBOT_FISICO = "192.168.3.75"
            robot = urx.Robot(IP_ROBOT_FISICO)

            X_ORIGEN = 0.400   
            Y_ORIGEN = -0.200   
            Z_DIBUJO = 0.150    
            Z_AIRE = 0.200      
            ANCHO_PIZARRON = 0.400 
            rx, ry, rz = 0.0, 3.1416, 0.0 
            v = 0.05
            a = 0.1

            robot.movel((X_ORIGEN, Y_ORIGEN, Z_AIRE, rx, ry, rz), a, v)

            for trazo in datos_trayectoria["strokes"]:
                primer_punto = True

                for punto in trazo["points"]:
                    x_real = X_ORIGEN + (punto["u"] * ANCHO_PIZARRON)
                    y_real = Y_ORIGEN + (punto["v"] * ANCHO_PIZARRON) 

                    if primer_punto:
                        robot.movel((x_real, y_real, Z_AIRE, rx, ry, rz), a, v)
                        robot.movel((x_real, y_real, Z_DIBUJO, rx, ry, rz), a, v)
                        primer_punto = False
                    else:
                        robot.movel((x_real, y_real, Z_DIBUJO, rx, ry, rz), a, v)
                
                # Sube el plumón donde terminó el ciclo
                robot.movel((X_ORIGEN, Y_ORIGEN, Z_AIRE, rx, ry, rz), a, v)

            robot.movel((X_ORIGEN, Y_ORIGEN, Z_AIRE, rx, ry, rz), a, v)
            robot.close()

        except Exception as e_robot:
            print(f"❌ Error controlando el UR3 físico: {e_robot}")

        return jsonify({"status": "éxito", "mensaje": "Pipeline completado."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

## Desglose de las partes clave

### 1. Inicialización: cargar el modelo pesado una sola vez

```python
modelo_voz = whisper.load_model("base")
```

Whisper se carga en memoria **al arrancar el servidor**, no dentro de cada petición. Es la diferencia entre esperar unos segundos una sola vez al iniciar el proceso, o esperar ese mismo costo en cada orden de voz del usuario — una decisión de diseño clave para mantener la latencia baja en un flujo interactivo.

Otros detalles de esta sección:
- `load_dotenv("openai.env")` carga la API key de OpenAI desde un archivo de entorno, siguiendo la buena práctica de no hardcodear credenciales.
- `client_groq = Groq(api_key="TU_GROQ_API_KEY")`, en cambio, sí trae la key escrita directamente en el código como *placeholder* — vale la pena reemplazar esa línea por una variable de entorno antes de subir el proyecto a un repositorio público.
- `os.environ["PATH"] += ...C:\ffmpeg\bin` es un ajuste específico de Windows: tanto Whisper como `pydub` (en `servidor.py`) dependen de `ffmpeg` para decodificar audio, y esta línea garantiza que el ejecutable sea visible para esos procesos.

> **Nota:** al igual que en `servidor.py`, la constante `URL_COMPANERA_TRAYECTORIA` conserva corchetes y paréntesis de un enlace en formato Markdown mal pegado. Como está escrita, la cadena no es una URL válida; debería quedar simplemente como `http://127.0.0.1:5050/trayectoria`.

### 2. FASE 1 — De la voz a un JSON estructurado (Whisper → Llama 3.3)

Primero, `modelo_voz.transcribe(ARCHIVO_AUDIO, language="es")` transcribe el audio forzando el idioma español (evita que Whisper intente detectar el idioma automáticamente, lo cual es más rápido y más preciso cuando ya se sabe el idioma de antemano).

El texto resultante se inserta en un *prompt* que se envía a **Llama 3.3** a través de Groq. Dos detalles técnicos importan aquí:
- `response_format={"type": "json_object"}` obliga al modelo a devolver JSON válido, evitando el trabajo extra de parsear texto libre en busca de una estructura.
- `temperature=2.0` es un valor muy alto (la escala típica va de 0 a 2). Con temperaturas cercanas al máximo, el modelo prioriza la variedad/creatividad sobre la consistencia — útil si se busca que interprete peticiones ambiguas de forma más libre, pero también aumenta el riesgo de que la extracción de objetos sea menos predecible. Si en algún momento la extracción de intención se vuelve inestable, este es el primer parámetro a revisar (valores entre 0 y 0.5 son más típicos para tareas de extracción estructurada).
- La línea `objects_list = [obj for obj in ... if obj.get('name')]` filtra de forma defensiva cualquier objeto mal formado que el LLM pudiera haber devuelto sin el campo `name`.

### 3. FASE 2 — Ingeniería de prompt para una imagen "procesable" (OpenAI)

```python
MASTER_PROMPT = f"A single cohesive solid black silhouette scene containing {objects_list[0].get('name')}. Pure white background, completely flat."
```

Este prompt no es solo una descripción visual: está diseñado a propósito para lo que viene después en OpenCV. Pedir explícitamente una **silueta sólida negra sobre fondo blanco puro y completamente plana** simplifica al máximo el trabajo de segmentación — sin gradientes, sombreados ni texturas, el umbral binario de la fase siguiente puede separar figura y fondo de forma limpia y determinista.

Nótese también que solo se usa `objects_list[0]`: aunque Llama 3.3 puede extraer una lista completa de objetos, la versión actual del pipeline solo dibuja el primero. Es una simplificación de alcance del prototipo, no una limitación técnica del LLM.

### 4. FASE 3 — De píxeles a coordenadas de robot (OpenCV)

Esta es la fase más densa del archivo. En orden:

1. **Escala de grises + umbral de Otsu** (`cv2.threshold(..., THRESH_BINARY_INV + THRESH_OTSU)`): binariza la imagen sin necesidad de ajustar manualmente el valor de corte — Otsu lo calcula automáticamente a partir del histograma, y `THRESH_BINARY_INV` invierte la imagen para que la silueta (negra) quede como primer plano blanco.
2. **`cv2.findContours(..., RETR_LIST, CHAIN_APPROX_NONE)`**: extrae todos los contornos como una lista plana (sin jerarquía padre-hijo) y sin comprimir puntos todavía — la compresión real ocurre a propósito más adelante, con Douglas-Peucker.
3. **Filtrado de ruido** (`if perimetro < 20: continue`): descarta contornos minúsculos que suelen ser artefactos de compresión de la imagen, no formas reales.
4. **Deduplicación por perímetro**: OpenCV frecuentemente detecta el borde interior y el borde exterior de una misma silueta como dos contornos casi idénticos. Comparar perímetros con una tolerancia del 5% evita que el robot dibuje el mismo trazo dos veces.
5. **Simplificación con Douglas-Peucker** (`cv2.approxPolyDP(cnt, 0.001 * perimetro, True)`): reduce la cantidad de puntos del contorno preservando su forma general. Esto es crítico para el robot: menos puntos significa menos comandos `movel` por trazo, movimientos más fluidos y menor carga en la comunicación con el controlador.
6. **Normalización a coordenadas UV**: `u = x/ancho`, `v = 1 - y/alto`. La inversión del eje Y es necesaria porque en una imagen el origen (0,0) está arriba a la izquierda, mientras que la convención UV — la misma que usa Unity para mapear texturas — ubica el origen abajo a la izquierda.

Al final de la fase, el resultado se reenvía al Servidor de Recepción (`requests.post(URL_COMPANERA_TRAYECTORIA, ...)`) envuelto en un `try/except` con timeout corto: si esa llamada falla, el error se registra pero **no** detiene el pipeline — el robot puede seguir dibujando aunque Unity se quede sin datos para el gemelo digital en esa ejecución.

### 5. FASE 4 — Control físico directo con `urx`

La última fase abandona las coordenadas normalizadas y las traduce al espacio real de trabajo del robot:

```python
x_real = X_ORIGEN + (punto["u"] * ANCHO_PIZARRON)
y_real = Y_ORIGEN + (punto["v"] * ANCHO_PIZARRON)
```

Aquí `X_ORIGEN`/`Y_ORIGEN` ubican la esquina del "pizarrón" en el sistema de coordenadas del robot, y `ANCHO_PIZARRON` escala el rango `[0,1]` de UV al tamaño físico real del área de dibujo. Un detalle a tener en cuenta: se usa el mismo `ANCHO_PIZARRON` para escalar tanto X como Y, lo que asume un área de dibujo cuadrada — si la imagen generada no fuera cuadrada, esto podría introducir una ligera distorsión de proporciones.

El resto de la fase es el patrón clásico de un plotter/dibujo con brazo robótico:
- Orientación fija de la herramienta (`rx, ry, rz = 0, 3.1416, 0`) y velocidades bajas (`v=0.05`, `a=0.1`) para privilegiar precisión sobre velocidad.
- Por cada trazo, el primer punto se aborda primero en el aire (`Z_AIRE`) y luego se desciende (`Z_DIBUJO`) — esto evita que el efector arrastre el plumón desde el punto final del trazo anterior.
- Al terminar cada trazo, el brazo vuelve a subir antes de iniciar el siguiente.
- `robot.close()` libera limpiamente la conexión Ethernet con el controlador al finalizar.

Todo el bloque está envuelto en su propio `try/except`, de modo que un fallo de conexión con el brazo físico no interrumpe el resto de la respuesta HTTP — el endpoint sigue devolviendo un JSON de estado en cualquier caso.
