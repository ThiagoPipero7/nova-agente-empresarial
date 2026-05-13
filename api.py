from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from groq import Groq
import json
from config.settings import GROQ_API_KEY, MODELO, SYSTEM_PROMPT
from herramientas.clientes import buscar_cliente, agregar_cliente, listar_clientes, actualizar_cliente, eliminar_cliente, listar_por_estado, DEFINICIONES as CLIENTES_DEF

app = FastAPI()
client = Groq(api_key=GROQ_API_KEY)

sesiones = {}

class Mensaje(BaseModel):
    session_id: str
    mensaje: str

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

@app.post("/chat")
async def chat(data: Mensaje):
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
                resultado = ejecutar_herramienta(nombre, argumentos)

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
async def index():
    return """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nova — Agente Empresarial</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f0f2f5; height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center; }
        .container { width: 100%; max-width: 700px; height: 90vh; background: white; border-radius: 16px; box-shadow: 0 4px 24px rgba(0,0,0,0.1); display: flex; flex-direction: column; overflow: hidden; }
        .header { background: linear-gradient(135deg, #667eea, #764ba2); padding: 20px 24px; color: white; }
        .header h1 { font-size: 22px; font-weight: 600; }
        .header p { font-size: 13px; opacity: 0.85; margin-top: 4px; }
        .messages { flex: 1; overflow-y: auto; padding: 24px; display: flex; flex-direction: column; gap: 16px; }
        .message { display: flex; gap: 10px; max-width: 85%; }
        .message.user { align-self: flex-end; flex-direction: row-reverse; }
        .bubble { padding: 12px 16px; border-radius: 16px; font-size: 14px; line-height: 1.6; white-space: pre-wrap; }
        .message.bot .bubble { background: #f0f2f5; color: #1a1a1a; border-bottom-left-radius: 4px; }
        .message.user .bubble { background: linear-gradient(135deg, #667eea, #764ba2); color: white; border-bottom-right-radius: 4px; }
        .avatar { width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 16px; flex-shrink: 0; background: #f0f2f5; }
        .input-area { padding: 16px 24px; border-top: 1px solid #f0f2f5; display: flex; gap: 12px; }
        .input-area input { flex: 1; padding: 12px 16px; border: 1.5px solid #e0e0e0; border-radius: 24px; font-size: 14px; outline: none; transition: border-color 0.2s; }
        .input-area input:focus { border-color: #667eea; }
        .input-area button { padding: 12px 24px; background: linear-gradient(135deg, #667eea, #764ba2); color: white; border: none; border-radius: 24px; font-size: 14px; cursor: pointer; font-weight: 500; }
        .input-area button:hover { opacity: 0.9; }
        .typing { display: none; align-self: flex-start; }
        .typing .bubble { background: #f0f2f5; color: #888; font-style: italic; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Nova</h1>
            <p>Agente empresarial de gestión de clientes</p>
        </div>
        <div class="messages" id="messages">
            <div class="message bot">
                <div class="avatar">🤖</div>
                <div class="bubble">¡Hola! Soy Nova, tu agente de gestión de clientes. ¿En qué puedo ayudarte hoy?</div>
            </div>
        </div>
        <div class="message typing" id="typing">
            <div class="avatar">🤖</div>
            <div class="bubble">Nova está escribiendo...</div>
        </div>
        <div class="input-area">
            <input type="text" id="input" placeholder="Escribí tu mensaje..." onkeypress="if(event.key==='Enter') enviar()"/>
            <button onclick="enviar()">Enviar</button>
        </div>
    </div>
    <script>
        const sessionId = Math.random().toString(36).substr(2, 9);

        async function enviar() {
            const input = document.getElementById('input');
            const mensaje = input.value.trim();
            if (!mensaje) return;

            agregarMensaje(mensaje, 'user');
            input.value = '';

            document.getElementById('typing').style.display = 'flex';

            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({session_id: sessionId, mensaje})
                });
                const data = await res.json();
                document.getElementById('typing').style.display = 'none';
                agregarMensaje(data.respuesta, 'bot');
            } catch(e) {
                document.getElementById('typing').style.display = 'none';
                agregarMensaje('Error al conectar con Nova', 'bot');
            }
        }

        function agregarMensaje(texto, tipo) {
            const messages = document.getElementById('messages');
            const div = document.createElement('div');
            div.className = `message ${tipo}`;
            div.innerHTML = `
                <div class="avatar">${tipo === 'bot' ? '🤖' : '👤'}</div>
                <div class="bubble">${texto}</div>
            `;
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
        }
    </script>
</body>
</html>
"""