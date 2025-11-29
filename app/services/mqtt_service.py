import json
import time
import paho.mqtt.client as paho
from paho import mqtt
from app.utils.predictor import process_message
from app.services.thingsboard_service import enviar_a_thingsboard
from app.models.AI_model import cargar_modelos



MQTT_HOST = "f57dc7cc97d9435093073870cc206dff.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_USER = "firemonitorsysclust"
MQTT_PASSWORD = "IoT8PROJECT"

TOPICS = [
    ("incendios/esp32_1/data", 1),
    ("incendios/esp32_2/data", 1)
]

cargar_modelos()

def on_connect(client, userdata, flags, rc, properties=None):
    print("Conectado a HiveMQ Cloud con código:", rc)
    for topic, qos in TOPICS:
        client.subscribe(topic, qos=qos)
        print("Suscrito a:", topic)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        esp_id = msg.topic.split("/")[1]  # esp32_1 o esp32_2

        print(f"\n📥 Mensaje recibido de {esp_id}: {payload}")

        resultado = process_message(esp_id, payload)
        
        enviar_a_thingsboard(esp_id,resultado)
        print(f"📊 Resultado del modelo ({esp_id}): {resultado}")

    except Exception as e:
        print("Error procesando mensaje:", e)

def on_publish(client, userdata, mid, properties=None):
    print("Publicado mid:", mid)

def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print("Suscripción confirmada:", granted_qos)

# Configurar cliente
client = paho.Client(client_id="", userdata=None, protocol=paho.MQTTv5)

client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish
client.on_subscribe = on_subscribe

# --- CONEXIÓN SEGURA TLS ---
client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)

# --- CREDENCIALES MQTT ---
client.username_pw_set(MQTT_USER, MQTT_PASSWORD)

# --- CONECTAR AL BROKER ---
client.connect(MQTT_HOST, MQTT_PORT)

# --- LOOP PERMANENTE ---
client.loop_forever()
