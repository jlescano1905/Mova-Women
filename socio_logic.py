# socio_logic.py
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

# ── Planes disponibles ───────────────────────────────────────

PLANES = {
    "1 mes":   relativedelta(months=1),
    "3 meses": relativedelta(months=3),
    "6 meses": relativedelta(months=6),
    "1 año":   relativedelta(years=1),
}

# ── Fechas ──────────────────────────────────────────────────

def fecha_hoy_str():
    """Retorna la fecha actual del sistema como string YYYY-MM-DD."""
    return date.today().strftime("%Y-%m-%d")

def fecha_registro_ahora():
    """Retorna fecha y hora actual para el campo fecha_registro."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def calcular_fecha_fin(fecha_inicio_str, plan):
    """
    Dado un string 'YYYY-MM-DD' y un plan (ej. '3 meses'),
    retorna la fecha_fin como string 'YYYY-MM-DD'.

    Ejemplo:
        calcular_fecha_fin("2025-06-01", "3 meses") → "2025-09-01"
        calcular_fecha_fin("2025-01-31", "1 mes")   → "2025-02-28"  ✅ correcto
    """
    if plan not in PLANES:
        raise ValueError(f"Plan no válido: '{plan}'. Opciones: {list(PLANES.keys())}")

    fecha_inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d").date()
    fecha_fin    = fecha_inicio + PLANES[plan]
    return fecha_fin.strftime("%Y-%m-%d")

def formatear_fecha_legible(fecha_str):
    """
    Convierte 'YYYY-MM-DD' a 'DD/MM/YYYY' para mostrar en pantalla.
    Ejemplo: '2025-09-01' → '01/09/2025'
    """
    return datetime.strptime(fecha_str, "%Y-%m-%d").strftime("%d/%m/%Y")

# ── Vigencia ─────────────────────────────────────────────────

def esta_vigente(fecha_inicio_str, fecha_fin_str, fecha_consulta_str=None):
    """
    Retorna True si la fecha de consulta está dentro del rango [inicio, fin].
    Si no se pasa fecha_consulta_str, usa la fecha actual del sistema.
    """
    hoy = (
        datetime.strptime(fecha_consulta_str, "%Y-%m-%d").date()
        if fecha_consulta_str
        else date.today()
    )
    inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d").date()
    fin    = datetime.strptime(fecha_fin_str,    "%Y-%m-%d").date()
    return inicio <= hoy <= fin

def dias_para_vencer(fecha_fin_str):
    """
    Retorna cuántos días faltan para que venza la membresía.
    Puede ser negativo si ya venció.
    """
    fin = datetime.strptime(fecha_fin_str, "%Y-%m-%d").date()
    return (fin - date.today()).days

# ── Validaciones ─────────────────────────────────────────────

def validar_telefono(telefono):
    """Retorna True si el teléfono tiene exactamente 9 dígitos numéricos."""
    return telefono.isdigit() and len(telefono) == 9

def validar_dni(dni):
    """Retorna True si el DNI tiene exactamente 8 dígitos numéricos."""
    return dni.isdigit() and len(dni) == 8

# ── Texto resumen para confirmación ──────────────────────────

def texto_resumen(nombre, apellido, dni, plan, fecha_inicio_str, fecha_fin_str):
    """
    Genera el texto de confirmación antes de guardar.
    Ejemplo:
      'El plan de Juan Pérez con DNI 12345678 es de 3 meses.
       Empieza el 01/06/2025 y termina el 01/09/2025.'
    """
    return (
        f"El plan de {nombre} {apellido} con DNI {dni} es de {plan}.\n"
        f"Empieza el {formatear_fecha_legible(fecha_inicio_str)} "
        f"y termina el {formatear_fecha_legible(fecha_fin_str)}."
    )

def fecha_fin_ya_vencida(fecha_fin_str):
    """Retorna True si la fecha_fin calculada ya pasó."""
    from datetime import date
    fin = datetime.strptime(fecha_fin_str, "%Y-%m-%d").date()
    return fin < date.today()