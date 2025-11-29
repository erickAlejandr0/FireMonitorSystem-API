# app/predictor.py

import numpy as np
import pandas as pd
from app.models.AI_model import get_modelo_y_scaler

def process_message(esp_id, payload):
    """
    Procesa los datos crudos de un ESP32, los escala, predice con el modelo
    correspondiente y devuelve predicción + probabilidades.
    """

    # ============================
    # 1. Extraer valores crudos
    # ============================
    try:
        humo = float(payload["humo"])
        temperatura = float(payload["temperatura"])
        llama = int(payload["llama"])
    except KeyError as e:
        return {"error": f"Falta el campo {e}"}
    
    hm = humo / 4095.0

    # Vector ordenado tal como fue durante el entrenamiento
    X = pd.DataFrame([[temperatura, hm, llama]],columns=["temperatura", "humo", "llama"])

    # ============================
    # 2. Obtener modelo correcto
    # ============================
    model, scaler = get_modelo_y_scaler(esp_id)

    # ============================
    # 3. Normalizar con su scaler
    # ============================
    X_scaled = scaler.transform(X)

    # ============================
    # 4. Predicción
    # ============================
    pred = model.predict(X_scaled)[0]

    # Probabilidades por clase
    probas = model.predict_proba(X_scaled)[0]
    clases = model.classes_

    idx = list(clases).index(pred)
    prob_pred = round(float(probas[idx]), 4)

    clases_riesgo = ["Alerta", "Crítico"]
    prob_incendio = sum(
        float(prob) for clase, prob in zip(model.classes_, model.predict_proba(X_scaled)[0])
        if clase in clases_riesgo
    )
    
    if prob_incendio < 0.25:
        riesgo = "Seguro"
    elif prob_incendio < 0.6:
        riesgo = "Alerta"
    else:
        riesgo = "Crítico"
    # ============================
    # 5. Respuesta final
    # ============================
    return {
        "esp32": esp_id,
        "temperatura": temperatura,
        "humo": humo,
        "llama": llama,
        "riesgo": riesgo,
        "probabilidades": (prob_incendio* 100)
    }
