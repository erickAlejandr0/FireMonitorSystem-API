from app.models.telemetria_model import Telemetria, ResultadoRiesgo
from fastapi import APIRouter, HTTPException 
from app.models.AI_model import MODEL
import numpy as np
import pandas as pd
from app.utils.telegram_util import enviar_telegram

router = APIRouter(prefix="/IAmodel", tags=["IAmodel"])

@router.post("/evaluar_riesgo/", response_model=ResultadoRiesgo)
def evaluar_riesgo(payload: Telemetria):
    # preparar entrada con nombres de columnas
    entrada = pd.DataFrame([[payload.temperatura, payload.humo, payload.tamaño]],
                           columns=["temperatura", "humo", "tamaño"])
    try:
        pred = MODEL.predict(entrada)[0]
        proba_arr = MODEL.predict_proba(entrada)
        # probabilidad de la clase 'Crítico'
        if "Crítico" in MODEL.classes_:
            proba_idx = list(MODEL.classes_).index("Crítico")
            proba = float(proba_arr[0][proba_idx])
        else:
            proba = float(np.max(proba_arr))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    resultado = {
        "zona": payload.zona,
        "riesgo": str(pred),
        "probabilidad": round(proba*100, 2)
    }

    # enviar alerta si riesgo alto
    if proba > 0.7:
        mensaje = (f"*ALERTA CRÍTICA*\nZona: {payload.zona}\n"
                   f"Probabilidad de incendio: {round(proba*100,2)}%\n"
                   f"Temp actual: {payload.temperatura}°C  Humo: {payload.humo} ")
        enviar_telegram(mensaje)

    return resultado
