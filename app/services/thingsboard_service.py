import json
import paho.mqtt.client as mqtt

# Tokens únicos por dispositivo ThingsBoard
DEVICE_TOKENS = {
    "esp32_1": "w36qq4h9d6t65e3y58z1",
    "esp32_2": "BuGSMZgbwS5ykcJWtGQB"
}

TB_HOST = "dashfiremonitorsys.app"
TB_PORT = 1883   # MQTT sin TLS (el que usa tu server)

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

        client.disconnect()

        print(f"[ThingsBoard] Telemetría enviada a {esp_id}[token: {token}]: {payload}")

    except Exception as e:
        print(f"[ThingsBoard] Error enviando telemetría: {e}")
