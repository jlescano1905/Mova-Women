# gui/frames/asistencia_frame.py
import customtkinter as ctk
import threading
from datetime import date, datetime
from database import (buscar_socio_por_dni, registrar_asistencia,
                      asistencia_ya_registrada_hoy)
from socio_logic import esta_vigente, validar_dni, formatear_fecha_legible
from sounds import sonido_exito, sonido_error
from gui.tema import *

class AsistenciaFrame(ctk.CTkFrame):
    def __init__(self, contenedor, app):
        super().__init__(contenedor, fg_color=FONDO)
        self.app = app
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._construir_ui()

    def on_show(self):
        self._limpiar()

    def _construir_ui(self):
        card = ctk.CTkFrame(
            self, fg_color=FONDO_CARD,
            corner_radius=24, width=780, height=680)
        card.grid(row=0, column=0)
        card.grid_propagate(False)
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(0, weight=1)
        card.grid_rowconfigure(1, weight=0)
        card.grid_rowconfigure(2, weight=0)
        card.grid_rowconfigure(3, weight=3)
        card.grid_rowconfigure(4, weight=0)

        # Título
        ctk.CTkLabel(
            card,
            text="Asistencia de cliente",
            font=fuente_titulo(), text_color=TEXTO
        ).grid(row=0, column=0, pady=(40, 0))

        # Label DNI
        ctk.CTkLabel(
            card,
            text="Ingresa el DNI de la cliente",
            font=fuente_label(), text_color=TEXTO_SUAVE
        ).grid(row=1, column=0, pady=(20, 4))

        # Entry + botón
        entry_frame = ctk.CTkFrame(card, fg_color="transparent")
        entry_frame.grid(row=2, column=0, padx=80, pady=(0, 16), sticky="ew")
        entry_frame.grid_columnconfigure(0, weight=1)

        self.entry_dni = ctk.CTkEntry(
            entry_frame,
            placeholder_text="8 dígitos",
            height=65, font=fuente(22),
            fg_color=CAMPO, border_color=BTN_SECUNDARIO,
            text_color=TEXTO, placeholder_text_color=TEXTO_CAMPO,
            corner_radius=12)
        self.entry_dni.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        self.entry_dni.bind("<Return>", lambda e: self._verificar())
        self.entry_dni.bind("<KeyPress-Return>", lambda e: "break")

        ctk.CTkButton(
            entry_frame,
            text="Verificar",
            width=160, height=65,
            font=fuente_boton(),
            fg_color=BTN_PRINCIPAL,
            hover_color="#9DC95A",
            text_color=TEXTO,
            corner_radius=12,
            command=self._verificar
        ).grid(row=0, column=1)

        # Resultado
        self.resultado_frame = ctk.CTkFrame(
            card, fg_color="transparent", corner_radius=16)
        self.resultado_frame.grid(
            row=3, column=0, padx=80, pady=(0, 16), sticky="nsew")
        self.resultado_frame.grid_columnconfigure(0, weight=1)
        self.resultado_frame.grid_rowconfigure((0,1,2,3,4), weight=1)

        self.label_nombre = ctk.CTkLabel(
            self.resultado_frame, text="",
            font=fuente(28, "bold"), text_color=TEXTO)
        self.label_nombre.grid(row=0, column=0)

        self.label_datos = ctk.CTkLabel(
            self.resultado_frame, text="",
            font=fuente_label(), text_color=TEXTO_SUAVE)
        self.label_datos.grid(row=1, column=0)

        self.label_vigencia = ctk.CTkLabel(
            self.resultado_frame, text="",
            font=fuente(26, "bold"))
        self.label_vigencia.grid(row=2, column=0, pady=(10, 4))

        self.label_fechas = ctk.CTkLabel(
            self.resultado_frame, text="",
            font=fuente_label(), text_color=TEXTO_SUAVE)
        self.label_fechas.grid(row=3, column=0)

        self.label_extra = ctk.CTkLabel(
            self.resultado_frame, text="",
            font=fuente_label())
        self.label_extra.grid(row=4, column=0, pady=(4, 0))

        # Botón limpiar
        self.btn_limpiar = ctk.CTkButton(
            card,
            text="🔄  Nueva consulta",
            height=60, font=fuente_boton(),
            fg_color=BTN_SECUNDARIO,
            hover_color="#C4A882",
            text_color=TEXTO, corner_radius=14,
            command=self._limpiar
        )
        self.btn_limpiar.grid(row=4, column=0, padx=80, pady=(0, 40), sticky="ew")
        self.btn_limpiar.grid_remove()

    def _limpiar(self):
        self.entry_dni.delete(0, "end")
        self.label_nombre.configure(text="")
        self.label_datos.configure(text="")
        self.label_vigencia.configure(text="")
        self.label_fechas.configure(text="")
        self.label_extra.configure(text="")
        self.resultado_frame.configure(fg_color="transparent")
        self.btn_limpiar.grid_remove()
        self.entry_dni.focus()

    def _verificar(self):
        dni = self.entry_dni.get().strip()

        if not validar_dni(dni):
            self._mostrar_error("⚠ El DNI debe tener 8 dígitos numéricos")
            return

        socio = buscar_socio_por_dni(dni)
        if not socio:
            self._mostrar_error("⚠ DNI no asociado a ningún cliente")
            return

        hoy_str  = date.today().strftime("%Y-%m-%d")
        hora_str = datetime.now().strftime("%H:%M:%S")
        vigente  = esta_vigente(socio["fecha_inicio"], socio["fecha_fin"])

        self.label_nombre.configure(
            text=f"{socio['nombre']} {socio['apellido']}")
        self.label_datos.configure(
            text=f"DNI: {socio['dni']}  |  Tel: {socio['telefono']}")
        self.label_fechas.configure(
            text=(f"Membresía: "
                  f"{formatear_fecha_legible(socio['fecha_inicio'])} → "
                  f"{formatear_fecha_legible(socio['fecha_fin'])}"))
        self.btn_limpiar.grid()

        if not vigente:
            self.resultado_frame.configure(fg_color="#F9DDD5")
            self.label_vigencia.configure(
                text="❌ Membresía vencida", text_color=ERROR)
            self.label_extra.configure(text="", text_color=TEXTO_SUAVE)
            threading.Thread(target=sonido_error, daemon=True).start()
            return

        if asistencia_ya_registrada_hoy(dni, hoy_str):
            self.resultado_frame.configure(fg_color="#FFF8E1")
            self.label_vigencia.configure(
                text="✅ Membresía vigente", text_color=EXITO)
            self.label_extra.configure(
                text="⚠ Ya registró asistencia hoy",
                text_color=ADVERTENCIA)
            return

        registrar_asistencia(dni, hoy_str, hora_str)
        self.resultado_frame.configure(fg_color="#EDF7E1")
        self.label_vigencia.configure(
            text="✅ Membresía vigente", text_color=EXITO)
        self.label_extra.configure(
            text=f"Asistencia registrada a las {hora_str}",
            text_color=EXITO)
        threading.Thread(target=sonido_exito, daemon=True).start()

    def _mostrar_error(self, msg):
        self.label_nombre.configure(text="")
        self.label_datos.configure(text="")
        self.label_vigencia.configure(text=msg, text_color=ERROR)
        self.label_fechas.configure(text="")
        self.label_extra.configure(text="")
        self.resultado_frame.configure(fg_color="transparent")
        self.btn_limpiar.grid()