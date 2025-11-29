import json
import threading
import paho.mqtt.client as paho
from paho import mqtt
from app.utils.predictor import process_message
from app.services.thingsboard_service import enviar_a_thingsboard
from app.models.AI_model import cargar_modelos


MQTT_HOST = "v21e7d52.ala.us-east-1.emqxsl.com"
MQTT_PORT = 8883
MQTT_USER = "firemonitorsysclust"
MQTT_PASSWORD = "IoT8PROJECT"

TOPICS = [
    ("incendios/esp32_1/data", 1),
    ("incendios/esp32_2/data", 1)
]

client = paho.Client(client_id="api_server_listener", userdata=None, protocol=paho.MQTTv5)

def on_connect(client, userdata, flags, rc, properties=None):
    print("Conectado a HiveMQ Cloud con código:", rc)
    for topic, qos in TOPICS:
        client.subscribe(topic, qos=qos)
        print("Suscrito a:", topic)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        esp_id = msg.topic.split("/")[1]

        print(f"\n📥 Mensaje recibido de {esp_id}: {payload}")

        resultado = process_message(esp_id, payload)
        enviar_a_thingsboard(esp_id, resultado)

        print(f"📊 Resultado modelo ({esp_id}): {resultado}")

    except Exception as e:
        print("⚠️ Error procesando mensaje:", e)


def init_mqtt():
    """Arranca el cliente MQTT en segundo plano sin bloquear FastAPI."""
    cargar_modelos()

    client.on_connect = on_connect
    client.on_message = on_message

    client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)

    client.connect(MQTT_HOST, MQTT_PORT)

    # ---- LOOP en un hilo ----
    thread = threading.Thread(target=client.loop_forever)
    thread.daemon = True
    thread.start()

    print("✔ MQTT corriendo en background")
