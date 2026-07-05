import os
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, f1_score

TARGET_DIR = r"C:\Users\desqu\OneDrive\Desktop\Tec_emergentes"
csv_path = os.path.join(TARGET_DIR, "resultados_llm_led_raw.csv")

if not os.path.exists(csv_path):
    print(f"Error: No se encontró el archivo {csv_path}. Ejecuta primero eval_100.py")
    exit()

df = pd.read_csv(csv_path)

# Filtrar posibles errores críticos de API para cálculo puramente estadístico
df_clean = df[~df["llm_action"].isin(["api_error", "invalid_json"])].copy()

y_true = df_clean["expected_action"]
y_pred = df_clean["llm_action"]

# 1. Calcular Métricas de Clasificación Clásicas
accuracy = accuracy_score(y_true, y_pred)
macro_f1 = f1_score(y_true, y_pred, average='macro')
json_validity_rate = df["schema_valid"].mean()

print("\n========================================================")
print("             RESUMEN ESTADÍSTICO DEL EXPERIMENTO         ")
print("========================================================")
print(f"Pruebas Totales Procesadas: {len(df)}")
print(f"Accuracy de Clasificación Semántica: {accuracy:.4f}")
print(f"Macro F1-Score Global: {macro_f1:.4f}")
print(f"Tasa de Validez Estructura JSON (Schema Valid): {json_validity_rate:.4f}")
print(f"Latencia Media del Pipeline de Extracción: {df['latency_ms'].mean():.2f} ms")
print(f"Consumo Promedio de Tokens de Entrada (Prompt): {df['prompt_tokens'].mean():.1f}")
print(f"Consumo Promedio de Tokens de Salida (Completion): {df['completion_tokens'].mean():.1f}")
print("========================================================\n")

# Guardar Reporte de Clasificación en CSV
reporte = classification_report(y_true, y_pred, output_dict=True)
df_reporte = pd.DataFrame(reporte).transpose()
reporte_path = os.path.join(TARGET_DIR, "classification_report.csv")
df_reporte.to_csv(reporte_path)

# 2. Generación Matriz de Confusión Gráfica
labels_experiment = ["draw", "none"]
cm = confusion_matrix(y_true, y_pred, labels=labels_experiment)

fig, ax = plt.subplots(figsize=(6, 5))
cax = ax.matshow(cm, cmap=plt.cm.Greens)
fig.colorbar(cax)

ax.set_xticklabels([''] + labels_experiment)
ax.set_yticklabels([''] + labels_experiment)
ax.set_xlabel('Predicción del LLM (Llama 3.3)', fontweight='bold')
ax.set_ylabel('Clase Esperada (Dataset Real)', fontweight='bold')

# Insertar etiquetas numéricas en los cuadrantes de la matriz
for i in range(cm.shape[0]):
    for j in range(cm.shape[1]):
        ax.text(j, i, str(cm[i, j]), va='center', ha='center', 
                fontweight='bold', color='black', fontsize=12)

plt.title('Matriz de Confusión - Clasificación Semántica UR3', pad=20, fontweight='bold')
plt.tight_layout()

# Guardar imagen directamente en la ruta de trabajo
grafica_path = os.path.join(TARGET_DIR, "confusion_matrix.png")
plt.savefig(grafica_path, dpi=150)
plt.close()
print(f"[ÉXITO] Matriz de confusión guardada visualmente en: '{grafica_path}'")