import requests
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def sincronizar_cliente_supabase(nombre, email, telefono, consulta, estado="pendiente"):
    try:
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/clientes",
            headers=HEADERS,
            json={
                "nombre": nombre,
                "email": email,
                "telefono": telefono,
                "consulta": consulta,
                "estado": estado
            }
        )
        if response.status_code in [200, 201]:
            return f"Cliente {nombre} sincronizado en Supabase!"
        return f"Error Supabase: {response.text}"
    except Exception as e:
        return f"Error al sincronizar: {str(e)}"

def actualizar_estado_supabase(nombre, estado):
    try:
        response = requests.patch(
            f"{SUPABASE_URL}/rest/v1/clientes?nombre=eq.{nombre}",
            headers=HEADERS,
            json={"estado": estado}
        )
        if response.status_code in [200, 204]:
            return f"Estado de {nombre} actualizado a '{estado}' en Supabase!"
        return f"Error Supabase: {response.text}"
    except Exception as e:
        return f"Error al actualizar: {str(e)}"

def listar_supabase():
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/clientes?select=*",
            headers=HEADERS
        )
        if response.status_code == 200:
            datos = response.json()
            if not datos:
                return "No hay clientes en Supabase"
            respuesta = []
            for r in datos:
                respuesta.append(f"ID:{r['id']} | {r['nombre']} | {r['email']} | {r['telefono']} | Estado:{r['estado']}")
            return "\n".join(respuesta)
        return f"Error Supabase: {response.text}"
    except Exception as e:
        return f"Error al listar: {str(e)}"