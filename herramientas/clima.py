import requests

def obtener_clima(ciudad):
    try:
        geo = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": ciudad, "count": 1, "language": "es"},
            timeout=5
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
            },
            timeout=5
        ).json()

        temp = clima["current"]["temperature_2m"]
        viento = clima["current"]["windspeed_10m"]
        return f"{nombre}: {temp}°C, viento {viento} km/h"

    except requests.exceptions.Timeout:
        return "No pude obtener el clima, el servicio tardó demasiado"
    except Exception as e:
        return f"Error al obtener el clima: {str(e)}"


DEFINICION = {
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
}