# app/predictor.py

import requests
import os

MODEL_URL = os.getenv("MODEL_URL") # Nombre del contenedor Edge Impulse

def process_message(esp_id, payload):
    # ============================
    # 1. Extraer valores crudos
    # ============================
    try:
        humo = float(payload["humo"])
        temperatura = float(payload["temperatura"])
        llama = int(payload["llama"])
    except KeyError as e:
        return {"error": f"Falta el campo {e}"}

    # ============================
    # 2. Vector de entrada EI
    # ============================
    features = [temperatura, humo, llama]

    # ============================
    # 3. Llamar contenedor EI
    # ============================
    try:
        response = requests.post(MODEL_URL, json={"features": features}, timeout=2)
        result = response.json()
    except Exception as e:
        return {"error": f"No se pudo conectar al modelo: {e}"}

    # ============================
    # 4. Leer clasificación EI
    # ============================
    classification = result["result"]["classification"]

    prob_fire = float(classification.get("fire", 0))
    prob_flame = float(classification.get("flame", 0))
    prob_smoke = float(classification.get("smoke-gas", 0))
    prob_normal = float(classification.get("normal", 0))

    # ============================
    # 5. Lógica personalizada de riesgo
    # ============================
    # Riesgo basado en cualquier condición peligrosa
    probabilidad_score = max(prob_fire + prob_flame + prob_smoke)

    if probabilidad_score < 0.20:
        estado = "Seguro"
        if prob_smoke < 0.10 or prob_flame < 0.10 or prob_fire < 0.10 or prob_normal >= 0.80:
            desc = "Condiciones normales detectadas."
        elif prob_smoke < 0.25:
            desc = "se detectaron fluctuaciones en el aire, monitoree la situación."
        else:
            desc = "calculando condiciones seguras, se recomienda vigilancia continua."

    elif probabilidad_score < 0.60:
        estado= "Alerta"
        if prob_smoke >= 0.35:
            desc = "Niveles elevados de humo detectados, verifique las alertas de temperatura y llama"
        else:
            desc = "Condiciones inestables detectadas, manténgase alerta y monitoree los sensores."

    else:
        estado = "Crítico"
        if prob_fire >= 0.40 :
            desc = "Alto riesgo de incendio detectado"
        elif prob_smoke >= 0.60:
            desc = "Niveles críticos de humo detectados, posible incendio en curso"
        elif prob_flame >= 0.40 and prob_smoke >= 0.40:
            desc = "Llama y humo detectados, riesgo inminente de incendio"
        else:
            desc = "Condiciones peligrosas detectadas, acción inmediata requerida"
    # ============================
    # 6. Respuesta limpia
    # ============================
    return {
        "esp32": esp_id,
        "temperatura": temperatura,
        "humo": humo,
        "llama": llama,
        "probs": {
            "fire": prob_fire,
            "flame": prob_flame,
            "smoke-gas": prob_smoke,
            "normal": prob_normal
        },
        "estado": estado,
        "descripcion": desc,    
        "riesgo_incendio": round(prob_fire * 100, 2)  # %
    }
