---
layout: default
title: Código de análisis
parent: Práctica 6
nav_order: 2
---

# Código de análisis

`analizar_resultados.py` toma el CSV crudo generado por `eval_100.py` y calcula las métricas de clasificación clásicas (accuracy, F1 macro, matriz de confusión) usando `scikit-learn`.

Código completo: [`evaluacion-p6/analizar_resultados.py`](https://github.com/oinonta24/Prospectiva-Tec/blob/main/evaluacion-p6/analizar_resultados.py)

---

## Propósito

Extraer y procesar los indicadores matemáticos de la matriz de datos crudos, filtrando primero los errores críticos de infraestructura (fallas de red o JSON inválido) para que no contaminen el cálculo puramente semántico.

```python
df = pd.read_csv(csv_path)

# Filtrar posibles errores críticos de API para cálculo puramente estadístico
df_clean = df[~df["llm_action"].isin(["api_error", "invalid_json"])].copy()

y_true = df_clean["expected_action"]
y_pred = df_clean["llm_action"]
```

En esta corrida `df_clean` es idéntico a `df` (100/100 filas), porque no hubo ningún `api_error` ni `invalid_json` — ver [Pruebas y métricas]({% link p6-pruebas.md %}).

---

## Cálculo de métricas

```python
accuracy = accuracy_score(y_true, y_pred)
macro_f1 = f1_score(y_true, y_pred, average='macro')
json_validity_rate = df["schema_valid"].mean()

print(f"Accuracy de Clasificación Semántica: {accuracy:.4f}")
print(f"Macro F1-Score Global: {macro_f1:.4f}")
print(f"Tasa de Validez Estructura JSON (Schema Valid): {json_validity_rate:.4f}")
print(f"Latencia Media del Pipeline de Extracción: {df['latency_ms'].mean():.2f} ms")
print(f"Consumo Promedio de Tokens de Entrada (Prompt): {df['prompt_tokens'].mean():.1f}")
print(f"Consumo Promedio de Tokens de Salida (Completion): {df['completion_tokens'].mean():.1f}")
```

`json_validity_rate` se calcula sobre `df` completo (no `df_clean`), porque es precisamente la métrica que mide si hubo fallas de esquema — filtrarlas antes ocultaría el problema que se quiere medir.

---

## Exportar el reporte de clasificación

```python
reporte = classification_report(y_true, y_pred, output_dict=True)
df_reporte = pd.DataFrame(reporte).transpose()
df_reporte.to_csv(os.path.join(TARGET_DIR, "classification_report.csv"))
```

`classification_report(output_dict=True)` entrega precision, recall, F1 y soporte por clase (`draw`, `none`), más las filas agregadas `accuracy`, `macro avg` y `weighted avg`. Convertir el diccionario a `DataFrame.transpose()` es lo que produce el CSV tabular usado en [Pruebas y métricas]({% link p6-pruebas.md %}).

---

## Matriz de confusión

```python
labels_experiment = ["draw", "none"]
cm = confusion_matrix(y_true, y_pred, labels=labels_experiment)

fig, ax = plt.subplots(figsize=(6, 5))
cax = ax.matshow(cm, cmap=plt.cm.Greens)
fig.colorbar(cax)

ax.set_xticklabels([''] + labels_experiment)
ax.set_yticklabels([''] + labels_experiment)
ax.set_xlabel('Predicción del LLM (Llama 3.3)', fontweight='bold')
ax.set_ylabel('Clase Esperada (Dataset Real)', fontweight='bold')

for i in range(cm.shape[0]):
    for j in range(cm.shape[1]):
        ax.text(j, i, str(cm[i, j]), va='center', ha='center', fontweight='bold')

plt.savefig(os.path.join(TARGET_DIR, "confusion_matrix.png"), dpi=150)
```

`labels=labels_experiment` fija el orden `["draw", "none"]` explícitamente en filas y columnas, para que la diagonal principal siempre corresponda a los aciertos sin depender del orden alfabético por defecto de `scikit-learn`.

---

## Posibles extensiones

La guía de la práctica sugiere además graficar la latencia por iteración, un boxplot de latencias y la relación tokens-vs-latencia (ver sección 16 de la guía). Esta versión del script se limita a la matriz de confusión y al `classification_report.csv`; una extensión natural sería añadir:

```python
plt.plot(df["trial"], df["latency_ms"], marker="o")
plt.axhline(df["latency_ms"].quantile(0.95), linestyle="--", label="P95")
plt.axhline(df["latency_ms"].quantile(0.99), linestyle="--", label="P99")
```

para visualizar directamente los percentiles reportados en [Pruebas y métricas]({% link p6-pruebas.md %}), en vez de calcularlos aparte.
