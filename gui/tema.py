# gui/tema.py
import customtkinter as ctk

# ── Paleta Mova ──────────────────────────────────────────────
FONDO           = "#C8A96E"
FONDO_CARD      = "#FAF0D7"
CAMPO           = "#E8D9BC"
BTN_PRINCIPAL   = "#B5D97A"
BTN_SECUNDARIO  = "#D4B896"
BTN_PELIGRO     = "#E8A87C"
BARRA           = "#B8924A"
TEXTO           = "#5C3D1E"
TEXTO_SUAVE     = "#8B6843"
TEXTO_CAMPO     = "#9E8060"
ERROR           = "#E07B5A"
EXITO           = "#7DBF5A"
ADVERTENCIA     = "#E8C84A"

# ── Tipografía — optimizada para adultos mayores 1920x1080 ───
def fuente(size=18, weight="normal"):
    return ctk.CTkFont(family="Calibri", size=size, weight=weight)

def fuente_titulo():    return fuente(38, "bold")
def fuente_subtitulo(): return fuente(28, "bold")
def fuente_label():     return fuente(20)
def fuente_boton():     return fuente(22, "bold")
def fuente_entrada():   return fuente(20)
def fuente_pequeña():   return fuente(17)

# ── Configuración global ─────────────────────────────────────
def aplicar_tema():
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("green")