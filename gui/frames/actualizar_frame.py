# gui/frames/actualizar_frame.py
import customtkinter as ctk
from database import (buscar_socio_por_dni, actualizar_telefono,
                      renovar_membresia)
from socio_logic import (validar_dni, validar_telefono, calcular_fecha_fin,
                          texto_resumen, PLANES, fecha_fin_ya_vencida,
                          formatear_fecha_legible)
from gui.widgets.fecha_picker import FechaPicker
from gui.tema import *

class ActualizarFrame(ctk.CTkFrame):
    def __init__(self, contenedor, app):
        super().__init__(contenedor, fg_color=FONDO)
        self.app = app
        self._socio = None
        self._nueva_fecha_ini = ""
        self._nueva_fecha_fin = ""

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._construir_pasos()

    def on_show(self):
        self._resetear()
        self._mostrar_paso(1)

    # ── Pasos ────────────────────────────────────────────────

    def _construir_pasos(self):
        self.paso1     = self._frame_buscar()
        self.paso2     = self._frame_opciones()
        self.paso3_tel = self._frame_actualizar_tel()
        self.paso3_mem = self._frame_renovar_mem()
        for f in (self.paso1, self.paso2, self.paso3_tel, self.paso3_mem):
            f.grid(row=0, column=0, sticky="nsew")

    def _mostrar_paso(self, nombre):
        pasos = {
            1: self.paso1, 2: self.paso2,
            "tel": self.paso3_tel, "mem": self.paso3_mem
        }
        pasos[nombre].tkraise()

    def _resetear(self):
        self._socio = None
        self.entry_dni.delete(0, "end")
        self.label_err_buscar.configure(text="")

    # ════════════════════════════════════════════════════════
    # PASO 1 — Buscar socio
    # ════════════════════════════════════════════════════════

    def _frame_buscar(self):
        f = ctk.CTkFrame(self, fg_color=FONDO)
        f.grid_rowconfigure(0, weight=1)
        f.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(
            f, fg_color=FONDO_CARD,
            corner_radius=24, width=780, height=480)
        card.grid(row=0, column=0)
        card.grid_propagate(False)
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure((0,1,2,3,4), weight=1)

        ctk.CTkLabel(
            card, text="Ver datos de cliente",
            font=fuente_titulo(), text_color=TEXTO
        ).grid(row=0, column=0, pady=(40, 0))

        ctk.CTkLabel(
            card, text="Ingresa el DNI de la cliente",
            font=fuente_label(), text_color=TEXTO_SUAVE
        ).grid(row=1, column=0, pady=(8, 4))

        entry_frame = ctk.CTkFrame(card, fg_color="transparent")
        entry_frame.grid(row=2, column=0, padx=80, pady=(0, 8), sticky="ew")
        entry_frame.grid_columnconfigure(0, weight=1)

        self.entry_dni = ctk.CTkEntry(
            entry_frame, placeholder_text="8 dígitos",
            height=62, font=fuente(22),
            fg_color=CAMPO, border_color=BTN_SECUNDARIO,
            text_color=TEXTO, placeholder_text_color=TEXTO_CAMPO,
            corner_radius=12)
        self.entry_dni.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        self.entry_dni.bind("<Return>", lambda e: "break")

        ctk.CTkButton(
            entry_frame, text="Buscar", width=150, height=62,
            font=fuente_boton(), fg_color=BTN_PRINCIPAL,
            hover_color="#9DC95A", text_color=TEXTO,
            corner_radius=12, command=self._buscar_socio
        ).grid(row=0, column=1)

        self.label_err_buscar = ctk.CTkLabel(
            card, text="", font=fuente_pequeña(), text_color=ERROR)
        self.label_err_buscar.grid(row=3, column=0)

        return f

    def _buscar_socio(self):
        dni = self.entry_dni.get().strip()
        if not validar_dni(dni):
            self.label_err_buscar.configure(
                text="⚠ El DNI debe tener 8 dígitos numéricos")
            return
        socio = buscar_socio_por_dni(dni)
        if not socio:
            self.label_err_buscar.configure(
                text="⚠ DNI incorrecto, no está registrado")
            return
        self._socio = socio
        self._poblar_opciones()
        self._mostrar_paso(2)

    # ════════════════════════════════════════════════════════
    # PASO 2 — Datos actuales y opciones
    # ════════════════════════════════════════════════════════

    def _frame_opciones(self):
        f = ctk.CTkFrame(self, fg_color=FONDO)
        f.grid_rowconfigure(0, weight=1)
        f.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(
            f, fg_color=FONDO_CARD,
            corner_radius=24, width=820, height=660)
        card.grid(row=0, column=0)
        card.grid_propagate(False)
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure((0,1,2,3,4), weight=1)

        ctk.CTkLabel(
            card, text="Datos actuales de la cliente",
            font=fuente_titulo(), text_color=TEXTO
        ).grid(row=0, column=0, pady=(36, 0))

        # Tabla datos
        info = ctk.CTkFrame(card, fg_color=CAMPO, corner_radius=14)
        info.grid(row=1, column=0, padx=60, pady=(12, 0), sticky="ew")
        info.grid_columnconfigure(1, weight=1)

        campos = ["Nombre", "Apellido", "DNI",
                  "Teléfono", "Inicio membresía", "Fin membresía"]
        self.labels_datos = {}

        for i, campo in enumerate(campos):
            color_fila = FONDO_CARD if i % 2 == 0 else CAMPO
            fila = ctk.CTkFrame(info, fg_color=color_fila, corner_radius=8)
            fila.grid(row=i, column=0, columnspan=2,
                      sticky="ew", padx=4, pady=2)
            fila.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                fila, text=f"  {campo}:",
                font=fuente(17, "bold"),
                text_color=TEXTO_SUAVE, anchor="w"
            ).grid(row=0, column=0, padx=16, pady=10, sticky="w")

            lbl = ctk.CTkLabel(
                fila, text="—",
                font=fuente(17), text_color=TEXTO, anchor="w")
            lbl.grid(row=0, column=1, padx=16, pady=10, sticky="w")
            self.labels_datos[campo] = lbl

        ctk.CTkLabel(
            card, text="¿Qué deseas actualizar?",
            font=fuente(20), text_color=TEXTO_SUAVE
        ).grid(row=2, column=0, pady=(16, 4))

        btns = ctk.CTkFrame(card, fg_color="transparent")
        btns.grid(row=3, column=0, padx=60, pady=(0, 8), sticky="ew")
        btns.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            btns, text="📞  Actualizar teléfono", height=62,
            font=fuente_boton(), fg_color=BTN_PRINCIPAL,
            hover_color="#9DC95A", text_color=TEXTO,
            corner_radius=14,
            command=lambda: self._mostrar_paso("tel")
        ).grid(row=0, column=0, padx=(0, 10), sticky="ew")

        ctk.CTkButton(
            btns, text="🔄  Renovar membresía", height=62,
            font=fuente_boton(), fg_color=BTN_PRINCIPAL,
            hover_color="#9DC95A", text_color=TEXTO,
            corner_radius=14, command=self._ir_renovar
        ).grid(row=0, column=1, padx=(10, 0), sticky="ew")

        ctk.CTkButton(
            card, text="←  Volver", height=54,
            font=fuente_boton(), fg_color=BTN_SECUNDARIO,
            hover_color="#C4A882", text_color=TEXTO,
            corner_radius=14,
            command=lambda: self._mostrar_paso(1)
        ).grid(row=4, column=0, padx=60, pady=(0, 32), sticky="ew")

        return f

    def _poblar_opciones(self):
        s = self._socio
        self.labels_datos["Nombre"].configure(text=s["nombre"])
        self.labels_datos["Apellido"].configure(text=s["apellido"])
        self.labels_datos["DNI"].configure(text=s["dni"])
        self.labels_datos["Teléfono"].configure(text=s["telefono"])
        self.labels_datos["Inicio membresía"].configure(
            text=formatear_fecha_legible(s["fecha_inicio"]))
        self.labels_datos["Fin membresía"].configure(
            text=formatear_fecha_legible(s["fecha_fin"]))

    # ════════════════════════════════════════════════════════
    # PASO 3A — Actualizar teléfono
    # ════════════════════════════════════════════════════════

    def _frame_actualizar_tel(self):
        f = ctk.CTkFrame(self, fg_color=FONDO)
        f.grid_rowconfigure(0, weight=1)
        f.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(
            f, fg_color=FONDO_CARD,
            corner_radius=24, width=740, height=460)
        card.grid(row=0, column=0)
        card.grid_propagate(False)
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure((0,1,2,3,4), weight=1)

        ctk.CTkLabel(
            card, text="Actualizar teléfono",
            font=fuente_titulo(), text_color=TEXTO
        ).grid(row=0, column=0, pady=(40, 0))

        ctk.CTkLabel(
            card, text="Nuevo número de teléfono:",
            font=fuente_label(), text_color=TEXTO_SUAVE
        ).grid(row=1, column=0, pady=(8, 4))

        self.entry_tel_nuevo = ctk.CTkEntry(
            card, placeholder_text="9 dígitos", height=62,
            font=fuente(22), fg_color=CAMPO,
            border_color=BTN_SECUNDARIO, text_color=TEXTO,
            placeholder_text_color=TEXTO_CAMPO, corner_radius=12)
        self.entry_tel_nuevo.grid(
            row=2, column=0, padx=80, pady=(0, 8), sticky="ew")
        self.entry_tel_nuevo.bind("<Return>", lambda e: "break")

        self.label_err_tel = ctk.CTkLabel(
            card, text="", font=fuente_pequeña())
        self.label_err_tel.grid(row=3, column=0)

        nav = ctk.CTkFrame(card, fg_color="transparent")
        nav.grid(row=4, column=0, padx=80, pady=(8, 40), sticky="ew")
        nav.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            nav, text="←  Volver", height=62,
            font=fuente_boton(), fg_color=BTN_SECUNDARIO,
            hover_color="#C4A882", text_color=TEXTO,
            corner_radius=14,
            command=lambda: self._mostrar_paso(2)
        ).grid(row=0, column=0, padx=(0, 10), sticky="ew")

        ctk.CTkButton(
            nav, text="💾  Guardar", height=62,
            font=fuente_boton(), fg_color=BTN_PRINCIPAL,
            hover_color="#9DC95A", text_color=TEXTO,
            corner_radius=14, command=self._guardar_telefono
        ).grid(row=0, column=1, padx=(10, 0), sticky="ew")

        return f

    def _guardar_telefono(self):
        tel = self.entry_tel_nuevo.get().strip()
        if not validar_telefono(tel):
            self.label_err_tel.configure(
                text="⚠ El teléfono debe tener 9 dígitos numéricos",
                text_color=ERROR)
            return
        if tel == self._socio["telefono"]:
            self.label_err_tel.configure(
                text="⚠ El número es igual al actual",
                text_color=ERROR)
            return

        dialogo = ctk.CTkToplevel(self)
        dialogo.title("Confirmar cambio")
        dialogo.resizable(False, False)
        dialogo.grab_set()
        dialogo.configure(fg_color=FONDO)
        dialogo.update_idletasks()
        x = (dialogo.winfo_screenwidth()  // 2) - 280
        y = (dialogo.winfo_screenheight() // 2) - 120
        dialogo.geometry(f"560x240+{x}+{y}")

        inner = ctk.CTkFrame(dialogo, fg_color=FONDO_CARD, corner_radius=20)
        inner.pack(fill="both", expand=True, padx=16, pady=16)

        ctk.CTkLabel(
            inner, text="¿Confirmas el cambio de teléfono?",
            font=fuente(22, "bold"), text_color=TEXTO
        ).pack(pady=(28, 10))

        ctk.CTkLabel(
            inner,
            text=f"{self._socio['telefono']}  →  {tel}",
            font=fuente(18), text_color=TEXTO_SUAVE
        ).pack(pady=(0, 20))

        btn_f = ctk.CTkFrame(inner, fg_color="transparent")
        btn_f.pack(fill="x", padx=40, pady=(0, 24))
        btn_f.grid_columnconfigure((0, 1), weight=1)

        def _cancelar():
            dialogo.destroy()

        def _confirmar():
            dialogo.destroy()
            actualizar_telefono(self._socio["dni"], tel)
            self._socio["telefono"] = tel
            self.labels_datos["Teléfono"].configure(text=tel)
            self.entry_tel_nuevo.delete(0, "end")
            self.label_err_tel.configure(
                text="✅ Teléfono actualizado correctamente",
                text_color=EXITO)
            self.after(2000, lambda: self._mostrar_paso(2))

        ctk.CTkButton(
            btn_f, text="Cancelar", height=54,
            font=fuente_boton(), fg_color=BTN_SECUNDARIO,
            hover_color="#C4A882", text_color=TEXTO,
            corner_radius=12, command=_cancelar
        ).grid(row=0, column=0, padx=(0, 10), sticky="ew")

        ctk.CTkButton(
            btn_f, text="✅  Sí, guardar", height=54,
            font=fuente_boton(), fg_color=BTN_PRINCIPAL,
            hover_color="#9DC95A", text_color=TEXTO,
            corner_radius=12, command=_confirmar
        ).grid(row=0, column=1, padx=(10, 0), sticky="ew")

    # ════════════════════════════════════════════════════════
    # PASO 3B — Renovar membresía
    # ════════════════════════════════════════════════════════

    def _frame_renovar_mem(self):
        f = ctk.CTkFrame(self, fg_color=FONDO)
        f.grid_rowconfigure(0, weight=1)
        f.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(
            f, fg_color=FONDO_CARD,
            corner_radius=24, width=840, height=680)
        card.grid(row=0, column=0)
        card.grid_propagate(False)
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure((0,1,2,3,4,5,6,7), weight=1)

        ctk.CTkLabel(
            card, text="Renovar membresía",
            font=fuente_titulo(), text_color=TEXTO
        ).grid(row=0, column=0, pady=(36, 0))

        ctk.CTkLabel(
            card, text="Selecciona el nuevo plan:",
            font=fuente_label(), text_color=TEXTO_SUAVE
        ).grid(row=1, column=0, pady=(8, 4))

        self.plan_var_mem = ctk.StringVar(value="")
        planes_frame = ctk.CTkFrame(card, fg_color="transparent")
        planes_frame.grid(row=2, column=0, pady=(0, 8))

        for i, plan in enumerate(PLANES.keys()):
            ctk.CTkRadioButton(
                planes_frame, text=plan,
                variable=self.plan_var_mem, value=plan,
                font=fuente(20), text_color=TEXTO,
                fg_color=BTN_PRINCIPAL, hover_color="#9DC95A",
                radiobutton_width=28, radiobutton_height=28,
                command=self._on_plan_mem
            ).grid(row=0, column=i, padx=24)

        ctk.CTkLabel(
            card, text="Fecha de inicio de la renovación:",
            font=fuente_label(), text_color=TEXTO_SUAVE
        ).grid(row=3, column=0, pady=(8, 4))

        self.fecha_picker_mem = FechaPicker(card)
        self.fecha_picker_mem.grid(row=4, column=0, pady=(0, 8))

        ctk.CTkButton(
            card, text="👁  Ver resumen", height=58,
            font=fuente_boton(), fg_color=BTN_SECUNDARIO,
            hover_color="#C4A882", text_color=TEXTO,
            corner_radius=14, command=self._ver_resumen_mem
        ).grid(row=5, column=0, padx=80, pady=(0, 4), sticky="ew")

        self.label_resumen_mem = ctk.CTkLabel(
            card, text="",
            font=fuente(18), text_color=TEXTO,
            wraplength=660, justify="center")
        self.label_resumen_mem.grid(row=6, column=0, padx=80, pady=(0, 4))

        self.label_err_mem = ctk.CTkLabel(
            card, text="",
            font=fuente_pequeña(), wraplength=660)
        self.label_err_mem.grid(row=7, column=0, padx=80)

        nav = ctk.CTkFrame(card, fg_color="transparent")
        nav.grid(row=8, column=0, padx=80, pady=(8, 36), sticky="ew")
        nav.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            nav, text="←  Volver", height=62,
            font=fuente_boton(), fg_color=BTN_SECUNDARIO,
            hover_color="#C4A882", text_color=TEXTO,
            corner_radius=14,
            command=lambda: self._mostrar_paso(2)
        ).grid(row=0, column=0, padx=(0, 10), sticky="ew")

        ctk.CTkButton(
            nav, text="🔄  Confirmar renovación", height=62,
            font=fuente_boton(), fg_color=BTN_PRINCIPAL,
            hover_color="#9DC95A", text_color=TEXTO,
            corner_radius=14, command=self._confirmar_renovacion
        ).grid(row=0, column=1, padx=(10, 0), sticky="ew")

        return f

    def _ir_renovar(self):
        self.plan_var_mem.set("")
        self.label_resumen_mem.configure(text="")
        self.label_err_mem.configure(text="")
        self._nueva_fecha_ini = ""
        self._nueva_fecha_fin = ""
        self._mostrar_paso("mem")

    def _on_plan_mem(self):
        self.label_err_mem.configure(text="")

    def _ver_resumen_mem(self):
        plan = self.plan_var_mem.get()
        if not plan:
            self.label_err_mem.configure(
                text="⚠ Selecciona un plan primero",
                text_color=ERROR)
            return

        fecha_ini = self.fecha_picker_mem.get_fecha()
        fecha_fin = calcular_fecha_fin(fecha_ini, plan)

        if fecha_fin_ya_vencida(fecha_fin):
            self._nueva_fecha_ini = ""
            self._nueva_fecha_fin = ""
            self.label_resumen_mem.configure(text="")
            self.label_err_mem.configure(
                text="⚠ La membresía con esa fecha de inicio ya estaría vencida.\n"
                     "Selecciona una fecha de inicio más reciente.",
                text_color=ERROR)
            return

        self._nueva_fecha_ini = fecha_ini
        self._nueva_fecha_fin = fecha_fin
        self.label_err_mem.configure(text="")
        self.label_resumen_mem.configure(
            text=texto_resumen(
                self._socio["nombre"], self._socio["apellido"],
                self._socio["dni"], plan, fecha_ini, fecha_fin),
            text_color=TEXTO)

    def _confirmar_renovacion(self):
        if not self._nueva_fecha_ini:
            self.label_err_mem.configure(
                text="⚠ Primero haz clic en 'Ver resumen'",
                text_color=ERROR)
            return

        plan = self.plan_var_mem.get()

        dialogo = ctk.CTkToplevel(self)
        dialogo.title("Confirmar renovación")
        dialogo.resizable(False, False)
        dialogo.grab_set()
        dialogo.configure(fg_color=FONDO)
        dialogo.update_idletasks()
        x = (dialogo.winfo_screenwidth()  // 2) - 300
        y = (dialogo.winfo_screenheight() // 2) - 150
        dialogo.geometry(f"600x300+{x}+{y}")

        inner = ctk.CTkFrame(dialogo, fg_color=FONDO_CARD, corner_radius=20)
        inner.pack(fill="both", expand=True, padx=16, pady=16)

        ctk.CTkLabel(
            inner, text="¿Confirmas la renovación?",
            font=fuente(22, "bold"), text_color=TEXTO
        ).pack(pady=(30, 10), padx=40)

        ctk.CTkLabel(
            inner,
            text=(f"{self._socio['nombre']} {self._socio['apellido']}  "
                  f"|  DNI: {self._socio['dni']}\n"
                  f"Plan: {plan}  |  "
                  f"{formatear_fecha_legible(self._nueva_fecha_ini)} → "
                  f"{formatear_fecha_legible(self._nueva_fecha_fin)}"),
            font=fuente(17), text_color=TEXTO_SUAVE
        ).pack(pady=(0, 24), padx=40)

        btn_f = ctk.CTkFrame(inner, fg_color="transparent")
        btn_f.pack(fill="x", padx=40, pady=(0, 24))
        btn_f.grid_columnconfigure((0, 1), weight=1)

        def _cancelar():
            dialogo.destroy()

        def _guardar():
            dialogo.destroy()
            renovar_membresia(
                self._socio["dni"],
                self._nueva_fecha_ini,
                self._nueva_fecha_fin)
            self._socio["fecha_inicio"] = self._nueva_fecha_ini
            self._socio["fecha_fin"]    = self._nueva_fecha_fin
            self._poblar_opciones()
            self.app._actualizar_campana()
            self.label_err_mem.configure(
                text="✅ Membresía renovada correctamente.",
                text_color=EXITO)
            self.after(2000, lambda: self._mostrar_paso(2))

        ctk.CTkButton(
            btn_f, text="Cancelar", height=54,
            font=fuente_boton(), fg_color=BTN_SECUNDARIO,
            hover_color="#C4A882", text_color=TEXTO,
            corner_radius=12, command=_cancelar
        ).grid(row=0, column=0, padx=(0, 10), sticky="ew")

        ctk.CTkButton(
            btn_f, text="✅  Sí, renovar", height=54,
            font=fuente_boton(), fg_color=BTN_PRINCIPAL,
            hover_color="#9DC95A", text_color=TEXTO,
            corner_radius=12, command=_guardar
        ).grid(row=0, column=1, padx=(10, 0), sticky="ew")