import json
import paho.mqtt.client as mqtt
import time
import os

# Tokens únicos por dispositivo ThingsBoard
DEVICE_TOKENS = {
    "esp32_1": os.getenv("ESP32_1_TOKEN"), 
    "esp32_2": os.getenv("ESP32_2_TOKEN")
}

TB_HOST = os.getenv("TB_HOST")  # Nombre del servidor ThingsBoard
TB_PORT = int(os.getenv("TB_PORT"))  # MQTT 

def enviar_a_thingsboard(esp_id: str, datos: dict):
    """
    Envía telemetría a un dispositivo específico en ThingsBoard según el ESP32.
    """

    if esp_id not in DEVICE_TOKENS:
        print(f"[ThingsBoard] ESP ID no reconocido: {esp_id}")
        return

    token = DEVICE_TOKENS[esp_id]

    # Crear un cliente MQTT para ese dispositivo
    client = mqtt.Client(protocol=mqtt.MQTTv311)

    # Autenticación ThingsBoard = token como usuario
    client.username_pw_set(token)
    

    try:
        client.connect(TB_HOST, TB_PORT, 60)

        payload = json.dumps(datos)

        client.publish("v1/devices/me/telemetry", payload, qos=1)

        time.sleep(0.5)  # Esperar a que se envíe todo

        client.loop_stop()

        client.disconnect()
        print(f"[ThingsBoard] Telemetría enviada a {esp_id}[token: {token}]: {payload}")

    except Exception as e:
        print(f"[ThingsBoard] Error enviando telemetría: {e}")
