# gui/splash_screen.py
import customtkinter as ctk
from gui.tema import *

class SplashScreen(ctk.CTkToplevel):
    def __init__(self, parent, logo_img=None):
        super().__init__(parent)
        self.overrideredirect(True)
        self.configure(fg_color=FONDO)

        ancho, alto = 500, 420
        x = (self.winfo_screenwidth()  // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto  // 2)
        self.geometry(f"{ancho}x{alto}+{x}+{y}")
        self.lift()
        self.grab_set()

        self._logo_img = logo_img
        self._construir_ui()

    def _construir_ui(self):
        card = ctk.CTkFrame(
            self, fg_color=FONDO_CARD, corner_radius=24)
        card.pack(fill="both", expand=True, padx=20, pady=20)

        if self._logo_img:
            ctk.CTkLabel(
                card, image=self._logo_img, text="",
                fg_color="transparent"
            ).pack(pady=(36, 8))
        else:
            ctk.CTkLabel(
                card, text="💪", font=fuente(64),
                fg_color="transparent"
            ).pack(pady=(36, 8))

        ctk.CTkLabel(
            card, text="Mova Women",
            font=fuente(30, "bold"), text_color=TEXTO
        ).pack(pady=(0, 4))

        ctk.CTkLabel(
            card, text="Donde nace tu fuerza",
            font=fuente(15), text_color=TEXTO_SUAVE
        ).pack(pady=(0, 28))

        self.barra = ctk.CTkProgressBar(
            card, width=340, height=14,
            corner_radius=7, fg_color=CAMPO,
            progress_color=BTN_PRINCIPAL
        )
        self.barra.pack(pady=(0, 12))
        self.barra.set(0)

        self.label_estado = ctk.CTkLabel(
            card, text="Iniciando...",
            font=fuente(14), text_color=TEXTO_SUAVE
        )
        self.label_estado.pack()

    def actualizar(self, progreso, mensaje):
        self.barra.set(progreso)
        self.label_estado.configure(text=mensaje)
        self.update()

    def cerrar(self):
        self.grab_release()
        self.destroy()