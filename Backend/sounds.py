# sounds.py
import pygame
import os
import sys
import time

def _carpeta_assets():
    if getattr(sys, "frozen", False):
        # Dentro del .exe
        return os.path.join(os.path.dirname(sys.executable), "assets")
    else:
        # En desarrollo
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

def _reproducir(archivo, duracion):
    ruta = os.path.join(_carpeta_assets(), archivo)
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(ruta)
        pygame.mixer.music.play()
        time.sleep(duracion)
    except Exception:
        pass  # si falla el sonido, la app sigue funcionando

def sonido_exito():
    _reproducir("exito.wav", 2)

def sonido_error():
    _reproducir("error.wav", 2)