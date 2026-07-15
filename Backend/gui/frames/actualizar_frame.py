# gui/frames/actualizar_frame.py
import customtkinter as ctk
from database import (buscar_socio_por_dni, actualizar_telefono,
                      renovar_membresia)
from socio_logic import (validar_dni, validar_telefono, calcular_fecha_fin,
                          texto_resumen, PLANES, TIPOS_PLAN,
                          fecha_fin_ya_vencida, formatear_fecha_legible,
                          formato_tipo_plan)
from gui.widgets.fecha_picker import FechaPicker
from gui.tema import *

class ActualizarFrame(ctk.CTkFrame):
    def __init__(self, contenedor, app):
        super().__init__(contenedor, fg_color=FONDO)
        self.app = app
        self._socio = None
        self._nueva_fecha_ini = ""
        self._nueva_fecha_fin = ""
        self._nuevo_tipo_plan = ""

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
        self.entry_doc.delete(0, "end")
        self.label_err_buscar.configure(text="")

    # ════════════════════════════════════════════════════════
    # PASO 1 — Buscar clienta
    # ════════════════════════════════════════════════════════

    def _frame_buscar(self):
        f = ctk.CTkFrame(self, fg_color=FONDO)
        f.grid_rowconfigure(0, weight=1)
        f.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(
            f, fg_color=FONDO_CARD,
            corner_radius=24, width=740, height=420)
        card.grid(row=0, column=0)
        card.grid_propagate(False)
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure((0,1,2,3), weight=1)

        ctk.CTkLabel(
            card, text="Ver datos de clienta",
            font=fuente_titulo(), text_color=TEXTO
        ).grid(row=0, column=0, pady=(36, 0))

        ctk.CTkLabel(
            card, text="Ingresa el número de documento",
            font=fuente_label(), text_color=TEXTO_SUAVE
        ).grid(row=1, column=0, pady=(8, 4))

        entry_frame = ctk.CTkFrame(card, fg_color="transparent")
        entry_frame.grid(row=2, column=0, padx=70, pady=(0, 8), sticky="ew")
        entry_frame.grid_columnconfigure(0, weight=1)

        self.entry_doc = ctk.CTkEntry(
            entry_frame,
            placeholder_text="Número de documento",
            height=58, font=fuente(20),
            fg_color=CAMPO, border_color=BTN_SECUNDARIO,
            text_color=TEXTO, placeholder_text_color=TEXTO_CAMPO,
            corner_radius=10)
        self.entry_doc.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.entry_doc.bind("<Return>", lambda e: "break")

        ctk.CTkButton(
            entry_frame, text="Buscar", width=140, height=58,
            font=fuente_boton(), fg_color=BTN_PRINCIPAL,
            hover_color="#9DC95A", text_color=TEXTO,
            corner_radius=10, command=self._buscar_socio
        ).grid(row=0, column=1)

        self.label_err_buscar = ctk.CTkLabel(
            card, text="", font=fuente_pequeña(), text_color=ERROR)
        self.label_err_buscar.grid(row=3, column=0)

        return f

    def _buscar_socio(self):
        doc = self.entry_doc.get().strip()
        if not doc:
            self.label_err_buscar.configure(
                text="⚠ Ingresa el número de documento")
            return
        socio = buscar_socio_por_dni(doc)
        if not socio:
            self.label_err_buscar.configure(
                text="⚠ Documento no encontrado en el sistema")
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
            corner_radius=24, width=820, height=720)
        card.grid(row=0, column=0, padx=20, pady=20)
        card.grid_propagate(False)
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(0, weight=1)
        card.grid_rowconfigure(1, weight=4)
        card.grid_rowconfigure(2, weight=1)
        card.grid_rowconfigure(3, weight=2)
        card.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(
            card, text="Datos de la clienta",
            font=fuente_titulo(), text_color=TEXTO
        ).grid(row=0, column=0, pady=(32, 0))

        # ── Tabla de datos con scroll ─────────────────────────
        self.scroll_datos = ctk.CTkScrollableFrame(
            card, fg_color=CAMPO, corner_radius=14,
            scrollbar_button_color=BTN_SECUNDARIO,
            scrollbar_button_hover_color=BARRA)
        self.scroll_datos.grid(row=1, column=0, padx=50,
                               pady=(12, 0), sticky="nsew")
        self.scroll_datos.grid_columnconfigure(1, weight=1)

        campos = ["Nombre", "Apellido", "Tipo de documento",
                  "Número de documento", "Teléfono", "Tipo de plan",
                  "Inicio membresía", "Fin membresía"]
        self.labels_datos = {}

        for i, campo in enumerate(campos):
            color_fila = FONDO_CARD if i % 2 == 0 else CAMPO
            fila = ctk.CTkFrame(
                self.scroll_datos, fg_color=color_fila, corner_radius=8)
            fila.grid(row=i, column=0, columnspan=2,
                      sticky="ew", padx=4, pady=2)
            fila.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                fila, text=f"  {campo}:",
                font=fuente_label(), text_color=TEXTO_SUAVE, anchor="w"
            ).grid(row=0, column=0, padx=14, pady=10, sticky="w")

            lbl = ctk.CTkLabel(
                fila, text="—",
                font=fuente_dato(), text_color=TEXTO, anchor="w")
            lbl.grid(row=0, column=1, padx=14, pady=10, sticky="w")
            self.labels_datos[campo] = lbl

        # Pregunta
        ctk.CTkLabel(
            card, text="¿Qué deseas hacer?",
            font=fuente_seccion(), text_color=TEXTO_SUAVE
        ).grid(row=2, column=0, pady=(16, 4))

        # Botones acción
        btns = ctk.CTkFrame(card, fg_color="transparent")
        btns.grid(row=3, column=0, padx=50, pady=(0, 8), sticky="ew")
        btns.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkButton(
            btns, text="📞  Actualizar teléfono", height=58,
            font=fuente_boton(), fg_color=BTN_PRINCIPAL,
            hover_color="#9DC95A", text_color=TEXTO,
            corner_radius=12,
            command=lambda: self._mostrar_paso("tel")
        ).grid(row=0, column=0, padx=(0, 6), sticky="ew")

        ctk.CTkButton(
            btns, text="🔄  Renovar membresía", height=58,
            font=fuente_boton(), fg_color=BTN_PRINCIPAL,
            hover_color="#9DC95A", text_color=TEXTO,
            corner_radius=12, command=self._ir_renovar
        ).grid(row=0, column=1, padx=6, sticky="ew")

        ctk.CTkButton(
            btns, text="📅  Historial", height=58,
            font=fuente_boton(), fg_color=BTN_PRINCIPAL,
            hover_color="#9DC95A", text_color=TEXTO,
            corner_radius=12, command=self._ir_historial
        ).grid(row=0, column=2, padx=(6, 0), sticky="ew")

        # Volver
        ctk.CTkButton(
            card, text="←  Volver", height=50,
            font=fuente_boton_sec(), fg_color=BTN_SECUNDARIO,
            hover_color="#C4A882", text_color=TEXTO,
            corner_radius=12,
            command=lambda: self._mostrar_paso(1)
        ).grid(row=4, column=0, padx=50, pady=(0, 28), sticky="ew")

        return f

    def _poblar_opciones(self):
        s = self._socio
        tipo_texto, tipo_color = formato_tipo_plan(
            s.get("tipo_plan", "—"), s["fecha_fin"])

        self.labels_datos["Nombre"].configure(text=s["nombre"])
        self.labels_datos["Apellido"].configure(text=s["apellido"])
        self.labels_datos["Tipo de documento"].configure(
            text=s.get("tipo_documento", "DNI"))
        self.labels_datos["Número de documento"].configure(text=s["dni"])
        self.labels_datos["Teléfono"].configure(text=s["telefono"])
        self.labels_datos["Tipo de plan"].configure(
            text=tipo_texto, text_color=tipo_color)
        self.labels_datos["Inicio membresía"].configure(
            text=formatear_fecha_legible(s["fecha_inicio"]))
        self.labels_datos["Fin membresía"].configure(
            text=formatear_fecha_legible(s["fecha_fin"]))

    def _ir_historial(self):
        historial = self.app.frames.get("historial")
        if historial:
            historial.set_socio(self._socio)
        self.app.mostrar_frame("historial")

    # ════════════════════════════════════════════════════════
    # PASO 3A — Actualizar teléfono
    # ════════════════════════════════════════════════════════

    def _frame_actualizar_tel(self):
        f = ctk.CTkFrame(self, fg_color=FONDO)
        f.grid_rowconfigure(0, weight=1)
        f.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(
            f, fg_color=FONDO_CARD,
            corner_radius=24, width=700, height=420)
        card.grid(row=0, column=0)
        card.grid_propagate(False)
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure((0,1,2,3,4), weight=1)

        ctk.CTkLabel(
            card, text="Actualizar teléfono",
            font=fuente_titulo(), text_color=TEXTO
        ).grid(row=0, column=0, pady=(36, 0))

        ctk.CTkLabel(
            card, text="Nuevo número de teléfono:",
            font=fuente_label(), text_color=TEXTO_SUAVE
        ).grid(row=1, column=0, pady=(8, 4))

        self.entry_tel_nuevo = ctk.CTkEntry(
            card, placeholder_text="9 dígitos", height=56,
            font=fuente(20), fg_color=CAMPO,
            border_color=BTN_SECUNDARIO, text_color=TEXTO,
            placeholder_text_color=TEXTO_CAMPO, corner_radius=10)
        self.entry_tel_nuevo.grid(
            row=2, column=0, padx=70, pady=(0, 8), sticky="ew")
        self.entry_tel_nuevo.bind("<Return>", lambda e: "break")

        self.label_err_tel = ctk.CTkLabel(
            card, text="", font=fuente_pequeña())
        self.label_err_tel.grid(row=3, column=0)

        nav = ctk.CTkFrame(card, fg_color="transparent")
        nav.grid(row=4, column=0, padx=70, pady=(8, 36), sticky="ew")
        nav.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            nav, text="←  Volver", height=56,
            font=fuente_boton_sec(), fg_color=BTN_SECUNDARIO,
            hover_color="#C4A882", text_color=TEXTO,
            corner_radius=12,
            command=lambda: self._mostrar_paso(2)
        ).grid(row=0, column=0, padx=(0, 8), sticky="ew")

        ctk.CTkButton(
            nav, text="💾  Guardar", height=56,
            font=fuente_boton(), fg_color=BTN_PRINCIPAL,
            hover_color="#9DC95A", text_color=TEXTO,
            corner_radius=12, command=self._guardar_telefono
        ).grid(row=0, column=1, padx=(8, 0), sticky="ew")

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
        x = (dialogo.winfo_screenwidth()  // 2) - 260
        y = (dialogo.winfo_screenheight() // 2) - 110
        dialogo.geometry(f"520x220+{x}+{y}")

        inner = ctk.CTkFrame(dialogo, fg_color=FONDO_CARD, corner_radius=20)
        inner.pack(fill="both", expand=True, padx=16, pady=16)

        ctk.CTkLabel(
            inner, text="¿Confirmas el cambio de teléfono?",
            font=fuente_titulo(), text_color=TEXTO
        ).pack(pady=(24, 10))

        ctk.CTkLabel(
            inner,
            text=f"{self._socio['telefono']}  →  {tel}",
            font=fuente_dato(), text_color=TEXTO_SUAVE
        ).pack(pady=(0, 16))

        btn_f = ctk.CTkFrame(inner, fg_color="transparent")
        btn_f.pack(fill="x", padx=36, pady=(0, 20))
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
            btn_f, text="Cancelar", height=50,
            font=fuente_boton_sec(), fg_color=BTN_SECUNDARIO,
            hover_color="#C4A882", text_color=TEXTO,
            corner_radius=10, command=_cancelar
        ).grid(row=0, column=0, padx=(0, 8), sticky="ew")

        ctk.CTkButton(
            btn_f, text="✅  Sí, guardar", height=50,
            font=fuente_boton(), fg_color=BTN_PRINCIPAL,
            hover_color="#9DC95A", text_color=TEXTO,
            corner_radius=10, command=_confirmar
        ).grid(row=0, column=1, padx=(8, 0), sticky="ew")

    # ════════════════════════════════════════════════════════
    # PASO 3B — Renovar membresía
    # ════════════════════════════════════════════════════════

    def _frame_renovar_mem(self):
        f = ctk.CTkFrame(self, fg_color=FONDO)
        f.grid_rowconfigure(0, weight=1)
        f.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(
            f, fg_color=FONDO_CARD,
            corner_radius=24, width=860, height=700)
        card.grid(row=0, column=0, padx=20, pady=20)
        card.grid_propagate(False)
        card.grid_columnconfigure((0, 1), weight=1)
        card.grid_rowconfigure(0, weight=2)
        card.grid_rowconfigure(1, weight=1)
        card.grid_rowconfigure((2,3,4,5), weight=2)
        card.grid_rowconfigure(6, weight=1)
        card.grid_rowconfigure(7, weight=1)
        card.grid_rowconfigure(8, weight=2)
        card.grid_rowconfigure(9, weight=1)
        card.grid_rowconfigure(10, weight=2)

        ctk.CTkLabel(
            card, text="Renovar membresía",
            font=fuente_titulo(), text_color=TEXTO
        ).grid(row=0, column=0, columnspan=2, pady=(32, 0))

        ctk.CTkLabel(
            card, text="Duración",
            font=fuente_seccion(), text_color=TEXTO_SUAVE, anchor="w"
        ).grid(row=1, column=0, sticky="w", padx=60)

        ctk.CTkLabel(
            card, text="Tipo de plan",
            font=fuente_seccion(), text_color=TEXTO_SUAVE, anchor="w"
        ).grid(row=1, column=1, sticky="w", padx=60)

        self.plan_var_mem = ctk.StringVar(value="")
        for i, plan in enumerate(PLANES.keys()):
            ctk.CTkRadioButton(
                card, text=plan,
                variable=self.plan_var_mem, value=plan,
                font=fuente_dato(), text_color=TEXTO,
                fg_color=BTN_PRINCIPAL, hover_color="#9DC95A",
                radiobutton_width=22, radiobutton_height=22,
                command=self._on_seleccion_mem
            ).grid(row=2+i, column=0, sticky="w", padx=80, pady=5)

        self.tipo_plan_var_mem = ctk.StringVar(value="")
        for i, tipo in enumerate(TIPOS_PLAN):
            ctk.CTkRadioButton(
                card, text=tipo,
                variable=self.tipo_plan_var_mem, value=tipo,
                font=fuente_dato(), text_color=TEXTO,
                fg_color=BTN_PRINCIPAL, hover_color="#9DC95A",
                radiobutton_width=22, radiobutton_height=22,
                command=self._on_seleccion_mem
            ).grid(row=2+i, column=1, sticky="w", padx=80, pady=5)

        ctk.CTkLabel(
            card, text="Fecha de inicio de la renovación:",
            font=fuente_label(), text_color=TEXTO_SUAVE
        ).grid(row=6, column=0, columnspan=2, pady=(8, 4))

        self.fecha_picker_mem = FechaPicker(
            card, on_change=lambda: self._ver_resumen_mem())
        self.fecha_picker_mem.grid(
            row=7, column=0, columnspan=2, pady=(0, 8))

        self.label_resumen_mem = ctk.CTkLabel(
            card, text="",
            font=fuente_dato(), text_color=TEXTO,
            wraplength=700, justify="center")
        self.label_resumen_mem.grid(
            row=8, column=0, columnspan=2, padx=60, pady=(0, 4))

        self.label_err_mem = ctk.CTkLabel(
            card, text="",
            font=fuente_pequeña(), wraplength=700)
        self.label_err_mem.grid(
            row=9, column=0, columnspan=2, padx=60)

        nav = ctk.CTkFrame(card, fg_color="transparent")
        nav.grid(row=10, column=0, columnspan=2,
                 padx=60, pady=(8, 32), sticky="ew")
        nav.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            nav, text="←  Volver", height=56,
            font=fuente_boton_sec(), fg_color=BTN_SECUNDARIO,
            hover_color="#C4A882", text_color=TEXTO,
            corner_radius=12,
            command=lambda: self._mostrar_paso(2)
        ).grid(row=0, column=0, padx=(0, 8), sticky="ew")

        ctk.CTkButton(
            nav, text="🔄  Confirmar renovación", height=56,
            font=fuente_boton(), fg_color=BTN_PRINCIPAL,
            hover_color="#9DC95A", text_color=TEXTO,
            corner_radius=12, command=self._confirmar_renovacion
        ).grid(row=0, column=1, padx=(8, 0), sticky="ew")

        return f

    def _ir_renovar(self):
        self.plan_var_mem.set("")
        self.tipo_plan_var_mem.set("")
        self.label_resumen_mem.configure(text="")
        self.label_err_mem.configure(text="")
        self._nueva_fecha_ini = ""
        self._nueva_fecha_fin = ""
        self._nuevo_tipo_plan = ""
        self._mostrar_paso("mem")

    def _on_seleccion_mem(self):
        self.label_err_mem.configure(text="")
        self._ver_resumen_mem()

    def _ver_resumen_mem(self, *args):
        plan      = self.plan_var_mem.get()
        tipo_plan = self.tipo_plan_var_mem.get()

        if not plan or not tipo_plan:
            self.label_resumen_mem.configure(text="")
            self._nueva_fecha_ini = ""
            self._nueva_fecha_fin = ""
            self.label_err_mem.configure(text="")
            return

        fecha_ini = self.fecha_picker_mem.get_fecha()
        fecha_fin = calcular_fecha_fin(fecha_ini, plan)

        if fecha_fin_ya_vencida(fecha_fin):
            self._nueva_fecha_ini = ""
            self._nueva_fecha_fin = ""
            self.label_resumen_mem.configure(text="")
            self.label_err_mem.configure(
                text="⚠ La membresía con esa fecha de inicio ya estaría vencida. "
                     "Selecciona una fecha más reciente.",
                text_color=ERROR)
            return

        self._nueva_fecha_ini = fecha_ini
        self._nueva_fecha_fin = fecha_fin
        self._nuevo_tipo_plan = tipo_plan
        self.label_err_mem.configure(text="")
        self.label_resumen_mem.configure(
            text=texto_resumen(
                self._socio["nombre"], self._socio["apellido"],
                self._socio["dni"], plan, tipo_plan,
                fecha_ini, fecha_fin),
            text_color=TEXTO)

    def _confirmar_renovacion(self):
        if not self.plan_var_mem.get():
            self.label_err_mem.configure(
                text="⚠ Selecciona una duración primero",
                text_color=ERROR)
            return
        if not self.tipo_plan_var_mem.get():
            self.label_err_mem.configure(
                text="⚠ Selecciona un tipo de plan primero",
                text_color=ERROR)
            return
        if not self._nueva_fecha_ini:
            self.label_err_mem.configure(
                text="⚠ La fecha seleccionada no es válida",
                text_color=ERROR)
            return

        plan      = self.plan_var_mem.get()
        tipo_plan = self.tipo_plan_var_mem.get()

        dialogo = ctk.CTkToplevel(self)
        dialogo.title("Confirmar renovación")
        dialogo.resizable(False, False)
        dialogo.grab_set()
        dialogo.configure(fg_color=FONDO)
        dialogo.update_idletasks()
        x = (dialogo.winfo_screenwidth()  // 2) - 310
        y = (dialogo.winfo_screenheight() // 2) - 240
        dialogo.geometry(f"620x480+{x}+{y}")

        inner = ctk.CTkFrame(dialogo, fg_color=FONDO_CARD, corner_radius=20)
        inner.pack(fill="both", expand=True, padx=16, pady=16)

        ctk.CTkLabel(
            inner, text="¿Confirmas la renovación?",
            font=fuente_titulo(), text_color=TEXTO
        ).pack(pady=(24, 16), padx=40)

        datos_frame = ctk.CTkFrame(inner, fg_color=CAMPO, corner_radius=12)
        datos_frame.pack(fill="x", padx=40, pady=(0, 16))
        datos_frame.grid_columnconfigure((0,1), weight=1)

        datos = [
            ("Clienta:", f"{self._socio['nombre']} {self._socio['apellido']}"),
            ("DNI:", self._socio["dni"]),
            ("Duración:", plan),
            ("Tipo de plan:", tipo_plan),
            ("Inicio:", formatear_fecha_legible(self._nueva_fecha_ini)),
            ("Fin:", formatear_fecha_legible(self._nueva_fecha_fin)),
        ]

        for i, (label, valor) in enumerate(datos):
            ctk.CTkLabel(
                datos_frame, text=label,
                font=fuente_label(), text_color=TEXTO_SUAVE, anchor="w"
            ).grid(row=i, column=0, sticky="w", padx=16, pady=5)
            ctk.CTkLabel(
                datos_frame, text=valor,
                font=fuente_dato(), text_color=TEXTO, anchor="w"
            ).grid(row=i, column=1, sticky="w", padx=16, pady=5)

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
                self._nueva_fecha_fin,
                self._nuevo_tipo_plan)
            self._socio["fecha_inicio"] = self._nueva_fecha_ini
            self._socio["fecha_fin"]    = self._nueva_fecha_fin
            self._socio["tipo_plan"]    = self._nuevo_tipo_plan
            self._poblar_opciones()
            self.app._actualizar_campana()
            self.label_err_mem.configure(
                text="✅ Membresía renovada correctamente.",
                text_color=EXITO)
            self.after(2000, lambda: self._mostrar_paso(2))

        ctk.CTkButton(
            btn_f, text="Cancelar", height=52,
            font=fuente_boton_sec(), fg_color=BTN_SECUNDARIO,
            hover_color="#C4A882", text_color=TEXTO,
            corner_radius=12, command=_cancelar
        ).grid(row=0, column=0, padx=(0, 8), sticky="ew")

        ctk.CTkButton(
            btn_f, text="✅  Sí, renovar", height=52,
            font=fuente_boton(), fg_color=BTN_PRINCIPAL,
            hover_color="#9DC95A", text_color=TEXTO,
            corner_radius=12, command=_guardar
        ).grid(row=0, column=1, padx=(8, 0), sticky="ew")