import joblib
from pathlib import Path

# Carpeta donde se guardan todos tus modelos
MODELOS_PATH = Path("modelos")

# Diccionarios para almacenar modelos y escaladores cargados en memoria
modelos = {}
scalers = {}


def cargar_modelos():
    """
    Carga los modelos y escaladores de esp32_1 y esp32_2 en memoria.
    Debes tener en /modelos:
        modelo_esp32_1.pkl
        modelo_esp32_2.pkl
        scaler_esp32_1.pkl
        scaler_esp32_2.pkl
    """
    dispositivos = ["esp32_1", "esp32_2"]

    for disp in dispositivos:
        modelo_file = MODELOS_PATH / f"modelo_{disp}.pkl"
        scaler_file = MODELOS_PATH / f"scaler_{disp}.pkl"

        if not modelo_file.exists():
            raise FileNotFoundError(f"No se encontró: {modelo_file}")
        if not scaler_file.exists():
            raise FileNotFoundError(f"No se encontró: {scaler_file}")

        print(f"Cargando modelo → {modelo_file}")
        print(f"Cargando scaler → {scaler_file}")

        modelos[disp] = joblib.load(modelo_file)
        scalers[disp] = joblib.load(scaler_file)

    print("✔ Todos los modelos y escaladores se cargaron correctamente.")


def get_modelo_y_scaler(esp_id: str):
    """
    Devuelve el modelo y el scaler para esp32_1 o esp32_2.
    """
    if esp_id not in modelos:
        raise ValueError(f"esp_id inválido: {esp_id}. Debe ser esp32_1 o esp32_2.")
    return modelos[esp_id], scalers[esp_id]
