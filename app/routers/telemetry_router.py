from fastapi import APIRouter
from app.models.telemetria_model import Telemetria

router = APIRouter(prefix="/telemetria", tags=["telemetria"])

@router.post("/telemetria")
def recibir_telemetria(data: Telemetria):
    print("📥 Telemetría recibida:")
    print(f"Temperatura: {data.temperatura} °C")


    return {"status": "ok", "msg": "Datos recibidos correctamente"}