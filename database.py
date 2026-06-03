# database.py
import sqlite3
import shutil
import os
import sys
from datetime import datetime

def _carpeta_app():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = _carpeta_app()
DB_PATH  = os.path.join(BASE_DIR, "gimnasio.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS socios (
            id                   INTEGER PRIMARY KEY AUTOINCREMENT,
            dni                  TEXT NOT NULL UNIQUE,
            nombre               TEXT NOT NULL,
            apellido             TEXT NOT NULL,
            telefono             TEXT NOT NULL,
            fecha_inicio         TEXT NOT NULL,
            fecha_fin            TEXT NOT NULL,
            fecha_registro       TEXT NOT NULL,
            notificacion_cerrada INTEGER NOT NULL DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_dni ON socios(dni)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_fecha_registro ON socios(fecha_registro)
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS asistencias (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            dni      TEXT NOT NULL,
            fecha    TEXT NOT NULL,
            hora     TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_asist_dni ON asistencias(dni)
    """)

    conn.commit()
    conn.close()

# ── Socios ───────────────────────────────────────────────────

def insertar_socio(dni, nombre, apellido, telefono,
                   fecha_inicio, fecha_fin, fecha_registro):
    conn = get_connection()
    try:
        conn.execute("""
            INSERT INTO socios
              (dni, nombre, apellido, telefono,
               fecha_inicio, fecha_fin, fecha_registro, notificacion_cerrada)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0)
        """, (dni, nombre, apellido, telefono,
              fecha_inicio, fecha_fin, fecha_registro))
        conn.commit()
    finally:
        conn.close()

def buscar_socio_por_dni(dni):
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM socios WHERE dni = ?", (dni,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def listar_socios():
    conn = get_connection()
    try:
        rows = conn.execute("""
            SELECT dni, nombre, apellido, fecha_inicio, fecha_fin, fecha_registro
            FROM socios
            ORDER BY fecha_registro DESC
        """).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

def actualizar_telefono(dni, nuevo_telefono):
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE socios SET telefono = ? WHERE dni = ?",
            (nuevo_telefono, dni)
        )
        conn.commit()
    finally:
        conn.close()

def renovar_membresia(dni, nueva_fecha_inicio, nueva_fecha_fin):
    conn = get_connection()
    try:
        conn.execute("""
            UPDATE socios
            SET fecha_inicio = ?,
                fecha_fin = ?,
                notificacion_cerrada = 0
            WHERE dni = ?
        """, (nueva_fecha_inicio, nueva_fecha_fin, dni))
        conn.commit()
    finally:
        conn.close()

def cerrar_notificacion(dni):
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE socios SET notificacion_cerrada = 1 WHERE dni = ?",
            (dni,)
        )
        conn.commit()
    finally:
        conn.close()

def socios_proximos_a_vencer(dias=4):
    conn = get_connection()
    try:
        rows = conn.execute("""
            SELECT *
            FROM socios
            WHERE notificacion_cerrada = 0
              AND julianday(fecha_fin) - julianday('now', 'localtime') <= ?
              AND julianday(fecha_fin) - julianday('now', 'localtime') >= 0
        """, (dias,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

# ── Asistencias ──────────────────────────────────────────────

def registrar_asistencia(dni, fecha, hora):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO asistencias (dni, fecha, hora) VALUES (?, ?, ?)",
            (dni, fecha, hora)
        )
        conn.commit()
    finally:
        conn.close()

def asistencia_ya_registrada_hoy(dni, fecha):
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT id FROM asistencias WHERE dni = ? AND fecha = ?",
            (dni, fecha)
        ).fetchone()
        return row is not None
    finally:
        conn.close()

# ── Backup ───────────────────────────────────────────────────

def hacer_backup():
    if not os.path.exists(DB_PATH):
        return

    carpeta = os.path.join(BASE_DIR, "backups")
    os.makedirs(carpeta, exist_ok=True)

    fecha   = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = os.path.join(carpeta, f"gimnasio_{fecha}.db")
    shutil.copy2(DB_PATH, destino)

    archivos = sorted([
        os.path.join(carpeta, f)
        for f in os.listdir(carpeta)
        if f.endswith(".db")
    ])
    while len(archivos) > 7:
        os.remove(archivos.pop(0))