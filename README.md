# Nova — Agente Empresarial de Gestión de Clientes 🤖

Nova es un agente conversacional inteligente que gestiona tu cartera de clientes en lenguaje natural. Sin formularios, sin interfaces complejas — solo hablale y Nova se encarga.

## ¿Qué puede hacer Nova?

- 👤 **Agregar clientes** con validación de datos en tiempo real
- 🔍 **Buscar clientes** por nombre
- 📋 **Listar toda la cartera** con formato visual claro
- ✏️ **Actualizar datos** de cualquier cliente
- 🗑️ **Eliminar clientes** de la base de datos
- 🔵 **Filtrar por estado** — pendiente, activo o resuelto

## Demo

    Vos: agregá a María García, maria@empresa.com, 1123456789, consulta sobre pricing
    Nova: ✅ Cliente María García agregado correctamente!

    Vos: mostrá todos los clientes activos
    Nova: 👤 María García
             📧 maria@empresa.com
             📱 1123456789
             📋 consulta sobre pricing
             🟢 Activo

## Stack tecnológico

| Componente | Tecnología |
|---|---|
| Motor de IA | Groq API — LLaMA 3.3 70B |
| Base de datos | Supabase (PostgreSQL en la nube) |
| Observabilidad | Logging + métricas de sesión |
| Lenguaje | Python 3.10+ |

## Instalación

1. Cloná el repositorio

        git clone https://github.com/tu-usuario/agente-bot.git
        cd agente-bot

2. Creá el entorno virtual

        python -m venv venv
        venv\Scripts\activate

3. Instalá las dependencias

        pip install groq requests python-dotenv

4. Configurá las variables de entorno — creá un archivo `.env`

        GROQ_API_KEY=tu_api_key_de_groq

5. Corré el agente

        python main.py

## Estructura del proyecto

    agente-bot/
    ├── main.py                  # Punto de entrada
    ├── config/
    │   └── settings.py          # Configuración central
    ├── herramientas/
    │   └── clientes.py          # Gestión de clientes con Supabase
    ├── .env                     # Variables de entorno (no se sube)
    ├── .gitignore
    └── README.md

## Características empresariales

- **Lenguaje natural** — entiende frases informales, errores ortográficos y distintas formas de pedir lo mismo
- **Validaciones** — no permite emails inválidos ni teléfonos incorrectos
- **Base de datos en la nube** — datos accesibles desde cualquier lugar en tiempo real
- **Observabilidad** — logs detallados y métricas de cada sesión
- **Modular** — fácil de extender con nuevas herramientas

---

Desarrollado con Python + Groq + Supabase