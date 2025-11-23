# app/model.py
import os
import joblib
from pathlib import Path

MODEL_PATH = os.getenv("MODEL_PATH", "modelo_incendios.pkl")

def load_model(path=None):
    p = path or MODEL_PATH
    p = Path(p)
    if not p.exists():
        raise FileNotFoundError(f"Modelo no encontrado en {p}")
    return joblib.load(str(p))

MODEL = load_model()