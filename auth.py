import requests
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Content-Type": "application/json"
}

def registrar_usuario(email, password):
    try:
        response = requests.post(
            f"{SUPABASE_URL}/auth/v1/signup",
            headers=HEADERS,
            json={"email": email, "password": password}
        )
        data = response.json()
        if response.status_code == 200 and data.get("id"):
            return {"ok": True, "user_id": data["id"], "mensaje": f"✅ Usuario {email} registrado correctamente!"}
        return {"ok": False, "mensaje": f"❌ Error al registrar: {data.get('msg', 'Error desconocido')}"}
    except Exception as e:
        return {"ok": False, "mensaje": f"Error: {str(e)}"}

def login_usuario(email, password):
    try:
        response = requests.post(
            f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
            headers=HEADERS,
            json={"email": email, "password": password}
        )
        data = response.json()
        if response.status_code == 200 and data.get("access_token"):
            return {
                "ok": True,
                "user_id": data["user"]["id"],
                "token": data["access_token"],
                "mensaje": f"✅ Bienvenido {email}!"
            }
        return {"ok": False, "mensaje": "❌ Email o contraseña incorrectos"}
    except Exception as e:
        return {"ok": False, "mensaje": f"Error: {str(e)}"}