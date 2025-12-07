import json
import requests
import os
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ===== Configuración HTTP =====
TB_HOST = os.getenv("TB_HOST")
TB_PORT = os.getenv("TB_PORT")

DEVICE_TOKENS = {
    "esp32_1": os.getenv("ESP32_1_TOKEN"), 
    "esp32_2": os.getenv("ESP32_2_TOKEN")
}

# Validaciones
if not TB_HOST:
    raise ValueError("TB_HOST no configurado en .env")

if not TB_PORT:
    raise ValueError("TB_PORT no configurado en .env")

if not all(DEVICE_TOKENS.values()):
    raise ValueError("Faltan tokens ESP32_1_TOKEN o ESP32_2_TOKEN en .env")

# Construir URL base
TB_HTTP_URL = f"http://{TB_HOST}:{TB_PORT}/api/v1"

print(f"[ThingsBoard] URL configurada: {TB_HTTP_URL}")


def crear_sesion_con_reintentos():
    """
    Crea una sesión HTTP con reintentos automáticos.
    """
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


def enviar_a_thingsboard(esp_id: str, datos: dict) -> bool:
    """
    Envía telemetría a ThingsBoard vía HTTP REST API.
    
    Endpoint: POST /api/v1/{token}/telemetry
    
    Args:
        esp_id: Identificador del ESP32 ("esp32_1" o "esp32_2")
        datos: Diccionario con los datos a enviar
    
    Returns:
        bool: True si se envió exitosamente, False si hubo error
    """
    
    # ===== 1. Validar ESP ID =====
    if esp_id not in DEVICE_TOKENS:
        print(f"❌ [ThingsBoard] ESP ID no reconocido: {esp_id}")
        return False

    token = DEVICE_TOKENS[esp_id]
    url = f"{TB_HTTP_URL}/{token}/telemetry"

    try:
        # ===== 2. Preparar payload de telemetría =====
        payload = {
         
            "temperatura": datos.get("temperatura"),
            "humo": datos.get("humo"),
            "llama": datos.get("llama"),
            "estado": datos.get("estado"),
            "descripcion": datos.get("descripcion"),
            "riesgo_incendio": datos.get("riesgo_incendio"),
            "probs_fire": datos.get("probs", {}).get("fire"),
            "probs_flame": datos.get("probs", {}).get("flame"),
            "probs_smoke": datos.get("probs", {}).get("smoke-gas"),
            "probs_normal": datos.get("probs", {}).get("normal"),
        }

        # ===== 3. Enviar solicitud HTTP con reintentos =====
        sesion = crear_sesion_con_reintentos()
        
        response = sesion.post(
            url,
            json=payload,
            timeout=5,
            headers={"Content-Type": "application/json"}
        )

        # ===== 4. Validar respuesta =====
        response.raise_for_status()
        
        print(f"✔ [ThingsBoard] Telemetría enviada exitosamente para {esp_id}")
        print(f"   → URL: {url}")
        print(f"   → Payload: {json.dumps(payload, indent=2)}")
        
        return True

    except requests.exceptions.ConnectionError as e:
        print(f"ThingsBoard] Error de conexión a {TB_HTTP_URL}")
        print(f"   → Verifica que ThingsBoard esté corriendo en {TB_HOST}:{TB_PORT}")
        print(f"   → Detalles: {e}")
        return False
        
    except requests.exceptions.Timeout:
        print(f"[ThingsBoard] Timeout: ThingsBoard tardó más de 5 segundos en responder")
        print(f"   → Endpoint: {url}")
        return False
        
    except requests.exceptions.HTTPError as e:
        status_code = response.status_code
        response_text = response.text
        
        if status_code == 401:
            print(f"[ThingsBoard] Error 401 (No autorizado): Token inválido para {esp_id}")
        elif status_code == 404:
            print(f"[ThingsBoard] Error 404 (No encontrado): Verifica el token y la URL")
        else:
            print(f"[ThingsBoard] Error HTTP {status_code}: {e}")
        
        print(f"   → Respuesta del servidor: {response_text}")
        return False
        
    except Exception as e:
        print(f"[ThingsBoard] Error inesperado al enviar telemetría: {e}")
        import traceback
        traceback.print_exc()
        return False
