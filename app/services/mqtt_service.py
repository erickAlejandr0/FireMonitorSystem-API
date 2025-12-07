import json
import threading
import paho.mqtt.client as paho
from paho import mqtt
from app.utils.predictor import process_message
from app.services.thingsboard_service import enviar_a_thingsboard
import os
import time


MQTT_HOST = os.getenv("MQTT_HOST")
MQTT_PORT = int(os.getenv("MQTT_PORT"))
MQTT_USER = os.getenv("MQTT_USER")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")

TOPICS = [
    ("incendios/esp32_1/data", 1),
    ("incendios/esp32_2/data", 1)
]
INACTIVITY_TIMEOUT = 60
last_message_time = time.time()
is_connected = False   

client = paho.Client(client_id="api_server_listener", userdata=None, protocol=paho.MQTTv5)

def on_connect(client, userdata, flags, rc, properties=None):
    global is_connected
    is_connected = True
    print("Conectado a EMXQ Cloud con código:", rc)
    for topic, qos in TOPICS:
        client.subscribe(topic, qos=qos)
        print("Suscrito a:", topic)

def on_disconnect(client, userdata, rc, properties=None):
    global is_connected
    is_connected = False
    print("Desconectado del broker (rc:", rc, ")")

    # Si se desconectó por error, activar reconexión automática del loop
    if rc != 0:
        print("Intentando reconectar automáticamente…")


def on_message(client, userdata, msg):
    global last_message_time
    last_message_time = time.time()
    try:

        try:

            payload = json.loads(msg.payload.decode())
            esp_id = msg.topic.split("/")[1]
        except json.JSONDecodeError as e:
            print(f" Error decodificando JSON del mensaje recibido: {msg.payload}")
            print(f" Detalles del error: {e}")
            return
        
        print(f"\n Mensaje recibido de {esp_id}: {payload}")

        resultado = process_message(esp_id, payload)
        exito = enviar_a_thingsboard(esp_id, resultado)

        if exito:
            print(f" Telemetría enviada a ThingsBoard desde mqtt service para {esp_id}")
        else:
            print(f" Error enviando telemetría a ThingsBoard desde mqtt service para {esp_id}")

        print(f" Resultado modelo ({esp_id}): {resultado}")
    except UnicodeDecodeError:
        print(f" Error decodificando el mensaje recibido: {msg.payload}")
    except Exception as e:
        print(" Error procesando mensaje:", e)
        print(" Mensaje original:", msg.payload)
        print(f" Topic: {msg.topic} QoS: {msg.qos}")


def init_mqtt():
    """Arranca el cliente MQTT en segundo plano sin bloquear FastAPI."""

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)

    client.reconnect_delay_set(min_delay=1, max_delay=30)

    try:
        client.connect(MQTT_HOST, MQTT_PORT)
        client.loop_start()
        print("✔ MQTT cliente iniciado en background")
    except Exception as e:
        print(f"✗ Error iniciando MQTT: {e}")
        return


    print("✔ MQTT corriendo en background")

      # Monitor de inactividad
    def inactivity_monitor():
        global last_message_time, is_connected
        while True:
            time.sleep(INACTIVITY_TIMEOUT / 2)  # Verificar cada 30s


            time_elapsed = time.time() - last_message_time
            if time_elapsed > INACTIVITY_TIMEOUT:
                print(f"No se recibieron mensajes en {INACTIVITY_TIMEOUT} segundos. Desconectando MQTT.")
                client.disconnect()
                is_connected = False
            
            print("[MQTT] Intentando reconectar…")
            while not is_connected:
                try:
                    client.reconnect()
                    print("[MQTT] Reconexión exitosa.")
                    break
                except Exception as e:
                    print(f"[MQTT] Fallo de reconexión: {e}. Reintentando en 5s...")
                    time.sleep(5)
                

    monitor_thread = threading.Thread(target=inactivity_monitor, daemon=True)
    monitor_thread.start()