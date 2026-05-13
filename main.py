from groq import Groq
import json
import logging
import time
from config.settings import GROQ_API_KEY, MODELO, SYSTEM_PROMPT
from herramientas.clientes import buscar_cliente, agregar_cliente, listar_clientes, actualizar_cliente, eliminar_cliente, listar_por_estado, DEFINICIONES as CLIENTES_DEF

# --- LOGS ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("agente.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

# --- CLIENTE IA ---
client = Groq(api_key=GROQ_API_KEY)

# --- HERRAMIENTAS ---
herramientas = CLIENTES_DEF

# --- MÉTRICAS ---
metricas = {
    "consultas": 0,
    "herramientas_usadas": 0,
    "tiempo_total": 0.0
}

def ejecutar_herramienta(nombre, argumentos):
    if nombre == "buscar_cliente":
        return buscar_cliente(argumentos["nombre"])
    elif nombre == "agregar_cliente":
        return agregar_cliente(
            argumentos["nombre"],
            argumentos["email"],
            argumentos["telefono"],
            argumentos["consulta"]
        )
    elif nombre == "listar_clientes":
        return listar_clientes()
    elif nombre == "actualizar_cliente":
        return actualizar_cliente(
            argumentos["id"],
            argumentos["campo"],
            argumentos["valor"]
        )
    elif nombre == "eliminar_cliente":
        return eliminar_cliente(argumentos["id"])
    elif nombre == "listar_por_estado":
        return listar_por_estado(argumentos["estado"])
    return "Herramienta no encontrada"

def mostrar_resumen():
    print(f"\n--- Resumen de sesión ---")
    print(f"Consultas realizadas: {metricas['consultas']}")
    print(f"Herramientas usadas:  {metricas['herramientas_usadas']}")
    print(f"Tiempo total:         {metricas['tiempo_total']:.2f} segundos")
    print(f"Promedio por consulta: {metricas['tiempo_total'] / max(metricas['consultas'], 1):.2f}s")

# --- LOOP PRINCIPAL ---

historial = [{"role": "system", "content": SYSTEM_PROMPT}]

log.info("Agente iniciado")
print("\nAgente empresarial iniciado! Escribí 'salir' para terminar.\n")

while True:
    mensaje = input("Vos: ")

    if mensaje.lower() == "salir":
        log.info(f"Sesión terminada | Consultas: {metricas['consultas']} | Herramientas: {metricas['herramientas_usadas']}")
        mostrar_resumen()
        print("Hasta luego!")
        break

    metricas["consultas"] += 1
    inicio = time.time()
    log.info(f"Consulta #{metricas['consultas']} | {mensaje}")

    historial.append({"role": "user", "content": mensaje})

    try:
        respuesta = client.chat.completions.create(
            model=MODELO,
            messages=historial,
            tools=herramientas,
            tool_choice="auto"
        )

        mensaje_ia = respuesta.choices[0].message

        if mensaje_ia.tool_calls:
            historial.append(mensaje_ia)
            resultado = ""

            for tool_call in mensaje_ia.tool_calls:
                nombre = tool_call.function.name
                argumentos = json.loads(tool_call.function.arguments)

                metricas["herramientas_usadas"] += 1
                log.info(f"Herramienta: {nombre} | Args: {argumentos}")

                resultado = ejecutar_herramienta(nombre, argumentos)
                log.info(f"Resultado: {resultado}")

                historial.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": resultado
                })

            respuesta_bot = resultado

        else:
            respuesta_bot = mensaje_ia.content

    except Exception as e:
        respuesta_bot = "Hubo un error procesando tu consulta, intentá de nuevo."
        log.error(f"Error: {str(e)}")

    tiempo = time.time() - inicio
    metricas["tiempo_total"] += tiempo
    log.info(f"Respuesta en {tiempo:.2f}s")

    historial.append({"role": "assistant", "content": respuesta_bot})
    print(f"\nBot: {respuesta_bot}\n")