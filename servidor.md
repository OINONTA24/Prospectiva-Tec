---
title: Servidor de Recepción
layout: default
parent: Reporte Final
nav_order: 6
---

# Código: Servidor de Recepción servidor.py

Este script actúa como el puente de comunicación principal entre el entorno de realidad mixta (Frontend) y el procesamiento pesado (Backend). Utiliza el framework **Flask** para levantar un servidor ligero en el puerto `5050`.

## ¿Qué hace este código?
1. **Escucha a Unity:** Recibe el archivo de audio (`.wav`) grabado por el usuario a través del micrófono de las Meta Quest 3.
2. **Conversión y Reenvío:** Convierte el archivo a formato `.mp3` para optimizar su tamaño y lo reenvía automáticamente al Servidor 2 (el motor de Inteligencia Artificial) mediante una petición HTTP POST.
3. **Almacenamiento de Trayectorias:** Una vez que la IA termina de procesar, este servidor recibe de vuelta un JSON con las coordenadas espaciales (los trazos UV) y las almacena temporalmente para que Unity pueda solicitarlas y dibujar el gemelo digital.

```python
from flask import Flask, request, jsonify, send_file
from datetime import datetime
from pydub import AudioSegment
import os
import requests
app = Flask(__name__)

contador_posts   = 0
ultimo_recibido  = None

ultimo_trayectoria = None
trayectoria_id     = 0  


@app.route("/", methods=["GET"])
def home():
    return f"""
    <h1>Servidor Flask vivo ✅</h1>
    <p>POSTs recibidos: <b>{contador_posts}</b></p>
    <p>Trayectorias recibidas: <b>{trayectoria_id}</b></p>
    <p><a href="/status">/status</a></p>
    <p><a href="/debug">/debug</a></p>
    <p><a href="/trayectoria">/trayectoria</a> (última trayectoria para Unity)</p>
    """

@app.route("/status", methods=["GET"])
def status():
    return jsonify({
        "server": "alive",
        "posts_recibidos": contador_posts,
        "trayectoria_id": trayectoria_id,
        "hay_trayectoria": ultimo_trayectoria is not None
    })

@app.route("/debug", methods=["GET"])
def debug():
    if ultimo_recibido is None:
        return jsonify({"status": "vacío", "message": "No ha llegado nada"})
    return jsonify(ultimo_recibido)

@app.route("/audio", methods=["POST", "GET"])
def recibir_audio():
    global contador_posts, ultimo_recibido

    print("\n" + "=" * 60)
    print("POST RECIBIDO:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("Content-Type:", request.content_type)
    contador_posts += 1

    if request.is_json:
        data = request.get_json()
        print("JSON recibido:", data)
        ultimo_recibido = {"tipo": "json", "data": data}
        return jsonify({"status": "ok", "tipo": "json", "recibido": data})

    if 'audio' in request.files:
        archivo  = request.files['audio']
        ruta_wav = "ultimo_audio.wav"
        ruta_mp3 = "ultimo_audio.mp3"

        archivo.save(ruta_wav)
        tam_wav_kb = os.path.getsize(ruta_wav) / 1024
        print(f"WAV recibido: {tam_wav_kb:.1f} KB → {ruta_wav}")

        audio = AudioSegment.from_wav(ruta_wav)
        audio.export(ruta_mp3, format="mp3", bitrate="128k")
        tam_mp3_kb = os.path.getsize(ruta_mp3) / 1024
        print(f"MP3 generado: {tam_mp3_kb:.1f} KB → {ruta_mp3}")

        url_tu_servidor = "[http://127.0.0.1:5000/recibir-orden](http://127.0.0.1:5000/recibir-orden)"
        try:
            print(f"Enviando audio automáticamente a la PC de IA: {url_tu_servidor}")
            with open(ruta_mp3, "rb") as f:
                # Se envía por POST con un timeout de seguridad de 10 segundos
                res_s2 = requests.post(url_tu_servidor, files={"audio": f}, timeout=120)
            print(f"Respuesta del Servidor 2: {res_s2.status_code}")
        except Exception as e:
            print(f"Advertencia: No se pudo enviar el audio al Servidor 2. {e}")

        ultimo_recibido = {
            "tipo": "mp3",
            "wav_kb": round(tam_wav_kb, 1),
            "mp3_kb": round(tam_mp3_kb, 1)
        }
        return jsonify({
            "status": "ok",
            "tipo": "mp3",
            "wav_kb": round(tam_wav_kb, 1),
            "mp3_kb": round(tam_mp3_kb, 1)
        })

    raw = request.get_data()
    print("Body raw recibido:", len(raw), "bytes")
    ultimo_recibido = {"tipo": "raw", "bytes": len(raw)}
    return jsonify({"status": "ok", "tipo": "raw", "bytes": len(raw)})

@app.route("/descargar-audio", methods=["GET"])
def descargar_audio():
    ruta = "ultimo_audio.mp3"
    if os.path.exists(ruta):
        return send_file(ruta, as_attachment=True)
    return jsonify({"status": "error", "message": "No hay audio disponible"}), 404

@app.route("/trayectoria", methods=["POST"])
def recibir_trayectoria():
    global ultimo_trayectoria, trayectoria_id

    if not request.is_json:
        return jsonify({"status": "error", "message": "Se esperaba JSON"}), 400

    data = request.get_json()

    if "strokes" not in data or not isinstance(data["strokes"], list):
        return jsonify({"status": "error", "message": "Falta el campo 'strokes'"}), 400

    trayectoria_id    += 1
    ultimo_trayectoria = data
    ultimo_trayectoria["_id"]        = trayectoria_id
    ultimo_trayectoria["_timestamp"] = datetime.now().isoformat()

    n_trazos = len(data["strokes"])
    n_puntos  = sum(len(s.get("points", [])) for s in data["strokes"])
    print(f"\n[/trayectoria] #{trayectoria_id} recibida: "
          f"{n_trazos} trazos, {n_puntos} puntos "
          f"({data.get('image_width',0)}x{data.get('image_height',0)}px)")

    return jsonify({
        "status": "ok",
        "id": trayectoria_id,
        "trazos": n_trazos,
        "puntos": n_puntos
    })


@app.route("/trayectoria", methods=["GET"])
def obtener_trayectoria():
    global ultimo_trayectoria

    if ultimo_trayectoria is None:
        return ("", 204)

    datos = ultimo_trayectoria
    ultimo_trayectoria = None  
    return jsonify(datos)

if __name__ == "__main__":
    print("=" * 60)
    print("Servidor Flask — UR3 Drawing Robot")
    print("Puerto: 5050")
    print("=" * 60)

    app.run(
        host="0.0.0.0",
        port=5050,
        debug=True,
        threaded=True
    )
```