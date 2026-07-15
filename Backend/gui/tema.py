# gui/tema.py
import customtkinter as ctk

# ── Paleta Mova ──────────────────────────────────────────────
FONDO           = "#C8A96E"   # dorado Mova
FONDO_CARD      = "#FAF0D7"   # crema claro
CAMPO           = "#E8D9BC"   # beige suave
BTN_PRINCIPAL   = "#B5D97A"   # verde claro
BTN_SECUNDARIO  = "#D4B896"   # beige medio
BTN_PELIGRO     = "#E8A87C"   # naranja suave
BARRA           = "#B8924A"   # dorado oscuro
TEXTO           = "#5C3D1E"   # marrón medio
TEXTO_SUAVE     = "#8B6843"   # marrón suave
TEXTO_CAMPO     = "#9E8060"   # placeholder
ERROR           = "#C0392B"   # rojo claro
EXITO           = "#5A8A3A"   # verde oscuro
ADVERTENCIA     = "#C47F00"   # amarillo oscuro

# ── Jerarquía tipográfica ────────────────────────────────────
def fuente(size=18, weight="normal"):
    return ctk.CTkFont(family="Calibri", size=size, weight=weight)

def fuente_titulo():      return fuente(34, "bold")    # títulos principales
def fuente_seccion():     return fuente(20, "bold")    # subtítulos de sección
def fuente_label():       return fuente(18, "normal")  # labels de campos
def fuente_dato():        return fuente(18, "bold")    # valores de datos
def fuente_boton():       return fuente(20, "bold")    # botones principales
def fuente_boton_sec():   return fuente(18, "normal")  # botones secundarios
def fuente_entrada():     return fuente(18, "normal")  # campos de entrada
def fuente_pequeña():     return fuente(16, "bold")    # errores y éxitos
def fuente_secundaria():  return fuente(16, "normal")  # textos secundarios

# ── Configuración global ─────────────────────────────────────
def aplicar_tema():
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("green")