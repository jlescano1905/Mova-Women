# gui/frames/menu_frame.py
import customtkinter as ctk
from gui.tema import *

class MenuFrame(ctk.CTkFrame):
    def __init__(self, contenedor, app):
        super().__init__(contenedor, fg_color=FONDO)
        self.app = app
        self._construir_ui()

    def _construir_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Card central
        card = ctk.CTkFrame(
            self,
            fg_color=FONDO_CARD,
            corner_radius=20,
            width=700, height=580
        )
        card.grid(row=0, column=0)
        card.grid_propagate(False)
        card.grid_rowconfigure(0, weight=1)
        card.grid_rowconfigure((1,2,3,4), weight=2)
        card.grid_rowconfigure(5, weight=1)
        card.grid_columnconfigure(0, weight=1)

        # Saludo
        ctk.CTkLabel(
            card,
            text="¿Qué deseas hacer hoy?",
            font=fuente_titulo(),
            text_color=TEXTO
        ).grid(row=0, column=0, pady=(36, 0))

        # Botones
        botones = [
            ("👤   Ingresar nueva cliente",      "nuevo_socio"),
            ("✅   Asistencia de cliente",         "asistencia"),
            ("📋   Lista de clientes",             "lista"),
            ("✏️    Actualizar datos de cliente",  "actualizar"),
        ]

        for i, (texto, destino) in enumerate(botones, start=1):
            ctk.CTkButton(
                card,
                text=texto,
                height=72,
                font=fuente_boton(),
                fg_color=BTN_PRINCIPAL,
                hover_color="#9DC95A",
                text_color=TEXTO,
                corner_radius=14,
                anchor="w",
                command=lambda d=destino: self.app.mostrar_frame(d)
            ).grid(row=i, column=0, sticky="ew", padx=60, pady=6)

        # Versión
        ctk.CTkLabel(
            card,
            text="Mova Women — Sistema de gestión v1.0",
            font=fuente_pequeña(),
            text_color=TEXTO_SUAVE
        ).grid(row=5, column=0, pady=(0, 20))