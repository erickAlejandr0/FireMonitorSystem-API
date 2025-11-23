from pydantic import BaseModel

class Telemetria(BaseModel):
    temperatura: float
    humo: float
    tamaño: float = 100.0
    zona: str = "Desconocida"

class ResultadoRiesgo(BaseModel):
    zona: str
    riesgo: str
    probabilidad: float