# gui/frames/historial_frame.py
import customtkinter as ctk
from datetime import date
import calendar
import threading
from database import obtener_asistencias_por_dni
from gui.tema import *

MESES_ES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

DIAS_ES = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]

class HistorialFrame(ctk.CTkFrame):
    def __init__(self, contenedor, app):
        super().__init__(contenedor, fg_color=FONDO)
        self.app    = app
        self._socio = None
        self._asistencias = set()
        self._mes_actual  = date.today().month
        self._anio_actual = date.today().year

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._construir_ui()

    def set_socio(self, socio):
        self._socio = socio
        self._mes_actual  = date.today().month
        self._anio_actual = date.today().year

    def on_show(self):
        if not self._socio:
            return
        self._cargar_asistencias()

    def _cargar_asistencias(self):
        self.label_total.configure(text="Cargando...")
        self._limpiar_calendario()
        threading.Thread(
            target=self._fetch_asistencias, daemon=True).start()

    def _fetch_asistencias(self):
        fechas = obtener_asistencias_por_dni(self._socio["dni"])
        self._asistencias = set(fechas)
        self.after(0, self._renderizar)

    # ── UI ───────────────────────────────────────────────────

    def _construir_ui(self):
        outer = ctk.CTkFrame(self, fg_color=FONDO_CARD, corner_radius=24)
        outer.grid(row=0, column=0, sticky="nsew", padx=40, pady=30)
        outer.grid_rowconfigure(2, weight=1)
        outer.grid_columnconfigure(0, weight=1)

        # ── Encabezado ───────────────────────────────────────
        encabezado = ctk.CTkFrame(outer, fg_color="transparent")
        encabezado.grid(row=0, column=0, sticky="ew", padx=50, pady=(28, 0))
        encabezado.grid_columnconfigure(0, weight=1)

        self.label_nombre = ctk.CTkLabel(
            encabezado, text="",
            font=fuente_titulo(), text_color=TEXTO, anchor="w")
        self.label_nombre.grid(row=0, column=0, sticky="w")

        self.label_total = ctk.CTkLabel(
            encabezado, text="",
            font=fuente_secundaria(), text_color=TEXTO_SUAVE, anchor="w")
        self.label_total.grid(row=1, column=0, sticky="w", pady=(2, 0))

        # ── Navegación de mes ────────────────────────────────
        nav_mes = ctk.CTkFrame(outer, fg_color=CAMPO, corner_radius=14)
        nav_mes.grid(row=1, column=0, sticky="ew", padx=50, pady=(16, 12))
        nav_mes.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            nav_mes, text="◀", width=60, height=46,
            font=fuente_boton(), fg_color=BTN_SECUNDARIO,
            hover_color="#C4A882", text_color=TEXTO,
            corner_radius=10, command=self._mes_anterior
        ).grid(row=0, column=0, padx=12, pady=10)

        self.label_mes = ctk.CTkLabel(
            nav_mes, text="",
            font=fuente(22, "bold"), text_color=TEXTO, anchor="center")
        self.label_mes.grid(row=0, column=1, sticky="ew")

        ctk.CTkButton(
            nav_mes, text="▶", width=60, height=46,
            font=fuente_boton(), fg_color=BTN_SECUNDARIO,
            hover_color="#C4A882", text_color=TEXTO,
            corner_radius=10, command=self._mes_siguiente
        ).grid(row=0, column=2, padx=12, pady=10)

        # ── Área del calendario ──────────────────────────────
        self.frame_cal = ctk.CTkFrame(
            outer, fg_color="transparent")
        self.frame_cal.grid(
            row=2, column=0, sticky="nsew", padx=50, pady=(0, 16))
        self.frame_cal.grid_columnconfigure(
            (0,1,2,3,4,5,6), weight=1)

        for col, dia in enumerate(DIAS_ES):
            ctk.CTkLabel(
                self.frame_cal, text=dia,
                font=fuente_seccion(), text_color=TEXTO_SUAVE,
                anchor="center"
            ).grid(row=0, column=col, pady=(0, 8), sticky="ew")

        # ── Botón volver ─────────────────────────────────────
        ctk.CTkButton(
            outer, text="←  Volver",
            height=50, font=fuente_boton_sec(),
            fg_color=BTN_SECUNDARIO, hover_color="#C4A882",
            text_color=TEXTO, corner_radius=12,
            command=self._volver_a_datos
        ).grid(row=3, column=0, padx=50, pady=(0, 28), sticky="ew")

    def _limpiar_calendario(self):
        for widget in self.frame_cal.winfo_children():
            info = widget.grid_info()
            if info.get("row", 0) >= 1:
                widget.destroy()

    def _renderizar(self):
        self._limpiar_calendario()

        if self._socio:
            self.label_nombre.configure(
                text=f"📅  {self._socio['nombre']} {self._socio['apellido']}")

        self.label_mes.configure(
            text=f"{MESES_ES[self._mes_actual - 1]} {self._anio_actual}")

        asist_mes = [
            f for f in self._asistencias
            if f.startswith(
                f"{self._anio_actual}-{str(self._mes_actual).zfill(2)}")
        ]
        total_mes = len(asist_mes)

        if total_mes == 0:
            self.label_total.configure(
                text=f"Sin asistencias este mes  |  "
                     f"Total acumulado: {len(self._asistencias)}")
        else:
            self.label_total.configure(
                text=f"Asistencias este mes: {total_mes}  |  "
                     f"Total acumulado: {len(self._asistencias)}")

        cal = calendar.monthcalendar(self._anio_actual, self._mes_actual)
        hoy = date.today()

        for semana_idx, semana in enumerate(cal):
            for dia_idx, dia in enumerate(semana):
                if dia == 0:
                    ctk.CTkLabel(
                        self.frame_cal, text="",
                        fg_color="transparent"
                    ).grid(row=semana_idx + 1, column=dia_idx,
                           padx=4, pady=4, sticky="nsew")
                    continue

                fecha_str = (f"{self._anio_actual}-"
                             f"{str(self._mes_actual).zfill(2)}-"
                             f"{str(dia).zfill(2)}")
                tiene_asistencia = fecha_str in self._asistencias
                es_hoy = (dia == hoy.day and
                          self._mes_actual == hoy.month and
                          self._anio_actual == hoy.year)

                if tiene_asistencia:
                    color_fondo = "#7DBF5A"
                    color_texto = "white"
                    borde       = "#5A9A3A"
                elif es_hoy:
                    color_fondo = BARRA
                    color_texto = "white"
                    borde       = BARRA
                else:
                    color_fondo = CAMPO
                    color_texto = TEXTO
                    borde       = BTN_SECUNDARIO

                celda = ctk.CTkFrame(
                    self.frame_cal,
                    fg_color=color_fondo,
                    corner_radius=8,
                    border_width=1,
                    border_color=borde
                )
                celda.grid(row=semana_idx + 1, column=dia_idx,
                           padx=4, pady=4, sticky="nsew")
                celda.grid_rowconfigure(0, weight=1)
                celda.grid_columnconfigure(0, weight=1)

                ctk.CTkLabel(
                    celda, text=str(dia),
                    font=fuente(18, "bold" if tiene_asistencia or es_hoy
                                else "normal"),
                    text_color=color_texto, anchor="center"
                ).grid(row=0, column=0, padx=6, pady=8, sticky="nsew")

    # ── Navegación ───────────────────────────────────────────

    def _mes_anterior(self):
        if self._mes_actual == 1:
            self._mes_actual  = 12
            self._anio_actual -= 1
        else:
            self._mes_actual -= 1
        self._renderizar()

    def _mes_siguiente(self):
        hoy = date.today()
        if (self._anio_actual == hoy.year and
                self._mes_actual >= hoy.month):
            return
        if self._mes_actual == 12:
            self._mes_actual  = 1
            self._anio_actual += 1
        else:
            self._mes_actual += 1
        self._renderizar()

    def _volver_a_datos(self):
        actualizar = self.app.frames.get("actualizar")
        if actualizar:
            actualizar._mostrar_paso(2)
        self.app.frames["actualizar"].tkraise()
        self.app.label_titulo.configure(text="Ver datos de clienta")