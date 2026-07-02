---
layout: default
title: Pruebas y métricas
parent: Práctica 5
nav_order: 3
---

# Pruebas y métricas

Se utilizó el mismo prompt en los tres proveedores con configuración idéntica:

> **Prompt de prueba:**
> ```
> Explica qué es la odometría diferencial en un robot móvil de dos ruedas.
> Incluye:
> 1. explicación conceptual;
> 2. ecuaciones básicas;
> 3. ejemplo para estudiantes de ingeniería;
> 4. una limitación práctica.
> Responde en máximo 250 palabras.
> ```

**Configuración:** temperature = 0.7 · top_p = 0.9 · max_tokens = 300 · Perfil: Asistente genérico

---

## Capturas de pantalla

### Prueba 1 — Gemini API · `gemini-2.5-flash`

![Prueba 1 — Gemini API](../assets/img/practica5/prueba1-gemini.png)

**Respuesta generada:**

La odometría diferencial estima la pose de un robot móvil de dos ruedas midiendo el desplazamiento de cada rueda.

**1. Explicación Conceptual:** Se basa en que el movimiento del robot es la combinación de las rotaciones de sus dos ruedas motrices independientes. Conociendo los radios de las ruedas, la distancia entre ellas (ancho del eje) y los pulsos de los encoders de cada rueda, se puede calcular la distancia recorrida por cada rueda y, a partir de esto, el cambio en la posición (x, y) y orientación (θ) del robot.

**2. Ecuaciones Básicas:** Sean v_L y v_R las velocidades lineales de las ruedas izquierda y derecha, R el radio de las ruedas, L el ancho del eje:

```
v = (v_R + v_L) / 2
ω = (v_R - v_L) / L
Δθ = ω Δt
Δx = v cos(θ + Δθ/2) Δt
Δy = v sin(θ + Δθ/2) Δt
```

**3. Ejemplo:** Robot con R = 0.05 m, L = 0.2 m. En 1 segundo, rueda izquierda gira a 10 rad/s y derecha a 12 rad/s:
v_L = 0.05 × 10 = 0.5 m/s · v_R = 0.05 × 12 = 0.6 m/s · v = 0.55 m/s · ω = 0.5 rad/s
Δθ = 0.5 rad · Δx ≈ 0.519 m · Δy ≈ 0.135 m

**4. Limitación Práctica:** La odometría diferencial acumula errores con el tiempo debido a deslizamientos de las ruedas, imprecisiones en los parámetros del robot (R, L) y cuantificación de los encoders. Esto lleva a una deriva en la estimación de la posición real del robot.

---

### Prueba 2 — Groq API · `llama-3.3-70b-versatile`

![Prueba 2 — Groq API](../assets/img/practica5/prueba2-groq.png)

**Respuesta generada:**

La odometría diferencial es un método para estimar la posición y orientación de un robot móvil de dos ruedas. Conceptualmente, se basa en medir la diferencia en la distancia recorrida por cada rueda para calcular la velocidad angular y lineal del robot.

Las ecuaciones básicas son:
- Velocidad lineal: v = (v_r + v_l) / 2
- Velocidad angular: ω = (v_r - v_l) / d

donde v_r y v_l son las velocidades de las ruedas derecha e izquierda, y d es la distancia entre ellas.

**Ejemplo:** Si un robot tiene ruedas de 10 cm de diámetro y la rueda derecha gira a 50 rpm, mientras que la rueda izquierda gira a 40 rpm, la velocidad lineal sería de 0.45 m/s y la velocidad angular sería de 0.5 rad/s.

**Limitación práctica:** La odometría diferencial se ve afectada por la desviación en la medición de las velocidades de las ruedas y el desgaste de los neumáticos, lo que puede llevar a errores en la estimación de la posición y orientación del robot.

---

### Prueba 3 — Ollama local · `qwen2.5:7b`

![Prueba 3 — Ollama local](../assets/img/practica5/prueba3-ollama.png)

**Respuesta generada:**

1. **Explicación Conceptual:** La odometría diferencial mide la distancia recorrida por cada rueda del robot móvil para determinar su posición y orientación. En un robot con dos ruedas, calcula el desplazamiento total usando las rotaciones de las ruedas.

2. **Ecuaciones Básicas:** Si D_L es la distancia recorrida por la rueda izquierda y D_R para la derecha:
```
Δx = (1/2)(D_L + D_R) cos(θ)
Δy = (1/2)(D_L + D_R) sin(θ)
Δθ = |D_R - D_L| / r
```
Donde r es el radio medio de las ruedas.

3. **Ejemplo:** Robot con radios 0.1 m y distancias recorridas D_L = 2π y D_R = 2.5π:
Δx = 2.25π cos(θ) · Δy = 2.25π sin(θ) · Δθ = 5π rad

4. **Limitación Práctica:** La odometría diferencial es imprecisa debido a factores como la desigualdad en el radio de las ruedas, fricción variable y desgaste. Estos errores acumulan con el tiempo, reduciendo la precisión del posicionamiento del robot.

---

## Tabla de caracterización

| Variable | Ollama local | Gemini API | Groq API |
|---|---|---|---|
| Proveedor | Ollama | Google | Groq |
| Modelo | `qwen2.5:7b` | `gemini-2.5-flash` | `llama-3.3-70b-versatile` |
| Tipo | Abierto / local | Cerrado / remoto | Abierto / remoto |
| Parámetros | 7B aprox. | No divulgado | 70B |
| Contexto máximo | 128 000 tokens | 1 048 576 tokens | 128 000 tokens |
| Tokens entrada | 201 | 195 | 221 |
| Tokens salida | 470 | 663 | 282 |
| Tokens totales | 671 | 858 | 503 |
| Tiempo total | 39.178 s | 3.809 s | 1.943 s |
| Tokens/s | 17.8 | 174.0 | 145.1 |
| ¿Requiere internet? | No | Sí | Sí |
| ¿Requiere API key? | No | Sí | Sí |
| ¿Tiene costo? | Hardware local | Tier gratuito limitado / pago | Free plan limitado / pago |
| Privacidad | Alta | Depende del proveedor | Depende del proveedor |
| Facilidad de integración | Media | Alta | Alta |

> **Nota sobre tokens/s:** Para Gemini y Groq el valor se calcula con el tiempo total de pared (incluye latencia de red), no con el tiempo de inferencia puro del modelo. Para Ollama el valor proviene de `eval_duration` (26.464 s), que mide únicamente el tiempo de generación en GPU/CPU local.

---

## Tabla de evaluación cualitativa

Escala: 1 = deficiente · 2 = básico · 3 = aceptable · 4 = bueno · 5 = excelente

| Criterio | Ollama local | Gemini API | Groq API |
|---|---|---|---|
| Claridad conceptual | 3 | 5 | 4 |
| Precisión técnica | 3 | 5 | 3 |
| Uso correcto de ecuaciones | 2 | 5 | 3 |
| Calidad del ejemplo | 2 | 5 | 3 |
| Nivel adecuado para ingeniería | 3 | 5 | 4 |
| Identificación de limitaciones | 3 | 5 | 3 |
| Alucinaciones o errores | 3 | 5 | 3 |
| Utilidad final | 3 | 5 | 4 |

**Observaciones por modelo:**

- **Ollama (qwen2.5:7b):** La ecuación Δθ = \|D_R − D_L\| / r utiliza el radio de rueda `r` en el denominador, cuando debería usar el ancho del eje `L`. El ejemplo calcula Δθ = 5π rad (≈ 1 570°), lo cual es físicamente irreal para un paso de tiempo. Las ecuaciones de LaTeX se muestran como texto plano porque el frontend no renderiza notación matemática.

- **Gemini (gemini-2.5-flash):** Respuesta técnicamente más completa: incluye la corrección del ángulo medio en las ecuaciones de posición (θ + Δθ/2), el ejemplo es numéricamente consistente y la limitación menciona tres fuentes de error específicas (deslizamiento, parámetros R y L, cuantificación de encoders).

- **Groq (llama-3.3-70b-versatile):** Respuesta concisa y bien estructurada, pero el ejemplo numérico (diámetro = 10 cm, 50 rpm vs 40 rpm → v = 0.45 m/s) presenta inconsistencias al verificar el cálculo. No incluye las ecuaciones de actualización de pose (Δx, Δy).
