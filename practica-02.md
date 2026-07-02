---
layout: default
title: Práctica 2
nav_order: 3
has_children: true
---

# Práctica 2 — Selección de modelos y benchmark de rendimiento

Esta práctica corresponde a la asignatura **Prospectiva de la Tecnología** (IE127), impartida en la Universidad Iberoamericana Ciudad de México durante el verano 2026.

El objetivo es identificar los modelos de IA más adecuados para el proyecto integrador, evaluar su rendimiento mediante un benchmark controlado y analizar el efecto de los parámetros de inferencia sobre la calidad y latencia de las respuestas.

---

## Contenido

- [Parte A — Matriz de decisión de modelos](matriz-decision.md)
- [Parte B — Benchmark de modelos](benchmark-modelos.md)
- [Parte C — Variación de parámetros](variacion-parametros.md)

---

## Contexto del proyecto

El proyecto integrador consiste en un sistema de generación de sketches a partir de comandos de voz. El pipeline completo es:

**Voz del usuario → STT → texto → LLM → JSON con características → modelo generador de imagen → sketch**

Cada componente del pipeline requiere un modelo con características específicas, lo que justifica el proceso de selección y benchmark documentado en esta práctica.
