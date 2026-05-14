from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from groq import Groq
import json
from config.settings import GROQ_API_KEY, MODELO, SYSTEM_PROMPT
from herramientas.clientes import buscar_cliente, agregar_cliente, listar_clientes, actualizar_cliente, eliminar_cliente, listar_por_estado, DEFINICIONES as CLIENTES_DEF
from auth import registrar_usuario, login_usuario

app = FastAPI()
client = Groq(api_key=GROQ_API_KEY)
templates = Jinja2Templates(directory="templates")

sesiones = {}
usuarios_logueados = {}

class Mensaje(BaseModel):
    session_id: str
    mensaje: str

class AuthData(BaseModel):
    email: str
    password: str
    session_id: str

def ejecutar_herramienta(nombre, argumentos, user_id):
    if nombre == "buscar_cliente":
        return buscar_cliente(argumentos["nombre"], user_id)
    elif nombre == "agregar_cliente":
        return agregar_cliente(
            argumentos["nombre"],
            argumentos["email"],
            argumentos["telefono"],
            argumentos["consulta"],
            user_id
        )
    elif nombre == "listar_clientes":
        return listar_clientes(user_id)
    elif nombre == "actualizar_cliente":
        return actualizar_cliente(
            argumentos["id"],
            argumentos["campo"],
            argumentos["valor"],
            user_id
        )
    elif nombre == "eliminar_cliente":
        return eliminar_cliente(argumentos["id"], user_id)
    elif nombre == "listar_por_estado":
        return listar_por_estado(argumentos["estado"], user_id)
    return "Herramienta no encontrada"

@app.post("/registro")
async def registro(data: AuthData):
    resultado = registrar_usuario(data.email, data.password)
    if resultado["ok"]:
        usuarios_logueados[data.session_id] = resultado["user_id"]
    return resultado

@app.post("/login")
async def login(data: AuthData):
    resultado = login_usuario(data.email, data.password)
    if resultado["ok"]:
        usuarios_logueados[data.session_id] = resultado["user_id"]
    return resultado

@app.post("/chat")
async def chat(data: Mensaje):
    user_id = usuarios_logueados.get(data.session_id)
    if not user_id:
        return {"respuesta": "Por favor iniciá sesión para continuar."}

    if data.session_id not in sesiones:
        sesiones[data.session_id] = [{"role": "system", "content": SYSTEM_PROMPT}]

    historial = sesiones[data.session_id]
    historial.append({"role": "user", "content": data.mensaje})

    try:
        respuesta = client.chat.completions.create(
            model=MODELO,
            messages=historial,
            tools=CLIENTES_DEF,
            tool_choice="auto"
        )

        mensaje_ia = respuesta.choices[0].message

        if mensaje_ia.tool_calls:
            historial.append(mensaje_ia)
            resultado = ""

            for tool_call in mensaje_ia.tool_calls:
                nombre = tool_call.function.name
                argumentos = json.loads(tool_call.function.arguments)
                resultado = ejecutar_herramienta(nombre, argumentos, user_id)

                historial.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": resultado
                })

            respuesta_bot = resultado
        else:
            respuesta_bot = mensaje_ia.content

        historial.append({"role": "assistant", "content": respuesta_bot})
        sesiones[data.session_id] = historial

        return {"respuesta": respuesta_bot}

    except Exception as e:
        return {"respuesta": f"Error: {str(e)}"}

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html")