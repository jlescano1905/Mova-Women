# reniec_api.py
import requests
import re

# ── API Principal — factiliza.com ────────────────────────────
TOKEN_PRINCIPAL = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0MTE0OSIsImh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd3MvMjAwOC8wNi9pZGVudGl0eS9jbGFpbXMvcm9sZSI6ImNvbnN1bHRvciJ9.E6G1MCsy1piNaWYNSmrvCLzjgmAOF1KQWRWDo3LN0Fo"

# ── API Respaldo — apiperu.dev ───────────────────────────────
API_URL_RESPALDO = "https://apiperu.dev/api/dni"
TOKEN_RESPALDO   = "523ce0c0a14de0b5c4f9b5408cca51f26f60250f4880407bd65707e7ebf4b57f"

# ── Validación ───────────────────────────────────────────────
_PALABRAS_INVALIDAS = {
    "llc", "inc", "corp", "ltd", "s.a", "s.a.", "sac",
    "printers", "solutions", "services", "company", "group",
    "enterprise", "systems", "technologies", "consulting"
}

def _nombre_parece_valido(nombre, apellido):
    texto = f"{nombre} {apellido}".lower()
    for palabra in _PALABRAS_INVALIDAS:
        if palabra in texto:
            return False
    if len(nombre.strip()) < 2 or len(apellido.strip()) < 2:
        return False
    if not re.match(r"^[a-záéíóúñüA-ZÁÉÍÓÚÑÜ\s]+$", nombre):
        return False
    if not re.match(r"^[a-záéíóúñüA-ZÁÉÍÓÚÑÜ\s]+$", apellido):
        return False
    return True

# ── APIs ─────────────────────────────────────────────────────

def _consultar_principal(dni):
    """API principal: factiliza.com"""
    response = requests.get(
        f"https://api.factiliza.com/v1/dni/info/{dni}",
        headers={
            "Authorization": f"Bearer {TOKEN_PRINCIPAL}",
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
    return None

def _consultar_respaldo(dni):
    """API respaldo: apiperu.dev"""
    response = requests.post(
        API_URL_RESPALDO,
        json={"dni": dni},
        headers={
            "Authorization": f"Bearer {TOKEN_RESPALDO}",
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
    return None

# ── Función principal ────────────────────────────────────────

def consultar_dni(dni):
    """
    Intenta con API principal (factiliza), luego respaldo (apiperu).
    Si ambas fallan retorna error.
    """
    # Intento 1 — principal
    try:
        resultado = _consultar_principal(dni)
        if resultado:
            return resultado
    except Exception:
        pass

    # Intento 2 — respaldo
    try:
        resultado = _consultar_respaldo(dni)
        if resultado:
            return resultado
    except Exception:
        pass

    return {"ok": False, "mensaje": "DNI incorrecto o sin conexión"}