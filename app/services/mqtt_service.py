import os
import json
import time
import random
import threading
import logging
from paho.mqtt import client as mqtt_client
from paho import mqtt
from app.utils.predictor import process_message
from app.services.thingsboard_service import enviar_a_thingsboard

# ===== Logging DEBUG =====
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MQTTService")

# ===== Configuración desde variables de entorno =====
MQTT_HOST = os.getenv("MQTT_HOST")
MQTT_PORT = int(os.getenv("MQTT_PORT", 8883))  # TLS serverless por defecto
MQTT_USER = os.getenv("MQTT_USER")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
CA_CERT = os.getenv("MQTT_CA_CERT", "emqxsl-ca.crt")  # Ruta al certificado EMQX

TOPICS = [
    ("incendios/esp32_1/data", 1),
    ("incendios/esp32_2/data", 1)
]

INACTIVITY_TIMEOUT = 60  # segundos

# ===== Estado global =====
last_message_time = time.time()
is_connected = False

# ===== Generar client_id único =====
client_id = f"api_server_listener_{random.randint(0,1000)}"
client = mqtt_client.Client(client_id=client_id, userdata=None, protocol=mqtt_client.MQTTv5)

# ===== Callbacks =====
def reconnect_if_needed():
    global client, is_connected
    if not is_connected:
        try:
            client.reconnect()
            logger.info("Reconexión MQTT bajo demanda exitosa.")
        except Exception as e:
            logger.warning(f"Fallo de reconexión bajo demanda: {e}")

def on_connect(client, userdata, flags, rc, properties=None):
    global is_connected
    if rc == 0:
        is_connected = True
        logger.info(f"Conectado a EMQX Cloud (rc={rc})")
        for topic, qos in TOPICS:
            client.subscribe(topic, qos=qos)
            logger.info(f"Suscrito a topic: {topic}")
    else:
        logger.error(f"Error al conectar, rc={rc}")

def on_disconnect(client, userdata, rc, properties=None):
    global is_connected
    is_connected = False
    logger.warning(f"Desconectado del broker (rc={rc})")
    if rc != 0:
        logger.info("Intentando reconectar automáticamente...")

def on_message(client, userdata, msg):
    global last_message_time
    last_message_time = time.time()

    reconnect_if_needed()
    try:
        payload = json.loads(msg.payload.decode())
        esp_id = msg.topic.split("/")[1]
        logger.info(f"Mensaje recibido de {esp_id}: {payload}")

        resultado = process_message(esp_id, payload)
        time.sleep(3)  # Pequeña pausa para evitar sobrecarga
        exito = enviar_a_thingsboard(esp_id, resultado)

        if exito:
            logger.info(f"Telemetría enviada a ThingsBoard para {esp_id}")
            logger.info(f"Resultado modelo enviado a TB: ({esp_id}): {resultado}")
        else:
            logger.error(f"Error enviando telemetría a ThingsBoard para {esp_id}")

        

    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        logger.error(f"Error decodificando mensaje: {msg.payload} - {e}")
    except Exception as e:
        logger.exception(f"Error procesando mensaje: {e} - Topic: {msg.topic} QoS: {msg.qos}")

# ===== Inicialización MQTT =====
def init_mqtt():
    global client, last_message_time, is_connected

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    # Configuración TLS y autenticación
    client.tls_set(ca_certs=CA_CERT, tls_version=mqtt_client.ssl.PROTOCOL_TLS)
    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)

    # Reconexión automática con backoff
    client.reconnect_delay_set(min_delay=1, max_delay=30)

    try:
        client.connect(MQTT_HOST, MQTT_PORT)
        client.loop_start()
        logger.info("✔ MQTT cliente iniciado en background")
    except Exception as e:
        logger.exception(f"✗ Error iniciando MQTT: {e}")
        return

