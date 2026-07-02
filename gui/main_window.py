# gui/main_window.py
import customtkinter as ctk
from gui.tema import *
from database import socios_proximos_a_vencer

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Mova — Sistema de gestión")
        self.withdraw()  # oculta hasta que el splash termine
        self.configure(fg_color=FONDO)
        self._logo_img = None  # se asigna desde main.py

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._construir_barra()
        self._construir_contenedor()
        self._barra_visible(False)

    def _registrar_frames(self):
        """Llamado desde main.py después de cargar logos."""
        from gui.frames.login_frame        import LoginFrame
        from gui.frames.menu_frame         import MenuFrame
        from gui.frames.nuevo_socio_frame  import NuevoSocioFrame
        from gui.frames.asistencia_frame   import AsistenciaFrame
        from gui.frames.lista_frame        import ListaFrame
        from gui.frames.actualizar_frame   import ActualizarFrame
        from gui.frames.notif_frame        import NotifFrame

        self.frames = {}
        for nombre, ClaseFrame in [
            ("login",          LoginFrame),
            ("menu",           MenuFrame),
            ("nuevo_socio",    NuevoSocioFrame),
            ("asistencia",     AsistenciaFrame),
            ("lista",          ListaFrame),
            ("actualizar",     ActualizarFrame),
            ("notificaciones", NotifFrame),
        ]:
            frame = ClaseFrame(self.contenedor, self)
            frame.grid(row=0, column=0, sticky="nsew")
            self.frames[nombre] = frame

        self.mostrar_frame("login")

    def _construir_barra(self):
        self.barra = ctk.CTkFrame(
            self, height=62, corner_radius=0, fg_color=BARRA)
        self.barra.grid(row=0, column=0, sticky="ew")
        self.barra.grid_columnconfigure(1, weight=1)

        # Botón logo — se actualiza después en _registrar_frames
        self.btn_logo = ctk.CTkButton(
            self.barra,
            text="Mova", font=fuente(18, "bold"),
            text_color="white",
            fg_color="transparent",
            hover_color=FONDO,
            command=lambda: self.mostrar_frame("menu")
        )
        self.btn_logo.grid(row=0, column=0, padx=16, pady=6)

        self.label_titulo = ctk.CTkLabel(
            self.barra, text="",
            font=fuente(17), text_color="white"
        )
        self.label_titulo.grid(row=0, column=1, sticky="w", padx=10)

        self.btn_campana = ctk.CTkButton(
            self.barra,
            text="🔔 0", width=90, height=38,
            fg_color="transparent",
            hover_color=FONDO,
            text_color="white",
            font=fuente(17, "bold"),
            command=lambda: self.mostrar_frame("notificaciones")
        )
        self.btn_campana.grid(row=0, column=2, padx=20, pady=10)

    def actualizar_logo_barra(self):
        """Actualiza el botón logo con la imagen una vez cargada."""
        if self._logo_img:
            self.btn_logo.configure(
                image=self._logo_img, text="",
                width=54, height=54)

    def _barra_visible(self, visible: bool):
        if visible:
            self.barra.grid()
        else:
            self.barra.grid_remove()

    def _construir_contenedor(self):
        self.contenedor = ctk.CTkFrame(
            self, fg_color=FONDO, corner_radius=0)
        self.contenedor.grid(row=1, column=0, sticky="nsew")
        self.contenedor.grid_rowconfigure(0, weight=1)
        self.contenedor.grid_columnconfigure(0, weight=1)

    TITULOS = {
        "menu":           "",
        "nuevo_socio":    "Ingresar nueva cliente",
        "asistencia":     "Asistencia de cliente",
        "lista":          "Lista de clientes",
        "actualizar":     "Actualizar datos de cliente",
        "notificaciones": "Notificaciones",
    }

    def mostrar_frame(self, nombre):
        frame = self.frames[nombre]
        frame.tkraise()
        self.label_titulo.configure(text=self.TITULOS.get(nombre, ""))
        if hasattr(frame, "on_show"):
            frame.on_show()

    def login_exitoso(self):
        self._barra_visible(True)
        self._actualizar_campana()
        self.mostrar_frame("menu")

    def _actualizar_campana(self):
        notifs = socios_proximos_a_vencer(dias=4)
        cantidad = len(notifs)
        color = "#E07B5A" if cantidad > 0 else "transparent"
        self.btn_campana.configure(
            text=f"🔔 {cantidad}", fg_color=color)