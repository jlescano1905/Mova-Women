# socio_logic.py
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

# ── Planes disponibles ───────────────────────────────────────

PLANES = {
    "15 días": relativedelta(days=15),   # NUEVO
    "1 mes":   relativedelta(months=1),
    "3 meses": relativedelta(months=3),
    "6 meses": relativedelta(months=6),
    "1 año":   relativedelta(years=1),
}

TIPOS_PLAN = ["Essential", "Balance", "Power"]

# ── Fechas ──────────────────────────────────────────────────

def fecha_hoy_str():
    return date.today().strftime("%Y-%m-%d")

def fecha_registro_ahora():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def calcular_fecha_fin(fecha_inicio_str, plan):
    if plan not in PLANES:
        raise ValueError(f"Plan no válido: '{plan}'. Opciones: {list(PLANES.keys())}")
    fecha_inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d").date()
    fecha_fin    = fecha_inicio + PLANES[plan]
    return fecha_fin.strftime("%Y-%m-%d")

def formatear_fecha_legible(fecha_str):
    return datetime.strptime(fecha_str, "%Y-%m-%d").strftime("%d/%m/%Y")

# ── Vigencia ─────────────────────────────────────────────────

def esta_vigente(fecha_inicio_str, fecha_fin_str, fecha_consulta_str=None):
    hoy = (
        datetime.strptime(fecha_consulta_str, "%Y-%m-%d").date()
        if fecha_consulta_str
        else date.today()
    )
    inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d").date()
    fin    = datetime.strptime(fecha_fin_str,    "%Y-%m-%d").date()
    return inicio <= hoy <= fin

def dias_para_vencer(fecha_fin_str):
    fin = datetime.strptime(fecha_fin_str, "%Y-%m-%d").date()
    return (fin - date.today()).days

def fecha_fin_ya_vencida(fecha_fin_str):
    fin = datetime.strptime(fecha_fin_str, "%Y-%m-%d").date()
    return fin < date.today()

# ── Validaciones ─────────────────────────────────────────────

def validar_telefono(telefono):
    return telefono.isdigit() and len(telefono) == 9

def validar_dni(dni):
    return dni.isdigit() and len(dni) == 8

def validar_dni_patron(dni):
    if len(set(dni)) == 1:
        return False
    if dni in ("12345678", "87654321", "01234567", "76543210"):
        return False
    return True

# ── Formato tipo de plan según vigencia ──────────────────────

def formato_tipo_plan(tipo_plan, fecha_fin_str):
    if fecha_fin_ya_vencida(fecha_fin_str):
        return f"⚠ {tipo_plan} (vencido)", "#A0A0A0"
    return tipo_plan, "#7DBF5A"

# ── Texto resumen ────────────────────────────────────────────

def texto_resumen(nombre, apellido, dni, plan, tipo_plan,
                  fecha_inicio_str, fecha_fin_str):
    return (
        f"Nombre: {nombre} {apellido}\n"
        f"DNI: {dni}\n"
        f"Duración: {plan}\n"
        f"Tipo de plan: {tipo_plan}\n"
        f"Inicio: {formatear_fecha_legible(fecha_inicio_str)}\n"
        f"Fin: {formatear_fecha_legible(fecha_fin_str)}"
    )