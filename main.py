import os
from fastapi import FastAPI
from app.routers import risk_router, telemetry_router
from dotenv import load_dotenv
from app.services.mqtt_service import iniciar_servicio_mqtt
from app.services.thingsboard_service import iniciar_conexion_tb
import threading




load_dotenv()
app = FastAPI(title="Fire Monitoring System")

# Inicializar ThingsBoard
threading.Thread(target=iniciar_conexion_tb, daemon=True).start()

# Inicializar MQTT para recibir ESP
threading.Thread(target=iniciar_servicio_mqtt, daemon=True).start()
