# gui/frames/control_asistencias_frame.py
import customtkinter as ctk
import threading
import calendar
from datetime import date
from database import obtener_asistencias_por_fecha
from socio_logic import formatear_fecha_legible
from gui.tema import *

MESES_ES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

DIAS_ES = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]

class ControlAsistenciasFrame(ctk.CTkFrame):
    def __init__(self, contenedor, app):
        super().__init__(contenedor, fg_color=FONDO)
        self.app = app
        self._mes_actual       = date.today().month
        self._anio_actual      = date.today().year
        self._dia_seleccionado = None

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._construir_ui()

    def on_show(self):
        self._mes_actual       = date.today().month
        self._anio_actual      = date.today().year
        self._dia_seleccionado = date.today().strftime("%Y-%m-%d")
        self._renderizar_calendario()
        self._cargar_asistencias(self._dia_seleccionado)

    # ════════════════════════════════════════════════════════
    # UI
    # ════════════════════════════════════════════════════════

    def _construir_ui(self):
        outer = ctk.CTkFrame(self, fg_color=FONDO_CARD, corner_radius=24)
        outer.grid(row=0, column=0, sticky="nsew", padx=40, pady=30)
        outer.grid_rowconfigure(0, weight=1)
        outer.grid_columnconfigure(0, weight=5)  # calendario
        outer.grid_columnconfigure(1, weight=1)  # separador
        outer.grid_columnconfigure(2, weight=6)  # tabla

        self._construir_lado_calendario(outer)

        # Separador vertical
        ctk.CTkFrame(
            outer, fg_color=CAMPO, width=2, corner_radius=2
        ).grid(row=0, column=1, sticky="ns", pady=30)

        self._construir_lado_asistencias(outer)

    def _construir_lado_calendario(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=0, sticky="nsew", padx=(30, 10), pady=30)
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            frame, text="Selecciona una fecha",
            font=fuente_seccion(), text_color=TEXTO_SUAVE, anchor="w"
        ).grid(row=0, column=0, sticky="w", pady=(0, 12))

        # Navegación mes
        nav_mes = ctk.CTkFrame(frame, fg_color=CAMPO, corner_radius=12)
        nav_mes.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        nav_mes.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            nav_mes, text="◀", width=50, height=42,
            font=fuente_boton(), fg_color=BTN_SECUNDARIO,
            hover_color="#C4A882", text_color=TEXTO,
            corner_radius=10, command=self._mes_anterior
        ).grid(row=0, column=0, padx=10, pady=8)

        self.label_mes = ctk.CTkLabel(
            nav_mes, text="",
            font=fuente(20, "bold"), text_color=TEXTO, anchor="center")
        self.label_mes.grid(row=0, column=1, sticky="ew")

        ctk.CTkButton(
            nav_mes, text="▶", width=50, height=42,
            font=fuente_boton(), fg_color=BTN_SECUNDARIO,
            hover_color="#C4A882", text_color=TEXTO,
            corner_radius=10, command=self._mes_siguiente
        ).grid(row=0, column=2, padx=10, pady=8)

        # Área calendario
        self.frame_cal = ctk.CTkFrame(frame, fg_color="transparent")
        self.frame_cal.grid(row=2, column=0, sticky="nsew")
        self.frame_cal.grid_columnconfigure((0,1,2,3,4,5,6), weight=1)

        for col, dia in enumerate(DIAS_ES):
            ctk.CTkLabel(
                self.frame_cal, text=dia,
                font=fuente_seccion(), text_color=TEXTO_SUAVE,
                anchor="center"
            ).grid(row=0, column=col, pady=(0, 6), sticky="ew")

    def _construir_lado_asistencias(self, parent):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=2, sticky="nsew", padx=(10, 30), pady=30)
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # Encabezado
        encabezado = ctk.CTkFrame(frame, fg_color="transparent")
        encabezado.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        encabezado.grid_columnconfigure(0, weight=1)

        self.label_fecha_sel = ctk.CTkLabel(
            encabezado, text="",
            font=fuente_seccion(), text_color=TEXTO, anchor="w")
        self.label_fecha_sel.grid(row=0, column=0, sticky="w")

        self.label_total_asist = ctk.CTkLabel(
            encabezado, text="",
            font=fuente_secundaria(), text_color=TEXTO_SUAVE, anchor="w")
        self.label_total_asist.grid(row=1, column=0, sticky="w")

        # Cabecera tabla
        cabecera = ctk.CTkFrame(frame, fg_color=BARRA, corner_radius=10)
        cabecera.grid(row=1, column=0, sticky="ew", pady=(0, 4))
        cabecera.grid_columnconfigure((0,1,2,3), weight=1)

        for col, texto in enumerate(
                ["Número", "Nombre", "Plan", "Hora"]):
            ctk.CTkLabel(
                cabecera, text=texto,
                font=fuente_seccion(), text_color="white", anchor="center"
            ).grid(row=0, column=col, padx=8, pady=12, sticky="ew")

        # Scroll
        self.scroll_asist = ctk.CTkScrollableFrame(
            frame, fg_color="transparent",
            scrollbar_button_color=BTN_SECUNDARIO,
            scrollbar_button_hover_color=BARRA)
        self.scroll_asist.grid(row=2, column=0, sticky="nsew")
        self.scroll_asist.grid_columnconfigure((0,1,2,3), weight=1)

    # ════════════════════════════════════════════════════════
    # Calendario
    # ════════════════════════════════════════════════════════

    def _limpiar_calendario(self):
        for widget in self.frame_cal.winfo_children():
            info = widget.grid_info()
            if info.get("row", 0) >= 1:
                widget.destroy()

    def _renderizar_calendario(self):
        self._limpiar_calendario()

        self.label_mes.configure(
            text=f"{MESES_ES[self._mes_actual - 1]} {self._anio_actual}")

        cal = calendar.monthcalendar(self._anio_actual, self._mes_actual)
        hoy = date.today()

        for semana_idx, semana in enumerate(cal):
            for dia_idx, dia in enumerate(semana):
                if dia == 0:
                    ctk.CTkLabel(
                        self.frame_cal, text="",
                        fg_color="transparent"
                    ).grid(row=semana_idx + 1, column=dia_idx,
                           padx=3, pady=3, sticky="nsew")
                    continue

                fecha_str = (f"{self._anio_actual}-"
                             f"{str(self._mes_actual).zfill(2)}-"
                             f"{str(dia).zfill(2)}")

                es_hoy          = (dia == hoy.day and
                                   self._mes_actual == hoy.month and
                                   self._anio_actual == hoy.year)
                es_seleccionado = fecha_str == self._dia_seleccionado
                es_futuro       = fecha_str > hoy.strftime("%Y-%m-%d")

                if es_seleccionado:
                    color_fondo = "#7DBF5A"
                    color_texto = "white"
                    borde       = "#5A9A3A"
                elif es_hoy:
                    color_fondo = BARRA
                    color_texto = "white"
                    borde       = BARRA
                elif es_futuro:
                    color_fondo = FONDO_CARD
                    color_texto = TEXTO_SUAVE
                    borde       = FONDO_CARD
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
                           padx=3, pady=3, sticky="nsew")
                celda.grid_rowconfigure(0, weight=1)
                celda.grid_columnconfigure(0, weight=1)

                if not es_futuro:
                    celda.bind("<Button-1>",
                               lambda e, f=fecha_str: self._seleccionar_dia(f))

                lbl = ctk.CTkLabel(
                    celda, text=str(dia),
                    font=fuente(16, "bold" if es_seleccionado or es_hoy
                                else "normal"),
                    text_color=color_texto, anchor="center"
                )
                lbl.grid(row=0, column=0, padx=4, pady=6, sticky="nsew")

                if not es_futuro:
                    lbl.bind("<Button-1>",
                             lambda e, f=fecha_str: self._seleccionar_dia(f))

    def _seleccionar_dia(self, fecha_str):
        self._dia_seleccionado = fecha_str
        self._renderizar_calendario()
        self._cargar_asistencias(fecha_str)

    def _mes_anterior(self):
        if self._mes_actual == 1:
            self._mes_actual  = 12
            self._anio_actual -= 1
        else:
            self._mes_actual -= 1
        self._renderizar_calendario()

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
        self._renderizar_calendario()

    # ════════════════════════════════════════════════════════
    # Asistencias
    # ════════════════════════════════════════════════════════

    def _cargar_asistencias(self, fecha_str):
        self._limpiar_tabla()
        self.label_total_asist.configure(text="⏳ Cargando...")

        hoy = date.today().strftime("%Y-%m-%d")
        if fecha_str == hoy:
            self.label_fecha_sel.configure(text="Hoy")
        else:
            self.label_fecha_sel.configure(
                text=formatear_fecha_legible(fecha_str))

        threading.Thread(
            target=self._fetch_asistencias,
            args=(fecha_str,), daemon=True
        ).start()

    def _fetch_asistencias(self, fecha_str):
        try:
            asistencias = obtener_asistencias_por_fecha(fecha_str)
            self.after(0, lambda: self._renderizar_asistencias(asistencias))
        except Exception as e:
            self.after(0, lambda: self._mostrar_error_carga())

    def _mostrar_error_carga(self):
        self._limpiar_tabla()
        self.label_total_asist.configure(text="")
        ctk.CTkLabel(
            self.scroll_asist,
            text="⚠ Error al cargar. Intenta de nuevo.",
            font=fuente_dato(), text_color=ERROR
        ).grid(row=0, column=0, columnspan=4, pady=40)

    def _limpiar_tabla(self):
        for widget in self.scroll_asist.winfo_children():
            widget.destroy()

    def _renderizar_asistencias(self, asistencias):
        self._limpiar_tabla()
        total = len(asistencias)

        if total == 0:
            self.label_total_asist.configure(text="")
            ctk.CTkLabel(
                self.scroll_asist,
                text="Esta fecha no hubo actividad.",
                font=fuente_dato(), text_color=TEXTO_SUAVE
            ).grid(row=0, column=0, columnspan=4, pady=40)
            return

        self.label_total_asist.configure(
            text=f"{total} asistencia{'s' if total != 1 else ''} "
                 f"registrada{'s' if total != 1 else ''}")

        for i, asist in enumerate(asistencias):
            color_fila = FONDO_CARD if i % 2 == 0 else CAMPO

            fila = ctk.CTkFrame(
                self.scroll_asist, fg_color=color_fila, corner_radius=8)
            fila.grid(row=i, column=0, columnspan=4,
                      sticky="ew", pady=2)
            fila.grid_columnconfigure((0,1,2,3), weight=1)

            datos = [
                asist["dni"],
                asist["nombre"],
                asist.get("tipo_plan", "—"),
                asist["hora"],
            ]

            for col, valor in enumerate(datos):
                ctk.CTkLabel(
                    fila, text=valor,
                    font=fuente_dato(), text_color=TEXTO,
                    anchor="center"
                ).grid(row=0, column=col, padx=8, pady=12, sticky="ew")