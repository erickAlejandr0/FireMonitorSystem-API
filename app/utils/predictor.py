# app/predictor.py

import numpy as np
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
        humo = float(payload["humo_ao"])
        temp = float(payload["temp_ao"])
        llama = int(payload["llama_do"])
    except KeyError as e:
        return {"error": f"Falta el campo {e}"}

    # Vector ordenado tal como fue durante el entrenamiento
    X = np.array([[temp, humo, llama]],dtype=float)

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

    prob_dict = {
        clase: round(float(prob), 4)
        for clase, prob in zip(clases, probas)
    }

    # ============================
    # 5. Respuesta final
    # ============================
    return {
        "esp32": esp_id,
        "entrada_cruda": {
            "temp_ao": temp,
            "humo_ao": humo,
            "llama_do": llama
        },
        "prediccion": pred,
        "probabilidades": prob_dict
    }
