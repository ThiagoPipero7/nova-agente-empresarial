def calcular(operacion):
    try:
        resultado = eval(operacion)
        return str(resultado)
    except ZeroDivisionError:
        return "Error: división por cero"
    except Exception:
        return "No pude calcular eso, revisá la operación"


DEFINICION = {
    "type": "function",
    "function": {
        "name": "calcular",
        "description": "Calcula operaciones matemáticas",
        "parameters": {
            "type": "object",
            "properties": {
                "operacion": {"type": "string", "description": "La operación a calcular, ej: 2+2"}
            },
            "required": ["operacion"]
        }
    }
}