# gui/frames/login_frame.py
import customtkinter as ctk
from gui.tema import *

USUARIO_CORRECTO  = "camila"
PASSWORD_CORRECTA = "123456"

class LoginFrame(ctk.CTkFrame):
    def __init__(self, contenedor, app):
        super().__init__(contenedor, fg_color=FONDO)
        self.app = app
        self._construir_ui()
        app.bind("<Return>", lambda e: self._intentar_login())

    def _construir_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(
            self, fg_color=FONDO_CARD,
            corner_radius=24, width=620, height=640)
        card.grid(row=0, column=0)
        card.grid_propagate(False)
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure((0,1,2,3,4,5,6,7,8), weight=1)

        # Logo
        logo_img = getattr(self.app, "_logo_img", None)
        if logo_img:
            ctk.CTkLabel(
                card, image=logo_img, text="",
                fg_color="transparent"
            ).grid(row=0, column=0, pady=(36, 0))
        else:
            ctk.CTkLabel(
                card, text="💪", font=fuente(56),
                fg_color="transparent", text_color=TEXTO
            ).grid(row=0, column=0, pady=(36, 0))

        # Título
        ctk.CTkLabel(
            card, text="Mova Women",
            font=fuente_titulo(), text_color=TEXTO
        ).grid(row=1, column=0, pady=(0, 2))

        # Subtítulo
        ctk.CTkLabel(
            card, text="Donde nace tu fuerza",
            font=fuente_secundaria(), text_color=TEXTO_SUAVE
        ).grid(row=2, column=0, pady=(0, 16))

        # Label usuario
        ctk.CTkLabel(
            card, text="Usuario",
            font=fuente_label(), text_color=TEXTO, anchor="w"
        ).grid(row=3, column=0, sticky="w", padx=70)

        # Entry usuario
        self.entry_usuario = ctk.CTkEntry(
            card,
            placeholder_text="Ingresa tu usuario",
            height=52, font=fuente_entrada(),
            fg_color=CAMPO, border_color=BTN_SECUNDARIO,
            text_color=TEXTO, placeholder_text_color=TEXTO_CAMPO,
            corner_radius=10)
        self.entry_usuario.grid(
            row=4, column=0, padx=70, pady=(4, 16), sticky="ew")

        # Label contraseña
        ctk.CTkLabel(
            card, text="Contraseña",
            font=fuente_label(), text_color=TEXTO, anchor="w"
        ).grid(row=5, column=0, sticky="w", padx=70)

        # Entry contraseña
        self.entry_password = ctk.CTkEntry(
            card,
            placeholder_text="Ingresa tu contraseña",
            show="•", height=52, font=fuente_entrada(),
            fg_color=CAMPO, border_color=BTN_SECUNDARIO,
            text_color=TEXTO, placeholder_text_color=TEXTO_CAMPO,
            corner_radius=10)
        self.entry_password.grid(
            row=6, column=0, padx=70, pady=(4, 8), sticky="ew")

        # Error
        self.label_error = ctk.CTkLabel(
            card, text="",
            font=fuente_pequeña(), text_color=ERROR)
        self.label_error.grid(row=7, column=0, pady=(0, 4))

        # Botón ingresar
        ctk.CTkButton(
            card, text="Ingresar",
            height=56, font=fuente_boton(),
            fg_color=BTN_PRINCIPAL, hover_color="#9DC95A",
            text_color=TEXTO, corner_radius=12,
            command=self._intentar_login
        ).grid(row=8, column=0, padx=70, pady=(4, 36), sticky="ew")

    def _intentar_login(self):
        usuario  = self.entry_usuario.get().strip()
        password = self.entry_password.get().strip()

        if usuario == USUARIO_CORRECTO and password == PASSWORD_CORRECTA:
            self.app.login_exitoso()
        else:
            self.label_error.configure(
                text="⚠ Usuario o contraseña incorrectos")
            self.entry_password.delete(0, "end")