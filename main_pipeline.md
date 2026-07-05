---
title: Flujo de construcción
layout: default
parent: Reporte Final
nav_order: 5
---

# Código: Orquestador Conceptual (`main_pipeline.py`)

A lo largo del proyecto se estructuró un script integrador a modo de esquema o prueba de escritorio. Aunque la lógica final de ejecución del hardware se trasladó directamente al servidor de Inteligencia Artificial para reducir la latencia de red, este archivo ilustra de manera limpia y modular cómo interactúan conceptualmente las funciones.

## ¿Qué hace este código?
Muestra el *pipeline* del proyecto como funciones independientes. Permite validar los modelos paso a paso en entornos locales sin necesidad de encender los servidores web, útil para diagnóstico y depuración antes de conectar el brazo robótico real.

```python
import socket
import time
from servidor_ia import transcribir_audio, obtener_intencion, procesar_coordenadas_visuales

def enviar_a_robot(waypoints):

    HOST = "192.168.1.100" 
    PORT = 30002
    
    try:
        robot_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        robot_socket.connect((HOST, PORT))
        print("¡Conectado al controlador CB3 del UR3!")

        for wp in waypoints:
            comando = f"movel(p[{wp[0]}, {wp[1]}, {wp[2]}, 0, 3.14, 0], a=0.1, v=0.1)\n"
            robot_socket.send(comando.encode('utf8'))
            time.sleep(0.1) 
        
        robot_socket.close()
        print("Trayectoria ejecutada con éxito.")
    except Exception as e:
        print(f"Error crítico en la comunicación robótica: {e}")

def ejecutar_pipeline_completo():

    ruta_audio = "audio_files/input_audio.wav"
    
    print("1. Analizando voz...")
    texto = transcribir_audio(ruta_audio)
    
    print("2. Extrayendo intención estructurada...")
    sujeto = obtener_intencion(texto)
    
    print("3. Generando mapa de coordenadas...")
    waypoints = procesar_coordenadas_visuales(sujeto)
    
    print("4. Transmitiendo a hardware físico...")
    enviar_a_robot(waypoints)

if __name__ == '__main__':
    ejecutar_pipeline_completo()
```

## Desglose de las partes clave

### 1. La importación: el mapa de las tres etapas de IA

```python
from servidor_ia import transcribir_audio, obtener_intencion, procesar_coordenadas_visuales
```

Esta línea es la columna vertebral conceptual de todo el proyecto. Cada nombre importado representa, en el papel, una de las etapas de IA descritas en la sección **Servidor de IA y Robótica**:

| Función | Modelo de IA detrás | Rol en el pipeline |
|---|---|---|
| `transcribir_audio` | **Whisper** | STT — convierte el audio grabado por el usuario en texto |
| `obtener_intencion` | **Llama 3.3** (vía Groq) | Interpreta el texto y lo estructura como JSON |
| `procesar_coordenadas_visuales` | **OpenAI** (imagen) + **OpenCV** (visión) | Genera la silueta del objeto y la convierte en coordenadas dibujables |

> **Nota para quien lea el repositorio:** en la implementación real (`servidor_ia.py`) estas tres etapas no existen como funciones separadas con estos nombres exactos; están fusionadas dentro de un único endpoint Flask (`/recibir-orden`), justamente para evitar saltos de red innecesarios entre procesos. Por eso `main_pipeline.py` no puede ejecutarse tal cual contra el servidor real: es una prueba de escritorio que documenta *cómo se pensó* la arquitectura antes de fusionar las fases por razones de rendimiento.

### 2. `enviar_a_robot()`: el puente de bajo nivel hacia el controlador físico

Esta función se conecta directamente al controlador **CB3** del UR3 usando un socket TCP crudo sobre el puerto **30002**, que es una de las interfaces de "cliente secundario" que expone el controlador para recibir comandos en **URScript** (el lenguaje nativo de Universal Robots) en tiempo real, sin pasar por la interfaz gráfica del robot.

Puntos clave:
- Cada punto de la trayectoria (`waypoints`) se traduce en un comando `movel(p[x, y, z, rx, ry, rz], a=..., v=...)`, donde `p[...]` es una pose cartesiana absoluta.
- La orientación se deja fija en `(0, 3.14, 0)` — una rotación de ~180° sobre el eje Y — pensada para que la herramienta (plumón/efector) quede perpendicular al plano de dibujo.
- `a=0.1` y `v=0.1` son la aceleración y velocidad máximas, deliberadamente bajas para privilegiar precisión y seguridad sobre velocidad.
- El `time.sleep(0.1)` entre envíos evita saturar el buffer de comandos del controlador, que procesa las instrucciones de forma secuencial.
- El `try/except` envuelve toda la comunicación: si el robot no responde o la red falla, el error se reporta pero no interrumpe el resto del programa.

### 3. `ejecutar_pipeline_completo()`: las cuatro fases en secuencia

Esta función es la versión "legible" del flujo completo del gemelo digital: voz → intención → imagen/coordenadas → movimiento. Cada `print` marca una fase que, en la implementación real, corresponde exactamente a las **FASE 1 a FASE 4** dentro de `servidor_ia.py` (ver esa sección para el detalle técnico de cada una).

## ¿Por qué conservar este archivo en el repositorio?

Aunque no se ejecuta en producción, cumple un rol de documentación viva: cualquier persona que quiera entender el flujo de datos de punta a punta (voz → intención → imagen → coordenadas → movimiento del brazo) puede leer este archivo de arriba a abajo sin tener que rastrear la lógica —mucho más densa— repartida entre los dos servidores Flask reales.
