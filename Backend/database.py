# database.py
from datetime import datetime, date, timedelta
from supabase import create_client, Client

# ── Configuración Supabase ───────────────────────────────────
SUPABASE_URL = "https://ybqqsqbqdetzzbzawngn.supabase.co"
SUPABASE_KEY = "sb_publishable_uHiO3E6F_CZgzjv7lI8w_Q_xn-pfFL_"

# Cliente único reutilizable
_client: Client = None

def get_client() -> Client:
    global _client
    if _client is None:
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client

def init_db():
    get_client()

def hacer_backup():
    pass

# ── Socios ───────────────────────────────────────────────────

def insertar_socio(dni, nombre, apellido, telefono,
                   fecha_inicio, fecha_fin, fecha_registro,
                   tipo_plan, tipo_documento="DNI"):
    sb = get_client()
    sb.table("socios").insert({
        "dni":                  dni,
        "nombre":               nombre,
        "apellido":             apellido,
        "telefono":             telefono,
        "fecha_inicio":         fecha_inicio,
        "fecha_fin":            fecha_fin,
        "fecha_registro":       fecha_registro,
        "notificacion_cerrada": 0,
        "tipo_plan":            tipo_plan,
        "tipo_documento":       tipo_documento
    }).execute()

def buscar_socio_por_dni(dni):
    sb = get_client()
    res = sb.table("socios").select("*").eq("dni", dni).execute()
    return res.data[0] if res.data else None

def listar_socios():
    sb = get_client()
    res = sb.table("socios").select(
        "dni, nombre, apellido, fecha_inicio, fecha_fin, "
        "fecha_registro, tipo_plan, tipo_documento"
    ).order("fecha_registro", desc=True).execute()
    return res.data

def actualizar_telefono(dni, nuevo_telefono):
    sb = get_client()
    sb.table("socios").update(
        {"telefono": nuevo_telefono}
    ).eq("dni", dni).execute()

def renovar_membresia(dni, nueva_fecha_inicio, nueva_fecha_fin, nuevo_tipo_plan):
    sb = get_client()
    sb.table("socios").update({
        "fecha_inicio":         nueva_fecha_inicio,
        "fecha_fin":            nueva_fecha_fin,
        "tipo_plan":            nuevo_tipo_plan,
        "notificacion_cerrada": 0
    }).eq("dni", dni).execute()

def cerrar_notificacion(dni):
    sb = get_client()
    sb.table("socios").update(
        {"notificacion_cerrada": 1}
    ).eq("dni", dni).execute()

def socios_proximos_a_vencer(dias=4):
    sb      = get_client()
    hoy     = date.today()
    limite  = (hoy + timedelta(days=dias)).strftime("%Y-%m-%d")
    hoy_str = hoy.strftime("%Y-%m-%d")

    res = sb.table("socios").select("*").eq(
        "notificacion_cerrada", 0
    ).lte("fecha_fin", limite).gte("fecha_fin", hoy_str).execute()
    return res.data

# ── Asistencias ──────────────────────────────────────────────

def registrar_asistencia(dni, fecha, hora):
    sb = get_client()
    sb.table("asistencias").insert({
        "dni":   dni,
        "fecha": fecha,
        "hora":  hora
    }).execute()

def asistencia_ya_registrada_hoy(dni, fecha):
    sb = get_client()
    res = sb.table("asistencias").select("id").eq(
        "dni", dni).eq("fecha", fecha).limit(1).execute()
    return len(res.data) > 0

def obtener_asistencias_por_dni(dni):
    """
    Retorna todas las fechas de asistencia de una clienta.
    Resultado: lista de strings 'YYYY-MM-DD'
    """
    sb = get_client()
    res = sb.table("asistencias").select("fecha").eq(
        "dni", dni).order("fecha", desc=False).execute()
    return [r["fecha"] for r in res.data]