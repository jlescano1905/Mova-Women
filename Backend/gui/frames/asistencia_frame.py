# gui/frames/asistencia_frame.py
import customtkinter as ctk
import threading
import os
import sys
from datetime import date, datetime
from database import (buscar_socio_por_dni, registrar_asistencia,
                      asistencia_ya_registrada_hoy, get_client)
from socio_logic import esta_vigente, formatear_fecha_legible
from sounds import sonido_exito, sonido_error
from gui.tema import *

def _ruta_asset(nombre):
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "..")
    return os.path.join(base, "assets", nombre)

class AsistenciaFrame(ctk.CTkFrame):
    def __init__(self, contenedor, app):
        super().__init__(contenedor, fg_color=FONDO)
        self.app = app
        self._logo = None
        self._timer_limpiar = None
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._cargar_logo()
        self._construir_ui()

    def _cargar_logo(self):
        try:
            from PIL import Image
            img = Image.open(_ruta_asset("logo_sinfondo.png"))
            img = img.resize((400, 400), Image.LANCZOS)
            self._logo = ctk.CTkImage(img, size=(400, 400))
        except Exception:
            self._logo = None

    def on_show(self):
        self._limpiar()

    def _construir_ui(self):
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=0)
        self.grid_columnconfigure(0, weight=1)

        # Título
        ctk.CTkLabel(
            self,
            text="Asistencia de clienta",
            font=fuente_titulo(), text_color="white"
        ).grid(row=0, column=0, pady=(36, 20))

        # Entrada documento
        entry_frame = ctk.CTkFrame(self, fg_color="transparent")
        entry_frame.grid(row=1, column=0, padx=200, pady=(0, 16), sticky="ew")
        entry_frame.grid_columnconfigure(0, weight=1)

        self.entry_dni = ctk.CTkEntry(
            entry_frame,
            placeholder_text="Ingresa el número de documento",
            height=68, font=fuente(22),
            fg_color=FONDO_CARD,
            border_color=BTN_SECUNDARIO,
            text_color=TEXTO,
            placeholder_text_color=TEXTO_CAMPO,
            corner_radius=14)
        self.entry_dni.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        self.entry_dni.bind("<Return>", lambda e: self._verificar())
        self.entry_dni.bind("<KeyPress-Return>", lambda e: "break")
        self.entry_dni.bind("<KeyRelease-Return>", lambda e: "break")

        self.btn_verificar = ctk.CTkButton(
            entry_frame,
            text="Verificar",
            width=160, height=68,
            font=fuente_boton(),
            fg_color=BTN_PRINCIPAL,
            hover_color="#9DC95A",
            text_color=TEXTO,
            corner_radius=14,
            command=self._verificar
        )
        self.btn_verificar.grid(row=0, column=1)

        # Logo (estado inicial)
        self.frame_logo = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_logo.grid(row=2, column=0, sticky="nsew")
        self.frame_logo.grid_rowconfigure(0, weight=1)
        self.frame_logo.grid_columnconfigure(0, weight=1)

        if self._logo:
            ctk.CTkLabel(
                self.frame_logo, image=self._logo, text="",
                fg_color="transparent"
            ).grid(row=0, column=0)
        else:
            ctk.CTkLabel(
                self.frame_logo, text="💪",
                font=fuente(80), fg_color="transparent",
                text_color="white"
            ).grid(row=0, column=0)

        # Resultado (oculto inicialmente)
        self.frame_resultado = ctk.CTkFrame(
            self, fg_color="transparent")
        self.frame_resultado.grid(row=2, column=0, sticky="nsew")
        self.frame_resultado.grid_rowconfigure(0, weight=1)
        self.frame_resultado.grid_columnconfigure(0, weight=1)
        self.frame_resultado.grid_remove()

        self.card_resultado = ctk.CTkFrame(
            self.frame_resultado,
            fg_color=FONDO_CARD,
            corner_radius=24)
        self.card_resultado.grid(
            row=0, column=0,
            padx=160, pady=20, sticky="nsew")
        self.card_resultado.grid_columnconfigure(0, weight=1)
        self.card_resultado.grid_rowconfigure((0,1,2,3,4), weight=1)

        self.label_nombre = ctk.CTkLabel(
            self.card_resultado, text="",
            font=fuente(32, "bold"), text_color=TEXTO)
        self.label_nombre.grid(row=0, column=0, pady=(30, 4))

        self.label_datos = ctk.CTkLabel(
            self.card_resultado, text="",
            font=fuente_secundaria(), text_color=TEXTO_SUAVE)
        self.label_datos.grid(row=1, column=0)

        self.label_vigencia = ctk.CTkLabel(
            self.card_resultado, text="",
            font=fuente(36, "bold"))
        self.label_vigencia.grid(row=2, column=0, pady=(20, 8))

        self.label_fechas = ctk.CTkLabel(
            self.card_resultado, text="",
            font=fuente_secundaria(), text_color=TEXTO_SUAVE)
        self.label_fechas.grid(row=3, column=0)

        self.label_extra = ctk.CTkLabel(
            self.card_resultado, text="",
            font=fuente_pequeña())
        self.label_extra.grid(row=4, column=0, pady=(8, 30))

        # Botón nueva consulta
        self.btn_limpiar = ctk.CTkButton(
            self,
            text="🔄  Nueva consulta",
            height=65,
            font=fuente_boton(),
            fg_color=FONDO_CARD,
            hover_color=CAMPO,
            text_color=TEXTO,
            corner_radius=0,
            command=self._limpiar
        )
        self.btn_limpiar.grid(row=3, column=0, sticky="ew")
        self.btn_limpiar.grid_remove()

    # ── Lógica ───────────────────────────────────────────────

    def _rehabilitar_entrada(self):
        self.entry_dni.bind("<Return>", lambda e: self._verificar())
        self.entry_dni.bind("<KeyPress-Return>", lambda e: "break")
        self.entry_dni.bind("<KeyRelease-Return>", lambda e: "break")
        self.btn_verificar.configure(state="normal")

    def _cancelar_timer(self):
        """Cancela el timer de limpieza automática si existe."""
        if self._timer_limpiar:
            self.after_cancel(self._timer_limpiar)
            self._timer_limpiar = None

    def _limpiar(self):
        self._cancelar_timer()
        self.entry_dni.delete(0, "end")
        self.label_nombre.configure(text="")
        self.label_datos.configure(text="")
        self.label_vigencia.configure(text="")
        self.label_fechas.configure(text="")
        self.label_extra.configure(text="")
        self.card_resultado.configure(fg_color=FONDO_CARD)
        self.frame_resultado.grid_remove()
        self.frame_logo.grid()
        self.btn_limpiar.grid_remove()
        self.entry_dni.focus()

    def _verificar(self):
        # Deshabilitar entrada para evitar doble click/enter
        self.entry_dni.unbind("<Return>")
        self.entry_dni.unbind("<KeyPress-Return>")
        self.entry_dni.unbind("<KeyRelease-Return>")
        self.btn_verificar.configure(state="disabled")
        self.after(3000, self._rehabilitar_entrada)

        numero = self.entry_dni.get().strip()

        if not numero:
            self._mostrar_error("⚠ Ingresa el número de documento")
            return

        socio = buscar_socio_por_dni(numero)
        if not socio:
            self._mostrar_error("⚠ Documento no asociado a ninguna clienta")
            return

        hoy_str  = date.today().strftime("%Y-%m-%d")
        hora_str = datetime.now().strftime("%H:%M:%S")
        vigente  = esta_vigente(socio["fecha_inicio"], socio["fecha_fin"])

        self.frame_logo.grid_remove()
        self.frame_resultado.grid()
        self.btn_limpiar.grid()

        self.label_nombre.configure(
            text=f"{socio['nombre']} {socio['apellido']}")
        self.label_datos.configure(
            text=f"{socio.get('tipo_documento', 'DNI')}: {socio['dni']}  |  "
                 f"Tel: {socio['telefono']}  |  "
                 f"Plan: {socio.get('tipo_plan', '—')}")
        self.label_fechas.configure(
            text=(f"Membresía: "
                  f"{formatear_fecha_legible(socio['fecha_inicio'])} → "
                  f"{formatear_fecha_legible(socio['fecha_fin'])}"))

        if not vigente:
            self.card_resultado.configure(fg_color="#F9DDD5")
            self.label_vigencia.configure(
                text="❌  Membresía vencida",
                text_color=ERROR)
            self.label_extra.configure(
                text="La membresía ha expirado. Por favor renueva tu plan.",
                text_color=ERROR)
            threading.Thread(target=sonido_error, daemon=True).start()
            return

        if asistencia_ya_registrada_hoy(numero, hoy_str):
            sb_res = get_client().table("asistencias").select("hora").eq(
                "dni", numero).eq("fecha", hoy_str).execute()
            hora_registro = sb_res.data[0]["hora"] if sb_res.data else "—"

            self.card_resultado.configure(fg_color="#FFF8E1")
            self.label_vigencia.configure(
                text="✅  Membresía vigente",
                text_color=EXITO)
            self.label_extra.configure(
                text=f"⚠ Ya registró asistencia hoy a las {hora_registro}",
                text_color=ADVERTENCIA)
            threading.Thread(target=sonido_exito, daemon=True).start()
            # Limpiar automáticamente después de 15 segundos
            self._cancelar_timer()
            self._timer_limpiar = self.after(10000, self._limpiar)
            return

        registrar_asistencia(numero, hoy_str, hora_str)
        self.card_resultado.configure(fg_color="#EDF7E1")
        self.label_vigencia.configure(
            text="✅  Membresía vigente",
            text_color=EXITO)
        self.label_extra.configure(
            text=f"✔ Asistencia registrada — {hora_str}",
            text_color=EXITO)
        threading.Thread(target=sonido_exito, daemon=True).start()
        # Limpiar automáticamente después de 15 segundos
        self._cancelar_timer()
        self._timer_limpiar = self.after(10000, self._limpiar)

    def _mostrar_error(self, msg):
        self.frame_logo.grid_remove()
        self.frame_resultado.grid()
        self.btn_limpiar.grid()
        self.label_nombre.configure(text="")
        self.label_datos.configure(text="")
        self.label_vigencia.configure(text=msg, text_color=ERROR)
        self.label_fechas.configure(text="")
        self.label_extra.configure(text="")
        self.card_resultado.configure(fg_color=FONDO_CARD)