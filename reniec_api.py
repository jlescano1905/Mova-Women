# reniec_api.py
import requests

API_URL   = "https://apiperu.dev/api/dni"
API_TOKEN = "0n5dBMAhQWNC9pC2jFpJEOJNZHvu964XzkyQCqyStY2jwqIWUWWJ2z7s2B7W"

# Palabras que no deberían aparecer en un nombre real
_PALABRAS_INVALIDAS = {
    "llc", "inc", "corp", "ltd", "s.a", "s.a.", "sac",
    "printers", "solutions", "services", "company", "group",
    "enterprise", "systems", "technologies", "consulting"
}

def _nombre_parece_valido(nombre, apellido):
    """
    Verifica que nombre y apellido parezcan datos reales de persona.
    Rechaza si contienen palabras de empresas o son muy cortos.
    """
    texto = f"{nombre} {apellido}".lower()
    for palabra in _PALABRAS_INVALIDAS:
        if palabra in texto:
            return False
    # Nombre y apellido deben tener al menos 2 caracteres cada uno
    if len(nombre.strip()) < 2 or len(apellido.strip()) < 2:
        return False
    # Solo deben contener letras y espacios
    import re
    if not re.match(r"^[a-záéíóúñüA-ZÁÉÍÓÚÑÜ\s]+$", nombre):
        return False
    if not re.match(r"^[a-záéíóúñüA-ZÁÉÍÓÚÑÜ\s]+$", apellido):
        return False
    return True

def consultar_dni(dni):
    try:
        response = requests.post(
            API_URL,
            json={"dni": dni},
            headers={
                "Authorization": f"Bearer {API_TOKEN}",
                "Content-Type":  "application/json",
                "Accept":        "application/json",
            },
            timeout=5
        )

        if response.status_code == 200:
            data     = response.json()
            info     = data.get("data", {})
            nombre   = info.get("nombres", "").strip().title()
            apellido = (
                info.get("apellido_paterno", "") + " " +
                info.get("apellido_materno", "")
            ).strip().title()

            if nombre and apellido and _nombre_parece_valido(nombre, apellido):
                return {"ok": True, "nombre": nombre, "apellido": apellido}
            else:
                return {"ok": False, "mensaje": "DNI incorrecto"}

        elif response.status_code == 422:
            return {"ok": False, "mensaje": "DNI incorrecto"}

        elif response.status_code == 401:
            return {"ok": False, "mensaje": "Token inválido o expirado"}

        else:
            return {"ok": False, "mensaje": f"Error del servidor ({response.status_code})"}

    except requests.exceptions.ConnectionError:
        return {"ok": False, "mensaje": "Sin conexión a internet"}

    except requests.exceptions.Timeout:
        return {"ok": False, "mensaje": "Tiempo de espera agotado"}

    except Exception as e:
        return {"ok": False, "mensaje": f"Error inesperado: {str(e)}"}