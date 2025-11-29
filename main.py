import os
import threading
from fastapi import FastAPI
from dotenv import load_dotenv

from app.services.mqtt_service import init_mqtt
from app.services.thingsboard_service import iniciar_conexion_tb

load_dotenv()

app = FastAPI(title="Fire Monitoring System")

@app.get("/")
def root():
    return {"message": "Fire Monitoring System API is running."}

@app.on_event("startup")
async def startup_event():

    # MQTT en segundo plano
    threading.Thread(target=init_mqtt, daemon=True).start()


