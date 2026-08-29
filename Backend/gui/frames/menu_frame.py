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

        # ── CAMBIO: card más alta para acomodar 5 botones ────
        card = ctk.CTkFrame(
            self, fg_color=FONDO_CARD,
            corner_radius=24, width=780, height=900)
        card.grid(row=0, column=0)
        card.grid_propagate(False)
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(0, weight=2)
        card.grid_rowconfigure((1,2,3,4,5), weight=3)
        card.grid_rowconfigure(6, weight=1)
        card.grid_rowconfigure(7, weight=2)

        ctk.CTkLabel(
            card,
            text="¿Qué deseas hacer hoy?",
            font=fuente_titulo(), text_color=TEXTO
        ).grid(row=0, column=0, pady=(36, 0))

        # ── CAMBIO: 5 botones, "Control de asistencias" nuevo ─
        botones = [
            ("👤   Ingresar nueva clienta",       "nuevo_socio"),
            ("✅   Asistencia de clienta",          "asistencia"),
            ("📋   Lista de clientas",              "lista"),
            ("📊   Control de asistencias",         "control_asistencias"),  # NUEVO
            ("📁   Ver datos de clienta",           "actualizar"),
        ]

        for i, (texto, destino) in enumerate(botones, start=1):
            ctk.CTkButton(
                card,
                text=texto,
                height=80,
                font=fuente_boton(),
                fg_color=BTN_PRINCIPAL,
                hover_color="#9DC95A",
                text_color=TEXTO,
                corner_radius=14,
                anchor="w",
                command=lambda d=destino: self.app.mostrar_frame(d)
            ).grid(row=i, column=0, sticky="ew", padx=70, pady=6)

        # Separador
        ctk.CTkFrame(
            card, fg_color=CAMPO, height=2, corner_radius=2
        ).grid(row=6, column=0, sticky="ew", padx=70, pady=(8, 0))

        # Botón cerrar sesión
        ctk.CTkButton(
            card,
            text="🔒  Cerrar sesión",
            height=50,
            font=fuente_boton_sec(),
            fg_color="transparent",
            hover_color=CAMPO,
            text_color=TEXTO_SUAVE,
            border_width=2,
            border_color=BTN_SECUNDARIO,
            corner_radius=12,
            command=self._cerrar_sesion
        ).grid(row=7, column=0, padx=70, pady=(10, 28), sticky="ew")

    def _cerrar_sesion(self):
        dialogo = ctk.CTkToplevel(self)
        dialogo.title("Cerrar sesión")
        dialogo.resizable(False, False)
        dialogo.grab_set()
        dialogo.configure(fg_color=FONDO)
        dialogo.update_idletasks()
        x = (dialogo.winfo_screenwidth()  // 2) - 220
        y = (dialogo.winfo_screenheight() // 2) - 90
        dialogo.geometry(f"440x180+{x}+{y}")

        inner = ctk.CTkFrame(dialogo, fg_color=FONDO_CARD, corner_radius=16)
        inner.pack(fill="both", expand=True, padx=16, pady=16)

        ctk.CTkLabel(
            inner,
            text="¿Deseas cerrar sesión?",
            font=fuente_titulo(), text_color=TEXTO
        ).pack(pady=(24, 16))

        btn_f = ctk.CTkFrame(inner, fg_color="transparent")
        btn_f.pack(fill="x", padx=30, pady=(0, 24))
        btn_f.grid_columnconfigure((0, 1), weight=1)

        def _cancelar():
            dialogo.destroy()

        def _confirmar():
            dialogo.destroy()
            self._ejecutar_cierre()

        ctk.CTkButton(
            btn_f, text="Cancelar", height=48,
            font=fuente_boton_sec(), fg_color=BTN_SECUNDARIO,
            hover_color="#C4A882", text_color=TEXTO,
            corner_radius=10, command=_cancelar
        ).grid(row=0, column=0, padx=(0, 8), sticky="ew")

        ctk.CTkButton(
            btn_f, text="🔒  Sí, cerrar sesión", height=48,
            font=fuente_boton(), fg_color=BTN_PRINCIPAL,
            hover_color="#9DC95A", text_color=TEXTO,
            corner_radius=10, command=_confirmar
        ).grid(row=0, column=1, padx=(8, 0), sticky="ew")

    def _ejecutar_cierre(self):
        login_frame = self.app.frames.get("login")
        if login_frame:
            login_frame.entry_usuario.delete(0, "end")
            login_frame.entry_password.delete(0, "end")
            login_frame.label_error.configure(text="")
        self.app._barra_visible(False)
        self.app.mostrar_frame("login")