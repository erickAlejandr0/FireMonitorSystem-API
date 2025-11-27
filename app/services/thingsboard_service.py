import requests
import json

TB_URL_BRIDGE = "http://dashfiremonitorsys.app:8080/api/v1/AAQSR7PyNwaV6zUYhZIW/telemetry"
TB_URL_DEVICE = "http://dashfiremonitorsys.app:8080/api/v1/w36qq4h9d6t65e3y58z1/telemetry"

def enviar_a_thingsboard(datos: dict):
    try:
        requests.post(
            TB_URL_BRIDGE,
            headers={"Content-Type": "application/json"},
            data=json.dumps(datos)
        )
    except Exception as e:
        print(f"Error enviando telemetría a ThingsBoard: {e}")


def datos_esp_thingsboard(datos: dict):
    try:
        requests.post(
            TB_URL_DEVICE,
            headers={"Content-Type": "application/json"},
            data=json.dumps(datos)
        )
    except Exception as e:
        print(f"Error enviando datos de telemetría hacia ThingsBoard: {e}")
        
