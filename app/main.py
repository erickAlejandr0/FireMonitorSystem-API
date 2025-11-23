import os
from fastapi import FastAPI
from app.routers import risk_router, telemetry_router
from dotenv import load_dotenv
from app.models.AI_model import load_model



load_dotenv()
app = FastAPI(title="Fire Monitoring System")
app.include_router(risk_router.router)
app.include_router(telemetry_router.router)

