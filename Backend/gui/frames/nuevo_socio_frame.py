# gui/frames/nuevo_socio_frame.py
import customtkinter as ctk
from reniec_api import consultar_dni
from socio_logic import (validar_telefono, validar_dni, validar_dni_patron,
                          calcular_fecha_fin, texto_resumen, PLANES,
                          TIPOS_PLAN, fecha_registro_ahora,
                          fecha_fin_ya_vencida, formatear_fecha_legible)
from database import insertar_socio, buscar_socio_por_dni
from gui.widgets.fecha_picker import FechaPicker
from gui.tema import *

TIPOS_DOCUMENTO = ["DNI", "Carnet de extranjería", "Pasaporte", "Otro"]

class NuevoSocioFrame(ctk.CTkFrame):
    def __init__(self, contenedor, app):
        super().__init__(contenedor, fg_color=FONDO)
        self.app = app

        self._telefono       = ""
        self._dni            = ""
        self._nombre         = ""
        self._apellido       = ""
        self._plan           = ""
        self._tipo_plan      = ""
        self._tipo_documento = "DNI"
        self._fecha_ini      = ""
        self._fecha_fin      = ""

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
        self._apellido = self._plan = self._tipo_plan = ""
        self._fecha_ini = self._fecha_fin = ""
        self._tipo_documento = "DNI"

        self.entry_tel.delete(0, "end")
        self.entry_numero.delete(0, "end")
        self.tipo_doc_var.set("DNI")
        self._on_tipo_documento_cambiado()
        self.label_nombre_valor.configure(text="—")
        self.label_apellido_valor.configure(text="—")
        self.label_err_p1.configure(text="")
        self.btn_siguiente_p1.configure(state="disabled")

        self.plan_var.set("")
        self.tipo_plan_var.set("")
        self.btn_siguiente_p2.configure(state="disabled")
        self.label_err_p2.configure(text="")

        for lbl in self.labels_resumen.values():
            lbl.configure(text="—")
        self.label_err_p3.configure(text="")

    # ════════════════════════════════════════════════════════
    # PASO 1 — Documento, Teléfono y datos
    # ════════════════════════════════════════════════════════

    def _frame_paso1(self):
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
        card.grid_rowconfigure((1,2,3,4,5,6,7), weight=2)
        card.grid_rowconfigure(8, weight=1)
        card.grid_rowconfigure(9, weight=2)

        # Título
        ctk.CTkLabel(
            card, text="Datos de la nueva clienta",
            font=fuente_titulo(), text_color=TEXTO
        ).grid(row=0, column=0, columnspan=2, pady=(32, 0))

        # ── Tipo de documento y teléfono ──────────────────────
        ctk.CTkLabel(
            card, text="Tipo de documento", anchor="w",
            font=fuente_label(), text_color=TEXTO
        ).grid(row=1, column=0, sticky="w", padx=50)

        ctk.CTkLabel(
            card, text="Teléfono", anchor="w",
            font=fuente_label(), text_color=TEXTO
        ).grid(row=1, column=1, sticky="w", padx=50)

        self.tipo_doc_var = ctk.StringVar(value="DNI")
        self.combo_tipo_doc = ctk.CTkComboBox(
            card,
            values=TIPOS_DOCUMENTO,
            variable=self.tipo_doc_var,
            height=52, font=fuente_entrada(),
            fg_color=CAMPO, border_color=BTN_SECUNDARIO,
            text_color=TEXTO, button_color=BTN_SECUNDARIO,
            button_hover_color=BARRA, dropdown_font=fuente(17),
            corner_radius=10,
            command=self._on_tipo_documento_cambiado
        )
        self.combo_tipo_doc.grid(row=2, column=0, padx=50, pady=(4,8), sticky="ew")

        self.entry_tel = ctk.CTkEntry(
            card, placeholder_text="9 dígitos", height=52,
            font=fuente_entrada(), fg_color=CAMPO,
            border_color=BTN_SECUNDARIO, text_color=TEXTO,
            placeholder_text_color=TEXTO_CAMPO, corner_radius=10)
        self.entry_tel.grid(row=2, column=1, padx=50, pady=(4,8), sticky="ew")
        self.entry_tel.bind("<Return>", lambda e: "break")
        self.entry_tel.bind("<KeyRelease>", lambda e: self._verificar_campos_manual())

        # ── Número de documento ───────────────────────────────
        self.label_numero = ctk.CTkLabel(
            card, text="Número de DNI (8 dígitos)", anchor="w",
            font=fuente_label(), text_color=TEXTO)
        self.label_numero.grid(row=3, column=0, columnspan=2,
                               sticky="w", padx=50)

        self.entry_numero = ctk.CTkEntry(
            card, placeholder_text="Número de documento",
            height=52, font=fuente_entrada(), fg_color=CAMPO,
            border_color=BTN_SECUNDARIO, text_color=TEXTO,
            placeholder_text_color=TEXTO_CAMPO, corner_radius=10)
        self.entry_numero.grid(row=4, column=0, columnspan=2,
                               padx=50, pady=(4,8), sticky="ew")
        self.entry_numero.bind("<Return>", lambda e: "break")
        self.entry_numero.bind("<KeyRelease>", lambda e: self._verificar_campos_manual())

        # Separador
        ctk.CTkFrame(
            card, fg_color=CAMPO, height=2, corner_radius=2
        ).grid(row=5, column=0, columnspan=2, padx=50, sticky="ew", pady=4)

        # ── Sección DNI — resultado automático ────────────────
        self.frame_dni = ctk.CTkFrame(card, fg_color="transparent")
        self.frame_dni.grid(row=6, column=0, columnspan=2,
                            rowspan=2, padx=50, sticky="ew")
        self.frame_dni.grid_columnconfigure((0,1), weight=1)

        ctk.CTkLabel(
            self.frame_dni, text="Nombre:", anchor="w",
            font=fuente_label(), text_color=TEXTO_SUAVE
        ).grid(row=0, column=0, sticky="w")

        self.label_nombre_valor = ctk.CTkLabel(
            self.frame_dni, text="—", anchor="w",
            font=fuente_dato(), text_color=TEXTO)
        self.label_nombre_valor.grid(row=0, column=1, sticky="w", padx=10)

        ctk.CTkLabel(
            self.frame_dni, text="Apellido:", anchor="w",
            font=fuente_label(), text_color=TEXTO_SUAVE
        ).grid(row=1, column=0, sticky="w")

        self.label_apellido_valor = ctk.CTkLabel(
            self.frame_dni, text="—", anchor="w",
            font=fuente_dato(), text_color=TEXTO)
        self.label_apellido_valor.grid(row=1, column=1, sticky="w", padx=10)

        self.btn_consultar_dni = ctk.CTkButton(
            self.frame_dni, text="🔍  Consultar RENIEC", height=52,
            font=fuente_boton(), fg_color=BTN_PRINCIPAL,
            hover_color="#9DC95A", text_color=TEXTO,
            corner_radius=10, command=self._consultar_reniec)
        self.btn_consultar_dni.grid(row=2, column=0, columnspan=2,
                                    pady=(8,0), sticky="ew")

        # ── Sección manual (no DNI) ───────────────────────────
        self.frame_manual = ctk.CTkFrame(card, fg_color="transparent")
        self.frame_manual.grid(row=6, column=0, columnspan=2,
                               rowspan=2, padx=50, sticky="ew")
        self.frame_manual.grid_columnconfigure((0,1), weight=1)
        self.frame_manual.grid_remove()

        ctk.CTkLabel(
            self.frame_manual, text="Nombre:", anchor="w",
            font=fuente_label(), text_color=TEXTO_SUAVE
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            self.frame_manual, text="Apellido:", anchor="w",
            font=fuente_label(), text_color=TEXTO_SUAVE
        ).grid(row=0, column=1, sticky="w", padx=(10,0))

        self.entry_nombre_manual = ctk.CTkEntry(
            self.frame_manual, placeholder_text="Ingresa el nombre",
            height=52, font=fuente_entrada(), fg_color=CAMPO,
            border_color=BTN_SECUNDARIO, text_color=TEXTO,
            placeholder_text_color=TEXTO_CAMPO, corner_radius=10)
        self.entry_nombre_manual.grid(row=1, column=0, pady=(4,0), sticky="ew")
        self.entry_nombre_manual.bind("<Return>", lambda e: "break")
        self.entry_nombre_manual.bind("<KeyRelease>",
                                      lambda e: self._verificar_campos_manual())

        self.entry_apellido_manual = ctk.CTkEntry(
            self.frame_manual, placeholder_text="Ingresa el apellido",
            height=52, font=fuente_entrada(), fg_color=CAMPO,
            border_color=BTN_SECUNDARIO, text_color=TEXTO,
            placeholder_text_color=TEXTO_CAMPO, corner_radius=10)
        self.entry_apellido_manual.grid(row=1, column=1, padx=(10,0),
                                        pady=(4,0), sticky="ew")
        self.entry_apellido_manual.bind("<Return>", lambda e: "break")
        self.entry_apellido_manual.bind("<KeyRelease>",
                                        lambda e: self._verificar_campos_manual())

        # Error
        self.label_err_p1 = ctk.CTkLabel(
            card, text="", font=fuente_pequeña(), text_color=ERROR)
        self.label_err_p1.grid(row=8, column=0, columnspan=2)

        # Siguiente
        self.btn_siguiente_p1 = ctk.CTkButton(
            card, text="Siguiente  →", height=56,
            font=fuente_boton(), fg_color=BTN_PRINCIPAL,
            hover_color="#9DC95A", text_color=TEXTO,
            corner_radius=12, state="disabled",
            command=self._intentar_siguiente
        )
        self.btn_siguiente_p1.grid(
            row=9, column=0, columnspan=2,
            padx=50, pady=(4, 32), sticky="ew")

        return f

    def _on_tipo_documento_cambiado(self, *args):
        tipo = self.tipo_doc_var.get()
        self._tipo_documento = tipo
        self.entry_numero.delete(0, "end")
        self.label_err_p1.configure(text="")
        self.btn_siguiente_p1.configure(state="disabled")
        self._nombre = ""
        self._apellido = ""

        if tipo == "DNI":
            self.label_numero.configure(text="Número de DNI (8 dígitos)")
            self.label_nombre_valor.configure(text="—")
            self.label_apellido_valor.configure(text="—")
            self.frame_manual.grid_remove()
            self.frame_dni.grid()
        else:
            self.label_numero.configure(text="Número de documento")
            self.entry_nombre_manual.delete(0, "end")
            self.entry_apellido_manual.delete(0, "end")
            self.frame_dni.grid_remove()
            self.frame_manual.grid()

    def _verificar_campos_manual(self):
        """Para documentos no DNI activa siguiente cuando hay tel+numero+nombre+apellido."""
        if self.tipo_doc_var.get() == "DNI":
            return
        tel      = self.entry_tel.get().strip()
        numero   = self.entry_numero.get().strip()
        nombre   = self.entry_nombre_manual.get().strip()
        apellido = self.entry_apellido_manual.get().strip()

        if tel and numero and nombre and apellido:
            self.btn_siguiente_p1.configure(state="normal")
            self.label_err_p1.configure(text="")
        else:
            self.btn_siguiente_p1.configure(state="disabled")

    def _intentar_siguiente(self):
        """Valida antes de pasar al paso 2."""
        tipo = self.tipo_doc_var.get()

        if tipo == "DNI":
            # Para DNI el siguiente solo se activa tras consultar RENIEC
            self._mostrar_paso(2)
        else:
            # Para otros documentos validar teléfono y registrar datos
            tel      = self.entry_tel.get().strip()
            numero   = self.entry_numero.get().strip()
            nombre   = self.entry_nombre_manual.get().strip()
            apellido = self.entry_apellido_manual.get().strip()

            if not validar_telefono(tel):
                self._set_error_p1("⚠ El teléfono debe tener 9 dígitos numéricos")
                self.btn_siguiente_p1.configure(state="disabled")
                return
            if buscar_socio_por_dni(numero):
                self._set_error_p1("⚠ Este documento ya está registrado")
                self.btn_siguiente_p1.configure(state="disabled")
                return

            self._telefono = tel
            self._dni      = numero
            self._nombre   = nombre.title()
            self._apellido = apellido.title()
            self._mostrar_paso(2)

    def _consultar_reniec(self):
        tel    = self.entry_tel.get().strip()
        numero = self.entry_numero.get().strip()

        if not validar_telefono(tel):
            self._set_error_p1("⚠ El teléfono debe tener 9 dígitos numéricos")
            return
        if not validar_dni(numero):
            self._set_error_p1("⚠ El DNI debe tener 8 dígitos numéricos")
            return
        if not validar_dni_patron(numero):
            self._set_error_p1("⚠ El DNI ingresado no es válido")
            return
        if buscar_socio_por_dni(numero):
            self._set_error_p1("⚠ Este DNI ya está registrado en el sistema")
            return

        self.label_err_p1.configure(
            text="Consultando...", text_color=TEXTO_SUAVE)
        self.update()

        resultado = consultar_dni(numero)

        if resultado["ok"]:
            self._telefono = tel
            self._dni      = numero
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
    # PASO 2 — Selección de plan y tipo de plan
    # ════════════════════════════════════════════════════════

    def _frame_paso2(self):
        f = ctk.CTkFrame(self, fg_color=FONDO)
        f.grid_rowconfigure(0, weight=1)
        f.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(
            f, fg_color=FONDO_CARD,
            corner_radius=24, width=820, height=640)
        card.grid(row=0, column=0, padx=20, pady=20)
        card.grid_propagate(False)
        card.grid_columnconfigure((0, 1), weight=1)
        card.grid_rowconfigure(0, weight=2)
        card.grid_rowconfigure(1, weight=1)
        card.grid_rowconfigure((2,3,4,5), weight=2)
        card.grid_rowconfigure(6, weight=1)
        card.grid_rowconfigure(7, weight=2)

        ctk.CTkLabel(
            card, text="Selecciona el plan",
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

        self.plan_var = ctk.StringVar(value="")
        for i, plan in enumerate(PLANES.keys()):
            ctk.CTkRadioButton(
                card, text=plan,
                variable=self.plan_var, value=plan,
                font=fuente_dato(), text_color=TEXTO,
                fg_color=BTN_PRINCIPAL, hover_color="#9DC95A",
                radiobutton_width=24, radiobutton_height=24,
                command=self._on_seleccion_cambiada
            ).grid(row=2+i, column=0, sticky="w", padx=80, pady=6)

        self.tipo_plan_var = ctk.StringVar(value="")
        for i, tipo in enumerate(TIPOS_PLAN):
            ctk.CTkRadioButton(
                card, text=tipo,
                variable=self.tipo_plan_var, value=tipo,
                font=fuente_dato(), text_color=TEXTO,
                fg_color=BTN_PRINCIPAL, hover_color="#9DC95A",
                radiobutton_width=24, radiobutton_height=24,
                command=self._on_seleccion_cambiada
            ).grid(row=2+i, column=1, sticky="w", padx=80, pady=6)

        self.label_err_p2 = ctk.CTkLabel(
            card, text="", font=fuente_pequeña(), text_color=ERROR)
        self.label_err_p2.grid(row=6, column=0, columnspan=2)

        nav = ctk.CTkFrame(card, fg_color="transparent")
        nav.grid(row=7, column=0, columnspan=2,
                 padx=50, pady=(4, 32), sticky="ew")
        nav.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            nav, text="←  Volver", height=56,
            font=fuente_boton_sec(), fg_color=BTN_SECUNDARIO,
            hover_color="#C4A882", text_color=TEXTO,
            corner_radius=12,
            command=lambda: self._mostrar_paso(1)
        ).grid(row=0, column=0, padx=(0, 8), sticky="ew")

        self.btn_siguiente_p2 = ctk.CTkButton(
            nav, text="Siguiente  →", height=56,
            font=fuente_boton(), fg_color=BTN_PRINCIPAL,
            hover_color="#9DC95A", text_color=TEXTO,
            corner_radius=12, state="disabled",
            command=self._ir_paso3
        )
        self.btn_siguiente_p2.grid(row=0, column=1, padx=(8, 0), sticky="ew")

        return f

    def _on_seleccion_cambiada(self):
        if self.plan_var.get() and self.tipo_plan_var.get():
            self.btn_siguiente_p2.configure(state="normal")
            self.label_err_p2.configure(text="")
        else:
            self.btn_siguiente_p2.configure(state="disabled")
        if self._nombre:
            self._actualizar_resumen()

    # ════════════════════════════════════════════════════════
    # PASO 3 — Confirmar fecha y resumen automático
    # ════════════════════════════════════════════════════════

    def _frame_paso3(self):
        f = ctk.CTkFrame(self, fg_color=FONDO)
        f.grid_rowconfigure(0, weight=1)
        f.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(
            f, fg_color=FONDO_CARD,
            corner_radius=24, width=820, height=680)
        card.grid(row=0, column=0, padx=20, pady=20)
        card.grid_propagate(False)
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(0, weight=2)
        card.grid_rowconfigure(1, weight=1)
        card.grid_rowconfigure(2, weight=1)
        card.grid_rowconfigure(3, weight=3)
        card.grid_rowconfigure(4, weight=1)
        card.grid_rowconfigure(5, weight=2)

        ctk.CTkLabel(
            card, text="Confirmar e inscribir",
            font=fuente_titulo(), text_color=TEXTO
        ).grid(row=0, column=0, pady=(32, 0))

        ctk.CTkLabel(
            card, text="Fecha de inicio de membresía:",
            font=fuente_label(), text_color=TEXTO_SUAVE, anchor="w"
        ).grid(row=1, column=0, padx=70, sticky="w")

        self.fecha_picker = FechaPicker(card,
                                        on_change=self._actualizar_resumen)
        self.fecha_picker.grid(row=2, column=0, padx=70, pady=(4, 8), sticky="w")

        # Resumen
        self.label_resumen = ctk.CTkFrame(
            card, fg_color=CAMPO, corner_radius=12)
        self.label_resumen.grid(row=3, column=0, padx=70, pady=(0, 4), sticky="ew")
        self.label_resumen.grid_columnconfigure((0,1), weight=1)

        campos_resumen = ["Nombre:", "Tipo de documento:",
                          "Número:", "Duración:",
                          "Tipo de plan:", "Inicio:", "Fin:"]
        self.labels_resumen = {}
        for i, campo in enumerate(campos_resumen):
            ctk.CTkLabel(
                self.label_resumen, text=campo,
                font=fuente_label(), text_color=TEXTO_SUAVE, anchor="w"
            ).grid(row=i, column=0, sticky="w", padx=16, pady=4)

            lbl = ctk.CTkLabel(
                self.label_resumen, text="—",
                font=fuente_dato(), text_color=TEXTO, anchor="w")
            lbl.grid(row=i, column=1, sticky="w", padx=16, pady=4)
            self.labels_resumen[campo] = lbl

        self.label_err_p3 = ctk.CTkLabel(
            card, text="",
            font=fuente_pequeña(), wraplength=660)
        self.label_err_p3.grid(row=4, column=0, padx=70)

        nav = ctk.CTkFrame(card, fg_color="transparent")
        nav.grid(row=5, column=0, padx=70, pady=(4, 32), sticky="ew")
        nav.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            nav, text="←  Volver", height=56,
            font=fuente_boton_sec(), fg_color=BTN_SECUNDARIO,
            hover_color="#C4A882", text_color=TEXTO,
            corner_radius=12,
            command=lambda: self._mostrar_paso(2)
        ).grid(row=0, column=0, padx=(0, 8), sticky="ew")

        ctk.CTkButton(
            nav, text="✅  Confirmar e inscribir", height=56,
            font=fuente_boton(), fg_color=BTN_PRINCIPAL,
            hover_color="#9DC95A", text_color=TEXTO,
            corner_radius=12, command=self._confirmar_inscripcion
        ).grid(row=0, column=1, padx=(8, 0), sticky="ew")

        return f

    def _ir_paso3(self):
        self._plan      = self.plan_var.get()
        self._tipo_plan = self.tipo_plan_var.get()
        self.label_err_p3.configure(text="")
        self._actualizar_resumen()
        self._mostrar_paso(3)

    def _actualizar_resumen(self, *args):
        if not self._nombre or not self._plan or not self._tipo_plan:
            return

        self._fecha_ini = self.fecha_picker.get_fecha()
        self._fecha_fin = calcular_fecha_fin(self._fecha_ini, self._plan)

        if fecha_fin_ya_vencida(self._fecha_fin):
            self._fecha_ini = ""
            self._fecha_fin = ""
            for lbl in self.labels_resumen.values():
                lbl.configure(text="—")
            self.label_err_p3.configure(
                text="⚠ La membresía con esa fecha de inicio ya estaría vencida. "
                     "Selecciona una fecha más reciente.",
                text_color=ERROR)
            return

        self.label_err_p3.configure(text="")
        self.labels_resumen["Nombre:"].configure(
            text=f"{self._nombre} {self._apellido}")
        self.labels_resumen["Tipo de documento:"].configure(
            text=self._tipo_documento)
        self.labels_resumen["Número:"].configure(text=self._dni)
        self.labels_resumen["Duración:"].configure(text=self._plan)
        self.labels_resumen["Tipo de plan:"].configure(text=self._tipo_plan)
        self.labels_resumen["Inicio:"].configure(
            text=formatear_fecha_legible(self._fecha_ini))
        self.labels_resumen["Fin:"].configure(
            text=formatear_fecha_legible(self._fecha_fin))

    def _confirmar_inscripcion(self):
        if not self._fecha_ini:
            self.label_err_p3.configure(
                text="⚠ Selecciona una fecha de inicio válida",
                text_color=ERROR)
            return

        dialogo = ctk.CTkToplevel(self)
        dialogo.title("Confirmar inscripción")
        dialogo.resizable(False, False)
        dialogo.grab_set()
        dialogo.configure(fg_color=FONDO)
        dialogo.update_idletasks()
        x = (dialogo.winfo_screenwidth()  // 2) - 310
        y = (dialogo.winfo_screenheight() // 2) - 270
        dialogo.geometry(f"620x540+{x}+{y}")

        inner = ctk.CTkFrame(dialogo, fg_color=FONDO_CARD, corner_radius=20)
        inner.pack(fill="both", expand=True, padx=16, pady=16)

        ctk.CTkLabel(
            inner, text="¿Confirmas la inscripción?",
            font=fuente_titulo(), text_color=TEXTO
        ).pack(pady=(28, 16), padx=40)

        datos_frame = ctk.CTkFrame(inner, fg_color=CAMPO, corner_radius=12)
        datos_frame.pack(fill="x", padx=40, pady=(0, 16))
        datos_frame.grid_columnconfigure((0,1), weight=1)

        datos = [
            ("Clienta:",           f"{self._nombre} {self._apellido}"),
            ("Tipo de documento:", self._tipo_documento),
            ("Número:",            self._dni),
            ("Duración:",          self._plan),
            ("Tipo de plan:",      self._tipo_plan),
            ("Inicio:",            formatear_fecha_legible(self._fecha_ini)),
            ("Fin:",               formatear_fecha_legible(self._fecha_fin)),
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
            try:
                insertar_socio(
                    dni            = self._dni,
                    nombre         = self._nombre,
                    apellido       = self._apellido,
                    telefono       = self._telefono,
                    fecha_inicio   = self._fecha_ini,
                    fecha_fin      = self._fecha_fin,
                    fecha_registro = fecha_registro_ahora(),
                    tipo_plan      = self._tipo_plan,
                    tipo_documento = self._tipo_documento
                )
                self.label_err_p3.configure(
                    text=f"✅ {self._nombre} {self._apellido} inscrita correctamente.",
                    text_color=EXITO)
                self.app._actualizar_campana()
                self.after(2000, lambda: self.app.mostrar_frame("menu"))
            except Exception as e:
                self.label_err_p3.configure(
                    text=f"⚠ Error al guardar: {str(e)}", text_color=ERROR)

        ctk.CTkButton(
            btn_f, text="Cancelar", height=52,
            font=fuente_boton_sec(), fg_color=BTN_SECUNDARIO,
            hover_color="#C4A882", text_color=TEXTO,
            corner_radius=12, command=_cancelar
        ).grid(row=0, column=0, padx=(0, 8), sticky="ew")

        ctk.CTkButton(
            btn_f, text="✅  Sí, inscribir", height=52,
            font=fuente_boton(), fg_color=BTN_PRINCIPAL,
            hover_color="#9DC95A", text_color=TEXTO,
            corner_radius=12, command=_guardar
        ).grid(row=0, column=1, padx=(8, 0), sticky="ew")