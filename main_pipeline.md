---
title: Pipeline Conceptual
layout: default
parent: Reporte Final
nav_order: 6
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

    # Parámetros de red del UR3
    HOST = "192.168.1.100" 
    PORT = 30002
    
    try:
        robot_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        robot_socket.connect((HOST, PORT))
        print("¡Conectado al controlador CB3 del UR3!")

        # Iteración sobre los puntos para dibujar
        for wp in waypoints:
            # Comando de movimiento lineal en URScript
            comando = f"movel(p[{wp[0]}, {wp[1]}, {wp[2]}, 0, 3.14, 0], a=0.1, v=0.1)\n"
            robot_socket.send(comando.encode('utf8'))
            time.sleep(0.1) # Breve pausa para no saturar el buffer
        
        robot_socket.close()
        print("Trayectoria ejecutada con éxito.")
    except Exception as e:
        print(f"Error crítico en la comunicación robótica: {e}")

def ejecutar_pipeline_completo():
    # Ruta del archivo generado
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