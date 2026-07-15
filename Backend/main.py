# main.py
from database import init_db, hacer_backup
from gui.tema import aplicar_tema
import customtkinter as ctk
import os, sys

def _ruta_asset(nombre):
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "assets", nombre)

def _cargar_logo(root, size):
    """Carga el logo atado al root para que nunca se destruya."""
    try:
        from PIL import Image
        img = Image.open(_ruta_asset("logo.png"))
        img = img.resize(size, Image.LANCZOS)
        logo = ctk.CTkImage(img, size=size)
        if not hasattr(root, "_logos"):
            root._logos = []
        root._logos.append(logo)
        return logo
    except Exception:
        return None

def main():
    aplicar_tema()

    from gui.main_window import MainWindow
    app = MainWindow()
    app.withdraw()  # ocultar hasta que el splash termine

    logo_splash = _cargar_logo(app, (180, 180))
    logo_barra  = _cargar_logo(app, (48, 48))

    app._logo_img = logo_barra
    app.actualizar_logo_barra()

    from gui.splash_screen import SplashScreen
    splash = SplashScreen(app, logo_splash)
    splash.actualizar(0.1, "Verificando base de datos...")

    hacer_backup()
    splash.actualizar(0.3, "Cargando datos...")

    init_db()
    splash.actualizar(0.5, "Preparando interfaz...")

    splash.actualizar(0.7, "Cargando módulos...")
    app._registrar_frames()

    splash.actualizar(0.9, "Casi listo...")
    splash.actualizar(1.0, "¡Listo!")

    app.after(600, splash.cerrar)
    app.after(700, lambda: (app.state("zoomed"), app.deiconify()))

    app.mainloop()

if __name__ == "__main__":
    main()