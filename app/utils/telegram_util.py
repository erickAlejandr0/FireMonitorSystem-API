# app/telegram_utils.py
import os
import requests



def enviar_telegram(mensaje: str):

    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("No se encontraron TELEGRAM_TOKEN o TELEGRAM_CHAT_ID en las variables de entorno.")
        
        return False
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": mensaje, "parse_mode":"Markdown"}
    try:
        r = requests.post(url, json=payload, timeout=5)
        return r.ok
    except Exception as e:
        print("Error al enviar mensaje a Telegram: " + e)
        return False
