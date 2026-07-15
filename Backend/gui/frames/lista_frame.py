# gui/frames/lista_frame.py
import customtkinter as ctk
import threading
from database import listar_socios, buscar_socio_por_dni
from socio_logic import formatear_fecha_legible, formato_tipo_plan
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
        self._mostrar_cargando()
        threading.Thread(target=self._cargar_socios, daemon=True).start()

    def _construir_ui(self):
        outer = ctk.CTkFrame(self, fg_color=FONDO_CARD, corner_radius=24)
        outer.grid(row=0, column=0, sticky="nsew", padx=40, pady=30)
        outer.grid_rowconfigure(3, weight=1)
        outer.grid_columnconfigure(0, weight=1)

        # ── Encabezado ───────────────────────────────────────
        encabezado = ctk.CTkFrame(outer, fg_color="transparent")
        encabezado.grid(row=0, column=0, sticky="ew", padx=50, pady=(28, 0))
        encabezado.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            encabezado,
            text="Lista de clientas",
            font=fuente_titulo(), text_color=TEXTO, anchor="w"
        ).grid(row=0, column=0, sticky="w")

        self.label_contador = ctk.CTkLabel(
            encabezado, text="",
            font=fuente_secundaria(), text_color=TEXTO_SUAVE, anchor="w"
        )
        self.label_contador.grid(row=1, column=0, sticky="w", pady=(2, 0))

        # ── Barra búsqueda ───────────────────────────────────
        barra = ctk.CTkFrame(outer, fg_color=CAMPO, corner_radius=14)
        barra.grid(row=1, column=0, sticky="ew", padx=50, pady=(16, 16))
        barra.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            barra, text="Buscar por número:",
            font=fuente_label(), text_color=TEXTO
        ).grid(row=0, column=0, padx=20, pady=14)

        self.entry_buscar = ctk.CTkEntry(
            barra,
            placeholder_text="Ingresa el número de documento",
            height=46, font=fuente_entrada(),
            fg_color=FONDO_CARD,
            border_color=BTN_SECUNDARIO,
            text_color=TEXTO,
            placeholder_text_color=TEXTO_CAMPO,
            corner_radius=10
        )
        self.entry_buscar.grid(
            row=0, column=1, sticky="ew", padx=(0, 10), pady=12)
        self.entry_buscar.bind("<Return>", lambda e: "break")

        ctk.CTkButton(
            barra, text="Filtrar", width=110, height=46,
            font=fuente_boton(), fg_color=BTN_PRINCIPAL,
            hover_color="#9DC95A", text_color=TEXTO,
            corner_radius=10, command=self._filtrar
        ).grid(row=0, column=2, padx=(0, 8), pady=12)

        ctk.CTkButton(
            barra, text="Ver todas", width=120, height=46,
            font=fuente_boton_sec(), fg_color=BTN_SECUNDARIO,
            hover_color="#C4A882", text_color=TEXTO,
            corner_radius=10, command=self._mostrar_todos
        ).grid(row=0, column=3, padx=(0, 16), pady=12)

        # ── Cabecera tabla ───────────────────────────────────
        cabecera = ctk.CTkFrame(
            outer, fg_color=BARRA, corner_radius=12)
        cabecera.grid(row=2, column=0, sticky="ew", padx=50, pady=(0, 4))
        cabecera.grid_columnconfigure((0,1,2,3,4,5), weight=1)

        for col, texto in enumerate([
                "Tipo doc.", "Número", "Nombre completo",
                "Tipo de plan", "Inicio", "Fin"]):
            ctk.CTkLabel(
                cabecera, text=texto,
                font=fuente_seccion(),
                text_color="white", anchor="center"
            ).grid(row=0, column=col, padx=10, pady=14, sticky="ew")

        # ── Scroll ───────────────────────────────────────────
        self.scroll = ctk.CTkScrollableFrame(
            outer, fg_color="transparent",
            scrollbar_button_color=BTN_SECUNDARIO,
            scrollbar_button_hover_color=BARRA)
        self.scroll.grid(
            row=3, column=0, sticky="nsew", padx=50, pady=(0, 28))
        self.scroll.grid_columnconfigure((0,1,2,3,4,5), weight=1)

    # ── Datos ────────────────────────────────────────────────

    def _mostrar_cargando(self):
        for widget in self.scroll.winfo_children():
            widget.destroy()
        self.label_contador.configure(text="Cargando...")
        ctk.CTkLabel(
            self.scroll,
            text="⏳ Cargando clientas...",
            font=fuente_dato(), text_color=TEXTO_SUAVE
        ).grid(row=0, column=0, columnspan=6, pady=40)

    def _cargar_socios(self):
        self._todos = listar_socios()
        self.after(0, lambda: self._renderizar(self._todos))

    def _filtrar(self):
        numero = self.entry_buscar.get().strip()
        if not numero:
            self._mostrar_todos()
            return
        socio = buscar_socio_por_dni(numero)
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
                text=f"Total: {total} clienta{'s' if total != 1 else ''} "
                     f"registrada{'s' if total != 1 else ''}")
        else:
            self.label_contador.configure(
                text=f"Mostrando {mostrando} de {total} clientas")

        if not socios:
            ctk.CTkLabel(
                self.scroll,
                text="No se encontraron clientas.",
                font=fuente_dato(), text_color=TEXTO_SUAVE
            ).grid(row=0, column=0, columnspan=6, pady=40)
            return

        for i, socio in enumerate(socios):
            color_fila = FONDO_CARD if i % 2 == 0 else CAMPO

            fila = ctk.CTkFrame(
                self.scroll, fg_color=color_fila, corner_radius=10)
            fila.grid(row=i, column=0, columnspan=6,
                      sticky="ew", pady=2)
            fila.grid_columnconfigure((0,1,2,3,4,5), weight=1)

            tipo_texto, tipo_color = formato_tipo_plan(
                socio.get("tipo_plan", "—"),
                socio["fecha_fin"]
            )

            datos = [
                (socio.get("tipo_documento", "DNI"), TEXTO),
                (socio["dni"],                       TEXTO),
                (f"{socio['nombre']} {socio['apellido']}", TEXTO),
                (tipo_texto,                         tipo_color),
                (formatear_fecha_legible(socio["fecha_inicio"]), TEXTO),
                (formatear_fecha_legible(socio["fecha_fin"]),    TEXTO),
            ]

            for col, (valor, color) in enumerate(datos):
                entry = ctk.CTkEntry(
                    fila,
                    font=fuente_dato(),
                    text_color=color,
                    fg_color="transparent",
                    border_width=0,
                    justify="center"
                )
                entry.insert(0, valor)
                entry.configure(state="readonly")
                entry.grid(row=0, column=col, padx=10,
                           pady=14, sticky="ew")