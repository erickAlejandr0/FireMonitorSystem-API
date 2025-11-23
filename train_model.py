# train_model.py
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
from pathlib import Path


# 1. Crear dataset simulado

np.random.seed(42)
n = 1000

temperatura = np.random.uniform(20, 120, n)   # °C
humo = np.random.uniform(0, 1, n)             # nivel 0 a 1
tamaño = np.random.uniform(50, 500, n)        # m²

# Regla simple para generar probabilidades de riesgo
riesgo = []
for t, h, s in zip(temperatura, humo, tamaño):
    prob = (t / 120) * 0.6 + h * 0.3 + (s / 500) * 0.1  # ponderación
    if prob < 0.3:
        riesgo.append("Seguro")
    elif prob < 0.6:
        riesgo.append("Alerta")
    else:
        riesgo.append("Crítico")

data = pd.DataFrame({
    "temperatura": temperatura,
    "humo": humo,
    "tamaño": tamaño,
    "riesgo": riesgo
})


# 2. Entrenar modelo

X = data[["temperatura", "humo", "tamaño"]]
y = data["riesgo"]

modelo = RandomForestClassifier(n_estimators=100, random_state=42)
modelo.fit(X, y)


# 3. Guardar modelo entrenado

output_path = Path("modelo_incendios.pkl")
joblib.dump(modelo, output_path)
print(f"Modelo entrenado y guardado en: {output_path.resolve()}")
print("Clases del modelo:", modelo.classes_)


# 4. Prueba rápida: probabilidades de incendio

ejemplo = np.array([[85, 0.7, 100]])  # temperatura, humo, tamaño
probas = modelo.predict_proba(ejemplo)[0]

# Mostrar probabilidad de cada clase
for clase, prob in zip(modelo.classes_, probas):
    print(f"{clase}: {round(prob*100,2)}%")

# Predicción final
pred = modelo.predict(ejemplo)[0]
print(f"Predicción final: {pred}")
