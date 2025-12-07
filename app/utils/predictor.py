# app/predictor.py

import requests
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

MODEL_URL = os.getenv("MODEL_URL") # Nombre del contenedor Edge Impulse
if not MODEL_URL:
    raise ValueError("MODEL_URL no está configurado en las variables de entorno.")

def crear_sesion_con_reintentos():
    sesion = requests.Session()
    reintentos = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504]
    )
    adaptador = HTTPAdapter(max_retries=reintentos)
    sesion.mount("http://", adaptador)
    sesion.mount("https://", adaptador)
    return sesion


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
        sesion= crear_sesion_con_reintentos()
        response = sesion.post(MODEL_URL, json={"features": features}, timeout=5, headers={"Content-Type": "application/json"})
        result = response.json()
    except Exception as e:
        return {"error": f"No se pudo conectar al modelo: {e}"}
    except requests.exceptions.Timeout:
        return {"error": "Tiempo de espera agotado al conectar con el modelo."} 
    except requests.exceptions.ConnectionError:
        return {"error": f"Error de conexión al intentar contactar el modelo.{MODEL_URL}"}
    except requests.exceptions.HTTPError as e:
        return {"error": f"Error HTTP {response.status_code} al llamar al modelo: {e}"}

    # ============================
    # 4. Leer clasificación EI
    # ============================
    try:
    
        classification = result["result"]["classification"]
    except KeyError:
        return {"error": f"Respuesta del modelo no tiene el formato esperado.{result}"}
    
    prob_fire = float(classification.get("fire", 0))
    prob_flame = float(classification.get("flame", 0))
    prob_smoke = float(classification.get("smoke-gas", 0))
    prob_normal = float(classification.get("normal", 0))

    # ============================
    # 5. Lógica personalizada de riesgo
    # ============================
    # Riesgo basado en cualquier condición peligrosa
    probabilidad_score = max(prob_fire, prob_flame, prob_smoke)

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
