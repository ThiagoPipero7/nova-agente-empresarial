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

ESTADOS_EMOJI = {
    "pendiente": "🔵 Pendiente",
    "activo": "🟢 Activo",
    "resuelto": "✅ Resuelto"
}

def formatear_cliente(r):
    estado = ESTADOS_EMOJI.get(r['estado'], r['estado'])
    return (
        f"👤 {r['nombre']}\n"
        f"   📧 {r['email']}\n"
        f"   📱 {r['telefono']}\n"
        f"   📋 {r['consulta']}\n"
        f"   {estado}\n"
    )

def buscar_cliente(nombre):
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/clientes?nombre=ilike.%{nombre}%&select=*",
            headers=HEADERS
        )
        if response.status_code == 200:
            datos = response.json()
            if not datos:
                return "No encontré ningún cliente con ese nombre"
            return "\n".join([formatear_cliente(r) for r in datos])
        return f"Error: {response.text}"
    except Exception as e:
        return f"Error al buscar cliente: {str(e)}"

def agregar_cliente(nombre, email, telefono, consulta):
    try:
        # Validación de email
        if "@" not in email or "." not in email.split("@")[-1]:
            return "❌ El email no es válido. Por favor ingresá un email correcto (ej: nombre@empresa.com)"

        # Validación de teléfono
        if not telefono.isdigit() or len(telefono) < 8:
            return "❌ El teléfono no es válido. Debe tener al menos 8 dígitos numéricos"

        # Validación de nombre
        if len(nombre.strip()) < 3:
            return "❌ El nombre debe tener al menos 3 caracteres"

        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/clientes",
            headers=HEADERS,
            json={
                "nombre": nombre,
                "email": email,
                "telefono": telefono,
                "consulta": consulta,
                "estado": "pendiente"
            }
        )
        if response.status_code in [200, 201]:
            return f"✅ Cliente {nombre} agregado correctamente!"
        return f"Error: {response.text}"
    except Exception as e:
        return f"Error al agregar cliente: {str(e)}"

def listar_clientes():
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/clientes?select=*",
            headers=HEADERS
        )
        if response.status_code == 200:
            datos = response.json()
            if not datos:
                return "No hay clientes registrados. ¿Querés agregar uno nuevo?"
            return "\n".join([formatear_cliente(r) for r in datos])
        return f"Error: {response.text}"
    except Exception as e:
        return f"Error al listar clientes: {str(e)}"

def actualizar_cliente(id, campo, valor):
    try:
        campos_permitidos = ["nombre", "email", "telefono", "consulta", "estado"]
        if campo not in campos_permitidos:
            return f"Campo no válido. Campos permitidos: {', '.join(campos_permitidos)}"
        response = requests.patch(
            f"{SUPABASE_URL}/rest/v1/clientes?id=eq.{id}",
            headers=HEADERS,
            json={campo: valor}
        )
        if response.status_code in [200, 204]:
            return f"✅ Cliente ID {id} actualizado: {campo} = {valor}"
        return f"Error: {response.text}"
    except Exception as e:
        return f"Error al actualizar cliente: {str(e)}"

def eliminar_cliente(id):
    try:
        response = requests.delete(
            f"{SUPABASE_URL}/rest/v1/clientes?id=eq.{id}",
            headers=HEADERS
        )
        if response.status_code in [200, 204]:
            return f"✅ Cliente ID {id} eliminado correctamente"
        return f"Error: {response.text}"
    except Exception as e:
        return f"Error al eliminar cliente: {str(e)}"

def listar_por_estado(estado):
    try:
        estados_validos = ["pendiente", "activo", "resuelto"]
        if estado not in estados_validos:
            return f"Estado no válido. Estados permitidos: {', '.join(estados_validos)}"
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/clientes?estado=eq.{estado}&select=*",
            headers=HEADERS
        )
        if response.status_code == 200:
            datos = response.json()
            if not datos:
                return f"No hay clientes con estado '{estado}'. ¿Querés agregar uno nuevo?"
            return "\n".join([formatear_cliente(r) for r in datos])
        return f"Error: {response.text}"
    except Exception as e:
        return f"Error al listar por estado: {str(e)}"


DEFINICIONES = [
    {
        "type": "function",
        "function": {
            "name": "buscar_cliente",
            "description": "Busca un cliente en la base de datos por nombre",
            "parameters": {
                "type": "object",
                "properties": {
                    "nombre": {"type": "string", "description": "Nombre del cliente a buscar"}
                },
                "required": ["nombre"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "agregar_cliente",
            "description": "Agrega un nuevo cliente a la base de datos",
            "parameters": {
                "type": "object",
                "properties": {
                    "nombre": {"type": "string", "description": "Nombre del cliente"},
                    "email": {"type": "string", "description": "Email del cliente"},
                    "telefono": {"type": "string", "description": "Teléfono del cliente"},
                    "consulta": {"type": "string", "description": "Consulta o motivo de contacto"}
                },
                "required": ["nombre", "email", "telefono", "consulta"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "listar_clientes",
            "description": "Lista todos los clientes de la base de datos",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "actualizar_cliente",
            "description": "Actualiza un campo de un cliente existente por su ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "description": "ID del cliente"},
                    "campo": {"type": "string", "description": "Campo a actualizar: nombre, email, telefono, consulta o estado"},
                    "valor": {"type": "string", "description": "Nuevo valor para el campo"}
                },
                "required": ["id", "campo", "valor"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "eliminar_cliente",
            "description": "Elimina un cliente de la base de datos por su ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "description": "ID del cliente a eliminar"}
                },
                "required": ["id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "listar_por_estado",
            "description": "Lista clientes filtrados por estado: pendiente, activo o resuelto",
            "parameters": {
                "type": "object",
                "properties": {
                    "estado": {"type": "string", "description": "Estado a filtrar: pendiente, activo o resuelto"}
                },
                "required": ["estado"]
            }
        }
    }
]