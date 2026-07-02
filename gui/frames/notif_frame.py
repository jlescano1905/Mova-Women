# gui/frames/notif_frame.py
import customtkinter as ctk
from database import socios_proximos_a_vencer, cerrar_notificacion
from socio_logic import formatear_fecha_legible, dias_para_vencer
from gui.tema import *

class NotifFrame(ctk.CTkFrame):
    def __init__(self, contenedor, app):
        super().__init__(contenedor, fg_color=FONDO)
        self.app = app

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._construir_ui()

    def on_show(self):
        self._cargar_notificaciones()

    # ── UI ───────────────────────────────────────────────────

    def _construir_ui(self):
        outer = ctk.CTkFrame(
            self, fg_color=FONDO_CARD, corner_radius=20)
        outer.grid(row=0, column=0, sticky="nsew", padx=40, pady=30)
        outer.grid_rowconfigure(2, weight=1)
        outer.grid_columnconfigure(0, weight=1)

        # Título
        ctk.CTkLabel(
            outer,
            text="🔔 Notificaciones",
            font=fuente_titulo(), text_color=TEXTO
        ).grid(row=0, column=0, sticky="w", padx=40, pady=(28, 4))

        self.label_contador = ctk.CTkLabel(
            outer, text="",
            font=fuente_label(), text_color=TEXTO_SUAVE
        )
        self.label_contador.grid(row=1, column=0, sticky="w", padx=40, pady=(0, 16))

        # Área scrollable
        self.scroll = ctk.CTkScrollableFrame(
            outer, fg_color="transparent",
            scrollbar_button_color=BTN_SECUNDARIO,
            scrollbar_button_hover_color=BARRA
        )
        self.scroll.grid(row=2, column=0, sticky="nsew", padx=40, pady=(0, 28))
        self.scroll.grid_columnconfigure(0, weight=1)

    # ── Datos ────────────────────────────────────────────────

    def _cargar_notificaciones(self):
        for widget in self.scroll.winfo_children():
            widget.destroy()

        notifs = socios_proximos_a_vencer(dias=4)

        if not notifs:
            self.label_contador.configure(
                text="No hay notificaciones pendientes.")
            ctk.CTkLabel(
                self.scroll,
                text="✅ Todo al día, no hay membresías próximas a vencer.",
                font=fuente(15), text_color=TEXTO_SUAVE
            ).grid(row=0, column=0, pady=40)
            return

        total = len(notifs)
        self.label_contador.configure(
            text=f"{total} membresía{'s' if total != 1 else ''} "
                 f"próxima{'s' if total != 1 else ''} a vencer.")

        for i, socio in enumerate(notifs):
            self._construir_tarjeta(i, socio)

    def _construir_tarjeta(self, indice, socio):
        dias = dias_para_vencer(socio["fecha_fin"])

        if dias == 0:
            texto_dias  = "⚠ Vence HOY"
            color_badge = "#E07B5A"
            color_fondo = "#FDF0EA"
        elif dias == 1:
            texto_dias  = "⚠ Vence mañana"
            color_badge = "#E8A87C"
            color_fondo = "#FDF5EE"
        else:
            texto_dias  = f"⚠ Vence en {dias} días"
            color_badge = "#C8A96E"
            color_fondo = FONDO_CARD

        tarjeta = ctk.CTkFrame(
            self.scroll,
            fg_color=color_fondo,
            corner_radius=14,
            border_width=1,
            border_color=BTN_SECUNDARIO
        )
        tarjeta.grid(row=indice, column=0, sticky="ew", pady=6)
        tarjeta.grid_columnconfigure(0, weight=1)

        # Fila superior: nombre + badge
        top = ctk.CTkFrame(tarjeta, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 4))
        top.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            top,
            text=f"{socio['nombre']} {socio['apellido']}",
            font=fuente(17, "bold"), text_color=TEXTO, anchor="w"
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            top, text=texto_dias,
            font=fuente(13, "bold"),
            text_color=color_badge
        ).grid(row=0, column=1, sticky="e")

        # Info: DNI + fecha fin
        ctk.CTkLabel(
            tarjeta,
            text=(f"DNI: {socio['dni']}  |  "
                  f"Finaliza el {formatear_fecha_legible(socio['fecha_fin'])}"),
            font=fuente_label(), text_color=TEXTO_SUAVE, anchor="w"
        ).grid(row=1, column=0, sticky="w", padx=20, pady=(0, 12))

        # Separador
        ctk.CTkFrame(
            tarjeta, fg_color=CAMPO, height=1, corner_radius=1
        ).grid(row=2, column=0, sticky="ew", padx=20)

        # Botones
        btn_frame = ctk.CTkFrame(tarjeta, fg_color="transparent")
        btn_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(10, 16))
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            btn_frame,
            text="📞  Ver contacto",
            height=42, font=fuente_boton(),
            fg_color=BTN_PRINCIPAL,
            hover_color="#9DC95A",
            text_color=TEXTO,
            corner_radius=10,
            command=lambda s=socio: self._notificar(s)
        ).grid(row=0, column=0, padx=(0, 8), sticky="ew")

        ctk.CTkButton(
            btn_frame,
            text="✖  Cerrar notificación",
            height=42, font=fuente_boton(),
            fg_color=BTN_SECUNDARIO,
            hover_color="#C4A882",
            text_color=TEXTO,
            corner_radius=10,
            command=lambda s=socio, t=tarjeta: self._cerrar(s, t)
        ).grid(row=0, column=1, padx=(8, 0), sticky="ew")

    # ── Acciones ─────────────────────────────────────────────

    def _notificar(self, socio):
        dialogo = ctk.CTkToplevel(self)
        dialogo.title("Contacto del socio")
        dialogo.resizable(False, False)
        dialogo.grab_set()
        dialogo.configure(fg_color=FONDO)
        dialogo.update_idletasks()
        x = (dialogo.winfo_screenwidth()  // 2) - 210
        y = (dialogo.winfo_screenheight() // 2) - 100
        dialogo.geometry(f"420x200+{x}+{y}")

        inner = ctk.CTkFrame(dialogo, fg_color=FONDO_CARD, corner_radius=16)
        inner.pack(fill="both", expand=True, padx=16, pady=16)

        ctk.CTkLabel(
            inner,
            text=f"Número de {socio['nombre']}:",
            font=fuente(15), text_color=TEXTO_SUAVE
        ).pack(pady=(24, 6))

        ctk.CTkLabel(
            inner,
            text=socio["telefono"],
            font=fuente(30, "bold"), text_color=TEXTO
        ).pack(pady=(0, 20))

        ctk.CTkButton(
            inner, text="Cerrar", width=140, height=40,
            font=fuente_boton(), fg_color=BTN_SECUNDARIO,
            hover_color="#C4A882", text_color=TEXTO,
            corner_radius=10, command=dialogo.destroy
        ).pack()

    def _cerrar(self, socio, tarjeta):
        cerrar_notificacion(socio["dni"])
        tarjeta.destroy()
        self.app._actualizar_campana()

        notifs = socios_proximos_a_vencer(dias=4)
        if not notifs:
            self.label_contador.configure(
                text="No hay notificaciones pendientes.")
            ctk.CTkLabel(
                self.scroll,
                text="✅ Todo al día, no hay membresías próximas a vencer.",
                font=fuente(15), text_color=TEXTO_SUAVE
            ).grid(row=0, column=0, pady=40)