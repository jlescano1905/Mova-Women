# gui/frames/nuevo_socio_frame.py
import customtkinter as ctk
from reniec_api import consultar_dni
from socio_logic import (validar_telefono, validar_dni, calcular_fecha_fin,
                          texto_resumen, PLANES, fecha_registro_ahora,
                          fecha_fin_ya_vencida, formatear_fecha_legible)
from database import insertar_socio, buscar_socio_por_dni
from gui.widgets.fecha_picker import FechaPicker
from gui.tema import *

class NuevoSocioFrame(ctk.CTkFrame):
    def __init__(self, contenedor, app):
        super().__init__(contenedor, fg_color=FONDO)
        self.app = app

        self._telefono  = ""
        self._dni       = ""
        self._nombre    = ""
        self._apellido  = ""
        self._plan      = ""
        self._fecha_ini = ""
        self._fecha_fin = ""

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._construir_pasos()

    def on_show(self):
        self._resetear()
        self._mostrar_paso(1)

    # ── Pasos ────────────────────────────────────────────────

    def _construir_pasos(self):
        self.paso1 = self._frame_paso1()
        self.paso2 = self._frame_paso2()
        self.paso3 = self._frame_paso3()
        for f in (self.paso1, self.paso2, self.paso3):
            f.grid(row=0, column=0, sticky="nsew")

    def _mostrar_paso(self, n):
        {1: self.paso1, 2: self.paso2, 3: self.paso3}[n].tkraise()

    def _resetear(self):
        self._telefono = self._dni = self._nombre = ""
        self._apellido = self._plan = self._fecha_ini = self._fecha_fin = ""

        self.entry_tel.delete(0, "end")
        self.entry_dni.delete(0, "end")
        self.label_nombre_valor.configure(text="—")
        self.label_apellido_valor.configure(text="—")
        self.label_err_p1.configure(text="")
        self.btn_siguiente_p1.configure(state="disabled")

        self.plan_var.set("")
        self.btn_siguiente_p2.configure(state="disabled")
        self.label_err_p2.configure(text="")

        self.label_resumen.configure(text="")
        self.label_err_p3.configure(text="")

    # ════════════════════════════════════════════════════════
    # PASO 1 — Teléfono, DNI y consulta RENIEC
    # ════════════════════════════════════════════════════════

    def _frame_paso1(self):
        f = ctk.CTkFrame(self, fg_color=FONDO)
        f.grid_rowconfigure(0, weight=1)
        f.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(
            f, fg_color=FONDO_CARD,
            corner_radius=20, width=680, height=540)
        card.grid(row=0, column=0, padx=20, pady=20)
        card.grid_propagate(False)
        card.grid_columnconfigure((0, 1), weight=1)
        card.grid_rowconfigure(0, weight=1)
        card.grid_rowconfigure((1,2,3,4,5,6,7), weight=2)
        card.grid_rowconfigure(8, weight=1)

        ctk.CTkLabel(
            card, text="Datos de la nueva cliente",
            font=fuente_titulo(), text_color=TEXTO
        ).grid(row=0, column=0, columnspan=2, pady=(30, 0))

        # Teléfono
        ctk.CTkLabel(
            card, text="Teléfono", anchor="w",
            font=fuente_label(), text_color=TEXTO
        ).grid(row=1, column=0, sticky="w", padx=40)

        self.entry_tel = ctk.CTkEntry(
            card, placeholder_text="9 dígitos", height=46,
            font=fuente_entrada(), fg_color=CAMPO,
            border_color=BTN_SECUNDARIO, text_color=TEXTO,
            placeholder_text_color=TEXTO_CAMPO, corner_radius=10)
        self.entry_tel.grid(row=2, column=0, padx=40, pady=(4,16), sticky="ew")
        self.entry_tel.bind("<Return>", lambda e: "break")

        # DNI
        ctk.CTkLabel(
            card, text="DNI", anchor="w",
            font=fuente_label(), text_color=TEXTO
        ).grid(row=1, column=1, sticky="w", padx=40)

        self.entry_dni = ctk.CTkEntry(
            card, placeholder_text="8 dígitos", height=46,
            font=fuente_entrada(), fg_color=CAMPO,
            border_color=BTN_SECUNDARIO, text_color=TEXTO,
            placeholder_text_color=TEXTO_CAMPO, corner_radius=10)
        self.entry_dni.grid(row=2, column=1, padx=40, pady=(4,16), sticky="ew")
        self.entry_dni.bind("<Return>", lambda e: "break")

        # Botón consultar
        ctk.CTkButton(
            card, text="🔍  Consultar DNI", height=46,
            font=fuente_boton(), fg_color=BTN_PRINCIPAL,
            hover_color="#9DC95A", text_color=TEXTO,
            corner_radius=10, command=self._consultar_reniec
        ).grid(row=3, column=0, columnspan=2, padx=40, pady=(0,16), sticky="ew")

        # Separador visual
        sep = ctk.CTkFrame(card, fg_color=CAMPO, height=2, corner_radius=2)
        sep.grid(row=4, column=0, columnspan=2, padx=40, sticky="ew")

        # Resultado RENIEC
        ctk.CTkLabel(
            card, text="Nombre:", anchor="w",
            font=fuente_label(), text_color=TEXTO_SUAVE
        ).grid(row=5, column=0, sticky="w", padx=40)

        self.label_nombre_valor = ctk.CTkLabel(
            card, text="—", anchor="w",
            font=fuente(15, "bold"), text_color=TEXTO)
        self.label_nombre_valor.grid(row=5, column=1, sticky="w", padx=40)

        ctk.CTkLabel(
            card, text="Apellido:", anchor="w",
            font=fuente_label(), text_color=TEXTO_SUAVE
        ).grid(row=6, column=0, sticky="w", padx=40)

        self.label_apellido_valor = ctk.CTkLabel(
            card, text="—", anchor="w",
            font=fuente(15, "bold"), text_color=TEXTO)
        self.label_apellido_valor.grid(row=6, column=1, sticky="w", padx=40)

        # Error
        self.label_err_p1 = ctk.CTkLabel(
            card, text="", font=fuente_pequeña(), text_color=ERROR)
        self.label_err_p1.grid(row=7, column=0, columnspan=2)

        # Siguiente
        self.btn_siguiente_p1 = ctk.CTkButton(
            card, text="Siguiente  →", height=50,
            font=fuente_boton(), fg_color=BTN_PRINCIPAL,
            hover_color="#9DC95A", text_color=TEXTO,
            corner_radius=12, state="disabled",
            command=lambda: self._mostrar_paso(2)
        )
        self.btn_siguiente_p1.grid(
            row=8, column=0, columnspan=2,
            padx=40, pady=(8, 30), sticky="ew")

        return f

    def _consultar_reniec(self):
        tel = self.entry_tel.get().strip()
        dni = self.entry_dni.get().strip()

        if not validar_telefono(tel):
            self._set_error_p1("⚠ El teléfono debe tener 9 dígitos numéricos")
            return
        if not validar_dni(dni):
            self._set_error_p1("⚠ El DNI debe tener 8 dígitos numéricos")
            return
        if buscar_socio_por_dni(dni):
            self._set_error_p1("⚠ Este DNI ya está registrado en el sistema")
            return

        self.label_err_p1.configure(
            text="Consultando...", text_color=TEXTO_SUAVE)
        self.update()

        resultado = consultar_dni(dni)

        if resultado["ok"]:
            self._telefono = tel
            self._dni      = dni
            self._nombre   = resultado["nombre"]
            self._apellido = resultado["apellido"]
            self.label_nombre_valor.configure(text=self._nombre)
            self.label_apellido_valor.configure(text=self._apellido)
            self.label_err_p1.configure(
                text="✅ DNI verificado", text_color=EXITO)
            self.btn_siguiente_p1.configure(state="normal")
        else:
            self._set_error_p1(f"⚠ {resultado['mensaje']}")
            self.label_nombre_valor.configure(text="—")
            self.label_apellido_valor.configure(text="—")
            self.btn_siguiente_p1.configure(state="disabled")

    def _set_error_p1(self, msg):
        self.label_err_p1.configure(text=msg, text_color=ERROR)

    # ════════════════════════════════════════════════════════
    # PASO 2 — Selección de plan
    # ════════════════════════════════════════════════════════

    def _frame_paso2(self):
        f = ctk.CTkFrame(self, fg_color=FONDO)
        f.grid_rowconfigure(0, weight=1)
        f.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(
            f, fg_color=FONDO_CARD,
            corner_radius=20, width=620, height=500)
        card.grid(row=0, column=0, padx=20, pady=20)
        card.grid_propagate(False)
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(0, weight=1)
        card.grid_rowconfigure((1,2,3,4,5), weight=2)
        card.grid_rowconfigure(6, weight=1)

        ctk.CTkLabel(
            card, text="Selecciona el plan",
            font=fuente_titulo(), text_color=TEXTO
        ).grid(row=0, column=0, pady=(30, 0))

        self.plan_var = ctk.StringVar(value="")

        for i, plan in enumerate(PLANES.keys(), start=1):
            ctk.CTkRadioButton(
                card, text=plan,
                variable=self.plan_var, value=plan,
                font=fuente(16),
                text_color=TEXTO,
                fg_color=BTN_PRINCIPAL,
                hover_color="#9DC95A",
                command=self._on_plan_seleccionado
            ).grid(row=i, column=0, sticky="w", padx=100, pady=6)

        self.label_err_p2 = ctk.CTkLabel(
            card, text="", font=fuente_pequeña(), text_color=ERROR)
        self.label_err_p2.grid(row=6, column=0)

        nav = ctk.CTkFrame(card, fg_color="transparent")
        nav.grid(row=7, column=0, padx=40, pady=(8, 30), sticky="ew")
        nav.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            nav, text="←  Volver", height=50,
            font=fuente_boton(), fg_color=BTN_SECUNDARIO,
            hover_color="#C4A882", text_color=TEXTO,
            corner_radius=12,
            command=lambda: self._mostrar_paso(1)
        ).grid(row=0, column=0, padx=(0, 8), sticky="ew")

        self.btn_siguiente_p2 = ctk.CTkButton(
            nav, text="Siguiente  →", height=50,
            font=fuente_boton(), fg_color=BTN_PRINCIPAL,
            hover_color="#9DC95A", text_color=TEXTO,
            corner_radius=12, state="disabled",
            command=self._ir_paso3
        )
        self.btn_siguiente_p2.grid(row=0, column=1, padx=(8, 0), sticky="ew")

        return f

    def _on_plan_seleccionado(self):
        self.btn_siguiente_p2.configure(state="normal")
        self.label_err_p2.configure(text="")

    # ════════════════════════════════════════════════════════
    # PASO 3 — Confirmar fecha y resumen
    # ════════════════════════════════════════════════════════

    def _frame_paso3(self):
        f = ctk.CTkFrame(self, fg_color=FONDO)
        f.grid_rowconfigure(0, weight=1)
        f.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(
            f, fg_color=FONDO_CARD,
            corner_radius=20, width=660, height=520)
        card.grid(row=0, column=0, padx=20, pady=20)
        card.grid_propagate(False)
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(0, weight=1)
        card.grid_rowconfigure((1,2,3,4,5), weight=2)
        card.grid_rowconfigure(6, weight=1)

        ctk.CTkLabel(
            card, text="Confirmar e inscribir",
            font=fuente_titulo(), text_color=TEXTO
        ).grid(row=0, column=0, pady=(30, 0))

        ctk.CTkLabel(
            card, text="Fecha de inicio de membresía:",
            font=fuente_label(), text_color=TEXTO_SUAVE
        ).grid(row=1, column=0, padx=60, sticky="w")

        self.fecha_picker = FechaPicker(card)
        self.fecha_picker.grid(row=2, column=0, padx=60, pady=(8,8), sticky="w")

        ctk.CTkButton(
            card, text="👁  Ver resumen", height=46,
            font=fuente_boton(), fg_color=BTN_SECUNDARIO,
            hover_color="#C4A882", text_color=TEXTO,
            corner_radius=12, command=self._actualizar_resumen
        ).grid(row=3, column=0, padx=60, pady=(0, 8), sticky="ew")

        self.label_resumen = ctk.CTkLabel(
            card, text="",
            font=fuente(14), text_color=TEXTO,
            wraplength=520, justify="left")
        self.label_resumen.grid(row=4, column=0, padx=60, pady=(0, 4))

        self.label_err_p3 = ctk.CTkLabel(
            card, text="",
            font=fuente_pequeña(), wraplength=520)
        self.label_err_p3.grid(row=5, column=0, padx=60)

        nav = ctk.CTkFrame(card, fg_color="transparent")
        nav.grid(row=6, column=0, padx=60, pady=(8, 30), sticky="ew")
        nav.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            nav, text="←  Volver", height=50,
            font=fuente_boton(), fg_color=BTN_SECUNDARIO,
            hover_color="#C4A882", text_color=TEXTO,
            corner_radius=12,
            command=lambda: self._mostrar_paso(2)
        ).grid(row=0, column=0, padx=(0, 8), sticky="ew")

        ctk.CTkButton(
            nav, text="✅  Confirmar e inscribir", height=50,
            font=fuente_boton(), fg_color=BTN_PRINCIPAL,
            hover_color="#9DC95A", text_color=TEXTO,
            corner_radius=12, command=self._confirmar_inscripcion
        ).grid(row=0, column=1, padx=(8, 0), sticky="ew")

        return f

    def _ir_paso3(self):
        self._plan = self.plan_var.get()
        self.label_resumen.configure(text="")
        self.label_err_p3.configure(text="")
        self._mostrar_paso(3)

    def _actualizar_resumen(self):
        self._fecha_ini = self.fecha_picker.get_fecha()
        self._fecha_fin = calcular_fecha_fin(self._fecha_ini, self._plan)

        if fecha_fin_ya_vencida(self._fecha_fin):
            self._fecha_ini = ""
            self._fecha_fin = ""
            self.label_resumen.configure(text="")
            self.label_err_p3.configure(
                text="⚠ La membresía con esa fecha de inicio ya estaría vencida.\n"
                     "Selecciona una fecha de inicio más reciente.",
                text_color=ERROR)
            return

        self.label_err_p3.configure(text="")
        self.label_resumen.configure(
            text=texto_resumen(
                self._nombre, self._apellido, self._dni,
                self._plan, self._fecha_ini, self._fecha_fin),
            text_color=TEXTO)

    def _confirmar_inscripcion(self):
        if not self._fecha_ini:
            self.label_err_p3.configure(
                text="⚠ Primero haz clic en 'Ver resumen'",
                text_color=ERROR)
            return

        dialogo = ctk.CTkToplevel(self)
        dialogo.title("Confirmar inscripción")
        dialogo.resizable(False, False)
        dialogo.grab_set()
        dialogo.configure(fg_color=FONDO)
        dialogo.update_idletasks()
        x = (dialogo.winfo_screenwidth()  // 2) - 260
        y = (dialogo.winfo_screenheight() // 2) - 120
        dialogo.geometry(f"520x240+{x}+{y}")

        inner = ctk.CTkFrame(dialogo, fg_color=FONDO_CARD, corner_radius=16)
        inner.pack(fill="both", expand=True, padx=16, pady=16)

        ctk.CTkLabel(
            inner,
            text="¿Confirmas la siguiente inscripción?",
            font=fuente(17, "bold"), text_color=TEXTO
        ).pack(pady=(24, 8), padx=30)

        ctk.CTkLabel(
            inner,
            text=(f"{self._nombre} {self._apellido}  |  DNI: {self._dni}\n"
                  f"Plan: {self._plan}  |  "
                  f"{formatear_fecha_legible(self._fecha_ini)} → "
                  f"{formatear_fecha_legible(self._fecha_fin)}"),
            font=fuente(13), text_color=TEXTO_SUAVE
        ).pack(pady=(0, 20), padx=30)

        btn_f = ctk.CTkFrame(inner, fg_color="transparent")
        btn_f.pack(fill="x", padx=30, pady=(0, 20))
        btn_f.grid_columnconfigure((0, 1), weight=1)

        def _cancelar():
            dialogo.destroy()

        def _guardar():
            dialogo.destroy()
            try:
                insertar_socio(
                    dni            = self._dni,
                    nombre         = self._nombre,
                    apellido       = self._apellido,
                    telefono       = self._telefono,
                    fecha_inicio   = self._fecha_ini,
                    fecha_fin      = self._fecha_fin,
                    fecha_registro = fecha_registro_ahora()
                )
                self.label_err_p3.configure(
                    text=f"✅ {self._nombre} {self._apellido} inscrito correctamente.",
                    text_color=EXITO)
                self.app._actualizar_campana()
                self.after(2000, lambda: self.app.mostrar_frame("menu"))
            except Exception as e:
                self.label_err_p3.configure(
                    text=f"⚠ Error al guardar: {str(e)}", text_color=ERROR)

        ctk.CTkButton(
            btn_f, text="Cancelar", height=44,
            font=fuente_boton(), fg_color=BTN_SECUNDARIO,
            hover_color="#C4A882", text_color=TEXTO,
            corner_radius=10, command=_cancelar
        ).grid(row=0, column=0, padx=(0, 8), sticky="ew")

        ctk.CTkButton(
            btn_f, text="✅  Sí, inscribir", height=44,
            font=fuente_boton(), fg_color=BTN_PRINCIPAL,
            hover_color="#9DC95A", text_color=TEXTO,
            corner_radius=10, command=_guardar
        ).grid(row=0, column=1, padx=(8, 0), sticky="ew")