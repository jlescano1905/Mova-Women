# gui/frames/lista_frame.py
import customtkinter as ctk
from database import listar_socios, buscar_socio_por_dni
from socio_logic import formatear_fecha_legible
from gui.tema import *

class ListaFrame(ctk.CTkFrame):
    def __init__(self, contenedor, app):
        super().__init__(contenedor, fg_color=FONDO)
        self.app = app
        self._todos = []

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._construir_ui()

    def on_show(self):
        self._cargar_socios()

    def _construir_ui(self):
        # Contenedor principal con padding
        outer = ctk.CTkFrame(self, fg_color=FONDO_CARD, corner_radius=20)
        outer.grid(row=0, column=0, sticky="nsew", padx=40, pady=30)
        outer.grid_rowconfigure(2, weight=1)
        outer.grid_columnconfigure(0, weight=1)

        # ── Título ───────────────────────────────────────────
        ctk.CTkLabel(
            outer,
            text="Lista de socios",
            font=fuente_titulo(), text_color=TEXTO
        ).grid(row=0, column=0, pady=(28, 16), padx=40, sticky="w")

        # ── Barra de búsqueda ────────────────────────────────
        barra = ctk.CTkFrame(outer, fg_color=CAMPO, corner_radius=12)
        barra.grid(row=1, column=0, sticky="ew", padx=40, pady=(0, 16))
        barra.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            barra, text="Buscar por DNI:",
            font=fuente_label(), text_color=TEXTO
        ).grid(row=0, column=0, padx=16, pady=12)

        self.entry_buscar = ctk.CTkEntry(
            barra,
            placeholder_text="Ingresa el DNI",
            height=40, font=fuente_entrada(),
            fg_color=FONDO_CARD,
            border_color=BTN_SECUNDARIO,
            text_color=TEXTO,
            placeholder_text_color=TEXTO_CAMPO,
            corner_radius=8
        )
        self.entry_buscar.grid(
            row=0, column=1, sticky="ew", padx=(0, 8), pady=10)
        self.entry_buscar.bind("<Return>", lambda e: "break")

        ctk.CTkButton(
            barra, text="Filtrar", width=100, height=40,
            font=fuente_boton(), fg_color=BTN_PRINCIPAL,
            hover_color="#9DC95A", text_color=TEXTO,
            corner_radius=8, command=self._filtrar
        ).grid(row=0, column=2, padx=(0, 8), pady=10)

        ctk.CTkButton(
            barra, text="Ver todas", width=110, height=40,
            font=fuente_boton(), fg_color=BTN_SECUNDARIO,
            hover_color="#C4A882", text_color=TEXTO,
            corner_radius=8, command=self._mostrar_todos
        ).grid(row=0, column=3, padx=(0, 8), pady=10)

        self.label_contador = ctk.CTkLabel(
            barra, text="",
            font=fuente_pequeña(), text_color=TEXTO_SUAVE
        )
        self.label_contador.grid(row=0, column=4, padx=16)

        # ── Cabecera tabla ───────────────────────────────────
        cabecera = ctk.CTkFrame(
            outer, fg_color=BARRA, corner_radius=10)
        cabecera.grid(row=2, column=0, sticky="ew", padx=40, pady=(0, 4))
        cabecera.grid_columnconfigure((0,1,2,3), weight=1)

        for col, texto in enumerate(
                ["DNI", "Nombre completo",
                 "Inicio membresía", "Fin membresía"]):
            ctk.CTkLabel(
                cabecera, text=texto,
                font=fuente(14, "bold"),
                text_color="white", anchor="center"
            ).grid(row=0, column=col, padx=10, pady=12, sticky="ew")

        # ── Área scrollable ──────────────────────────────────
        self.scroll = ctk.CTkScrollableFrame(
            outer, fg_color="transparent",
            scrollbar_button_color=BTN_SECUNDARIO,
            scrollbar_button_hover_color=BARRA)
        self.scroll.grid(
            row=3, column=0, sticky="nsew", padx=40, pady=(0, 28))
        self.scroll.grid_columnconfigure((0,1,2,3), weight=1)
        outer.grid_rowconfigure(3, weight=1)

    # ── Datos ────────────────────────────────────────────────

    def _cargar_socios(self):
        self._todos = listar_socios()
        self._renderizar(self._todos)

    def _filtrar(self):
        dni = self.entry_buscar.get().strip()
        if not dni:
            self._mostrar_todos()
            return
        socio = buscar_socio_por_dni(dni)
        self._renderizar([socio] if socio else [])

    def _mostrar_todos(self):
        self.entry_buscar.delete(0, "end")
        self._renderizar(self._todos)

    def _renderizar(self, socios):
        for widget in self.scroll.winfo_children():
            widget.destroy()

        total     = len(self._todos)
        mostrando = len(socios)

        if mostrando == total:
            self.label_contador.configure(
                text=f"Total: {total} socio{'s' if total != 1 else ''}")
        else:
            self.label_contador.configure(
                text=f"Mostrando {mostrando} de {total}")

        if not socios:
            ctk.CTkLabel(
                self.scroll,
                text="No se encontraron socios.",
                font=fuente(15), text_color=TEXTO_SUAVE
            ).grid(row=0, column=0, columnspan=4, pady=40)
            return

        for i, socio in enumerate(socios):
            color_fila = FONDO_CARD if i % 2 == 0 else CAMPO

            fila = ctk.CTkFrame(
                self.scroll, fg_color=color_fila, corner_radius=8)
            fila.grid(row=i, column=0, columnspan=4,
                      sticky="ew", pady=2)
            fila.grid_columnconfigure((0,1,2,3), weight=1)

            datos = [
                socio["dni"],
                f"{socio['nombre']} {socio['apellido']}",
                formatear_fecha_legible(socio["fecha_inicio"]),
                formatear_fecha_legible(socio["fecha_fin"]),
            ]

            for col, valor in enumerate(datos):
                ctk.CTkLabel(
                    fila, text=valor,
                    font=fuente(14), text_color=TEXTO,
                    anchor="center"
                ).grid(row=0, column=col, padx=10, pady=12, sticky="ew")