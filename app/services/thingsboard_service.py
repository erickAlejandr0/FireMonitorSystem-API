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

if not TB_HOST or not TB_PORT:
    raise ValueError("TB_HOST o TB_PORT no están configurados en las variables de entorno.")

if not all(DEVICE_TOKENS.values()):
    raise ValueError("Faltan tokens de dispositivos en las variables de entorno.")  

def enviar_a_thingsboard(esp_id: str, datos: dict):
    """
    Envía telemetría a un dispositivo específico en ThingsBoard según el ESP32.
    """

    if esp_id not in DEVICE_TOKENS:
        print(f"[ThingsBoard] ESP ID no reconocido: {esp_id}")
        return

    token = DEVICE_TOKENS[esp_id]

    # Crear un cliente MQTT para ese dispositivo
    client = mqtt.Client(client_id=f"api_{esp_id}",protocol=mqtt.MQTTv311)

    is_connected = False
    published_success = False
    # Autenticación ThingsBoard = token como usuario
    #client.username_pw_set(token)

    def on_connect(client, userdata, flags, rc):
        nonlocal is_connected
        if rc == 0:
            is_connected = True
            print(f"[ThingsBoard] Conectado al ThingsBoard como {esp_id} (rc={rc})")
        else:
            print(f"[ThingsBoard] Falló la conexión a ThingsBoard (rc={rc})")

    def on_disconnect(client, userdata, rc):
        nonlocal is_connected
        is_connected = False
        print(f"[ThingsBoard] Desconectado de ThingsBoard (rc={rc})")
        if rc != 0:
            print("[Thingsboard] desconexion inesperada")
    
    def on_publish(client, userdata, mid):
        nonlocal published_success
        published_success = True
        print(f"[ThingsBoard] Mensaje publicado con en: {esp_id}")

    def on_disconect_final(client, userdata, rc):
        if rc == 0:
            print(f"[ThingsBoard] Desconectado finalmente de ThingsBoard como {esp_id}")


    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_publish = on_publish


    try:
        client.connect(TB_HOST, TB_PORT, keepalive=60)
        client.loop_start()

        timeout = time.time() + 5  # segundos
        while not is_connected and time.time() < timeout:
            time.sleep(0.1)
        
        if not is_connected:
            print(f"[ThingsBoard] No se pudo conectar a ThingsBoard en el tiempo esperado para {esp_id}.")
            client.loop_stop()
            return
        
        payload = json.dumps(datos)

        result = client.publish("v1/devices/me/telemetry", payload, qos=1)

        if published_success:
            print(f"[ThingsBoard] Telemetría publicada exitosamente para {esp_id}.")
            return True
        else:
            print(f"[ThingsBoard] Falló la publicación de telemetría para {esp_id}.")
            return False
        
    except ConnectionRefusedError:
        print(f"[ThingsBoard] Conexión rechazada al ThingsBoard para {esp_id}. Verifica el token y la conectividad.{TB_HOST}:{TB_PORT}")
    except TimeoutError:
        print(f"[ThingsBoard] Tiempo de espera agotado al conectar con ThingsBoard para {TB_HOST}:{TB_PORT} ")
    except Exception as e:
        print("error enviando telemetria [Thingsboard]")
        return False
    finally:
        try:
            client.loop_stop()
            client.on_disconnect = on_disconect_final
            client.disconnect()
        except Exception as e:
            print(f"[ThingsBoard] Error en la desconexión final: {e}")
