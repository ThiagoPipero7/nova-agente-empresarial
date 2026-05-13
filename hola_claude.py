from groq import Groq
import json
import requests
import sqlite3
import logging
import time
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

# --- CONFIGURACIÓN DE LOGS ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("agente.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# --- MÉTRICAS ---
metricas = {
    "consultas": 0,
    "herramientas_usadas": 0,
    "tiempo_total": 0.0
}

# --- HERRAMIENTAS ---

def obtener_clima(ciudad):
    geo = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": ciudad, "count": 1, "language": "es"}
    ).json()
    if not geo.get("results"):
        return f"No encontré la ciudad {ciudad}"
    lat = geo["results"][0]["latitude"]
    lon = geo["results"][0]["longitude"]
    nombre = geo["results"][0]["name"]
    clima = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,weathercode,windspeed_10m",
            "timezone": "auto"
        }
    ).json()
    temp = clima["current"]["temperature_2m"]
    viento = clima["current"]["windspeed_10m"]
    return f"{nombre}: {temp}°C, viento {viento} km/h"

def calcular(operacion):
    try:
        return str(eval(operacion))
    except:
        return "No pude calcular eso"

def buscar_cliente(nombre):
    conn = sqlite3.connect("empresa.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes WHERE nombre LIKE ?", (f"%{nombre}%",))
    resultados = cursor.fetchall()
    conn.close()
    if not resultados:
        return "No encontré ningún cliente con ese nombre"
    respuesta = []
    for r in resultados:
        respuesta.append(f"ID:{r[0]} | Nombre:{r[1]} | Email:{r[2]} | Tel:{r[3]} | Consulta:{r[4]}")
    return "\n".join(respuesta)

def agregar_cliente(nombre, email, telefono, consulta):
    conn = sqlite3.connect("empresa.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO clientes (nombre, email, telefono, consulta) VALUES (?, ?, ?, ?)",
        (nombre, email, telefono, consulta)
    )
    conn.commit()
    conn.close()
    return f"Cliente {nombre} agregado correctamente!"

def listar_clientes():
    conn = sqlite3.connect("empresa.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes")
    resultados = cursor.fetchall()
    conn.close()
    if not resultados:
        return "No hay clientes registrados"
    respuesta = []
    for r in resultados:
        respuesta.append(f"ID:{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]}")
    return "\n".join(respuesta)

# --- HERRAMIENTAS PARA LA IA ---

herramientas = [
    {
        "type": "function",
        "function": {
            "name": "obtener_clima",
            "description": "Obtiene el clima actual de cualquier ciudad",
            "parameters": {
                "type": "object",
                "properties": {
                    "ciudad": {"type": "string", "description": "Nombre de la ciudad"}
                },
                "required": ["ciudad"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calcular",
            "description": "Calcula operaciones matemáticas",
            "parameters": {
                "type": "object",
                "properties": {
                    "operacion": {"type": "string", "description": "La operación a calcular"}
                },
                "required": ["operacion"]
            }
        }
    },
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
    }
]

# --- LOOP PRINCIPAL ---

historial = [
    {
        "role": "system",
        "content": "Sos un agente empresarial. Cuando el usuario pida ver, listar o mostrar clientes, SIEMPRE usá la herramienta listar_clientes. Cuando pida buscar un cliente, usá buscar_cliente. Cuando pida agregar un cliente, usá agregar_cliente."
    }
]

log.info("Agente iniciado")
print("\nAgente empresarial iniciado! Escribí 'salir' para terminar.\n")

while True:
    mensaje = input("Vos: ")

    if mensaje.lower() == "salir":
        log.info(f"Sesión terminada | Consultas: {metricas['consultas']} | Herramientas usadas: {metricas['herramientas_usadas']} | Tiempo total: {metricas['tiempo_total']:.2f}s")
        print(f"\n--- Resumen de sesión ---")
        print(f"Consultas realizadas: {metricas['consultas']}")
        print(f"Herramientas usadas:  {metricas['herramientas_usadas']}")
        print(f"Tiempo total:         {metricas['tiempo_total']:.2f} segundos")
        print("Hasta luego!")
        break

    metricas["consultas"] += 1
    inicio = time.time()
    log.info(f"Consulta #{metricas['consultas']} | Usuario: {mensaje}")

    historial.append({"role": "user", "content": mensaje})

    respuesta = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=historial,
        tools=herramientas,
        tool_choice="auto"
    )

    mensaje_ia = respuesta.choices[0].message

    if mensaje_ia.tool_calls:
        historial.append(mensaje_ia)

        for tool_call in mensaje_ia.tool_calls:
            nombre = tool_call.function.name
            argumentos = json.loads(tool_call.function.arguments)

            metricas["herramientas_usadas"] += 1
            log.info(f"Herramienta usada: {nombre} | Args: {argumentos}")

            if nombre == "obtener_clima":
                resultado = obtener_clima(argumentos["ciudad"])
            elif nombre == "calcular":
                resultado = calcular(argumentos["operacion"])
            elif nombre == "buscar_cliente":
                resultado = buscar_cliente(argumentos["nombre"])
            elif nombre == "agregar_cliente":
                resultado = agregar_cliente(
                    argumentos["nombre"],
                    argumentos["email"],
                    argumentos["telefono"],
                    argumentos["consulta"]
                )
            elif nombre == "listar_clientes":
                resultado = listar_clientes()

            log.info(f"Resultado: {resultado}")

            historial.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": resultado
            })

        respuesta_final = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=historial
        )
        respuesta_bot = respuesta_final.choices[0].message.content

    else:
        respuesta_bot = mensaje_ia.content

    tiempo = time.time() - inicio
    metricas["tiempo_total"] += tiempo
    log.info(f"Respuesta en {tiempo:.2f}s | Bot: {respuesta_bot[:80]}...")

    historial.append({"role": "assistant", "content": respuesta_bot})
    print(f"\nBot: {respuesta_bot}\n")