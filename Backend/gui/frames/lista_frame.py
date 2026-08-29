# gui/frames/lista_frame.py
import customtkinter as ctk
import threading
from datetime import date
from database import listar_socios, buscar_socio_por_dni
from socio_logic import formatear_fecha_legible, formato_tipo_plan, TIPOS_PLAN, fecha_fin_ya_vencida
from gui.tema import *

class ListaFrame(ctk.CTkFrame):
    def __init__(self, contenedor, app):
        super().__init__(contenedor, fg_color=FONDO)
        self.app = app
        self._todos          = []
        self._filtrados      = []
        self._planes_activos = set()
        self._pagina_actual  = 0
        self._por_pagina     = 20

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._construir_ui()

    def on_show(self):
        self._mostrar_cargando()
        threading.Thread(target=self._cargar_socios, daemon=True).start()

    def _construir_ui(self):
        outer = ctk.CTkFrame(self, fg_color=FONDO_CARD, corner_radius=24)
        outer.grid(row=0, column=0, sticky="nsew", padx=40, pady=30)
        outer.grid_rowconfigure(3, weight=1)
        outer.grid_rowconfigure(4, weight=0)
        outer.grid_columnconfigure(0, weight=1)

        # ── Encabezado ───────────────────────────────────────
        encabezado = ctk.CTkFrame(outer, fg_color="transparent")
        encabezado.grid(row=0, column=0, sticky="ew", padx=50, pady=(28, 0))
        encabezado.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            encabezado,
            text="Lista de clientas",
            font=fuente_titulo(), text_color=TEXTO, anchor="w"
        ).grid(row=0, column=0, sticky="w")

        self.label_contador = ctk.CTkLabel(
            encabezado, text="",
            font=fuente_secundaria(), text_color=TEXTO_SUAVE, anchor="w"
        )
        self.label_contador.grid(row=1, column=0, sticky="w", pady=(2, 0))

        self.label_filtro_activo = ctk.CTkLabel(
            encabezado, text="",
            font=fuente(15), text_color=ADVERTENCIA, anchor="w"
        )
        self.label_filtro_activo.grid(row=2, column=0, sticky="w", pady=(2, 0))

        # ── Barra búsqueda ───────────────────────────────────
        barra = ctk.CTkFrame(outer, fg_color=CAMPO, corner_radius=14)
        barra.grid(row=1, column=0, sticky="ew", padx=50, pady=(16, 16))
        barra.grid_columnconfigure(0, weight=0)
        barra.grid_columnconfigure(1, weight=1)
        barra.grid_columnconfigure(2, weight=0)

        # Grupo izquierdo
        izq = ctk.CTkFrame(barra, fg_color="transparent")
        izq.grid(row=0, column=0, sticky="w", padx=(12, 0), pady=10)

        ctk.CTkLabel(
            izq, text="Buscar por número:",
            font=fuente_label(), text_color=TEXTO
        ).grid(row=0, column=0, padx=(8, 8))

        self.entry_buscar = ctk.CTkEntry(
            izq,
            placeholder_text="Número de documento",
            height=46, font=fuente_entrada(),
            fg_color=FONDO_CARD,
            border_color=BTN_SECUNDARIO,
            text_color=TEXTO,
            placeholder_text_color=TEXTO_CAMPO,
            corner_radius=10,
            width=220
        )
        self.entry_buscar.grid(row=0, column=1, padx=(0, 8))
        self.entry_buscar.bind("<Return>", lambda e: "break")

        ctk.CTkButton(
            izq, text="Buscar", width=110, height=46,
            font=fuente_boton(), fg_color=BTN_PRINCIPAL,
            hover_color="#9DC95A", text_color=TEXTO,
            corner_radius=10, command=self._filtrar
        ).grid(row=0, column=2)

        # Grupo derecho
        der = ctk.CTkFrame(barra, fg_color="transparent")
        der.grid(row=0, column=2, sticky="e", padx=(0, 12), pady=10)

        self.btn_filtro_plan = ctk.CTkButton(
            der, text="🔽  Filtrar por plan", width=180, height=46,
            font=fuente_boton_sec(), fg_color=BTN_SECUNDARIO,
            hover_color="#C4A882", text_color=TEXTO,
            corner_radius=10, command=self._abrir_popup_plan
        )
        self.btn_filtro_plan.grid(row=0, column=0, padx=(0, 8))

        ctk.CTkButton(
            der, text="Ver todas", width=120, height=46,
            font=fuente_boton_sec(), fg_color=BTN_SECUNDARIO,
            hover_color="#C4A882", text_color=TEXTO,
            corner_radius=10, command=self._limpiar_filtros
        ).grid(row=0, column=1)

        # ── Cabecera tabla ───────────────────────────────────
        cabecera = ctk.CTkFrame(
            outer, fg_color=BARRA, corner_radius=12)
        cabecera.grid(row=2, column=0, sticky="ew", padx=50, pady=(0, 4))
        cabecera.grid_columnconfigure((0,1,2,3,4,5), weight=1)

        for col, texto in enumerate([
                "Tipo doc.", "Número", "Nombre completo",
                "Tipo de plan", "Inicio", "Fin"]):
            ctk.CTkLabel(
                cabecera, text=texto,
                font=fuente_seccion(),
                text_color="white", anchor="center"
            ).grid(row=0, column=col, padx=10, pady=14, sticky="ew")

        # ── Scroll ───────────────────────────────────────────
        self.scroll = ctk.CTkScrollableFrame(
            outer, fg_color="transparent",
            scrollbar_button_color=BTN_SECUNDARIO,
            scrollbar_button_hover_color=BARRA)
        self.scroll.grid(
            row=3, column=0, sticky="nsew", padx=50, pady=(0, 4))
        self.scroll.grid_columnconfigure((0,1,2,3,4,5), weight=1)

        # ── Paginación ───────────────────────────────────────
        self.frame_pag = ctk.CTkFrame(outer, fg_color="transparent")
        self.frame_pag.grid(row=4, column=0, pady=(4, 20))

        self.btn_anterior = ctk.CTkButton(
            self.frame_pag, text="← Anterior", width=120, height=38,
            font=fuente_boton_sec(), fg_color=BTN_SECUNDARIO,
            hover_color="#C4A882", text_color=TEXTO,
            corner_radius=10, command=self._pagina_anterior
        )
        self.btn_anterior.grid(row=0, column=0, padx=8)

        self.label_pagina = ctk.CTkLabel(
            self.frame_pag, text="",
            font=fuente_dato(), text_color=TEXTO_SUAVE)
        self.label_pagina.grid(row=0, column=1, padx=16)

        self.btn_siguiente = ctk.CTkButton(
            self.frame_pag, text="Siguiente →", width=120, height=38,
            font=fuente_boton_sec(), fg_color=BTN_SECUNDARIO,
            hover_color="#C4A882", text_color=TEXTO,
            corner_radius=10, command=self._pagina_siguiente
        )
        self.btn_siguiente.grid(row=0, column=2, padx=8)

    # ── Datos ────────────────────────────────────────────────

    def _mostrar_cargando(self):
        for widget in self.scroll.winfo_children():
            widget.destroy()
        self.label_contador.configure(text="Cargando...")
        self.label_pagina.configure(text="")
        ctk.CTkLabel(
            self.scroll,
            text="⏳ Cargando clientas...",
            font=fuente_dato(), text_color=TEXTO_SUAVE
        ).grid(row=0, column=0, columnspan=6, pady=40)

    def _cargar_socios(self):
        self._todos = listar_socios()
        self.after(0, lambda: self._aplicar_filtros())

    def _filtrar(self):
        numero = self.entry_buscar.get().strip()
        if not numero:
            self._aplicar_filtros()
            return
        socio = buscar_socio_por_dni(numero)
        if not socio:
            self._filtrados = []
            self._pagina_actual = 0
            self._renderizar()
            return
        if self._planes_activos:
            if socio.get("tipo_plan") not in self._planes_activos:
                self._filtrados = []
                self._pagina_actual = 0
                self._renderizar()
                return
        self._filtrados = [socio]
        self._pagina_actual = 0
        self._renderizar()

    def _limpiar_filtros(self):
        self.entry_buscar.delete(0, "end")
        self._planes_activos = set()
        self._pagina_actual  = 0
        self._actualizar_indicador_filtro()
        self._filtrados = self._todos
        self._renderizar()

    # ── Popup filtro por plan ─────────────────────────────────

    def _abrir_popup_plan(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Filtrar por plan")
        popup.resizable(False, False)
        popup.grab_set()
        popup.configure(fg_color=FONDO)
        popup.update_idletasks()
        x = (popup.winfo_screenwidth()  // 2) - 200
        y = (popup.winfo_screenheight() // 2) - 160
        popup.geometry(f"400x320+{x}+{y}")

        inner = ctk.CTkFrame(popup, fg_color=FONDO_CARD, corner_radius=20)
        inner.pack(fill="both", expand=True, padx=16, pady=16)

        ctk.CTkLabel(
            inner, text="Selecciona uno o más planes:",
            font=fuente_seccion(), text_color=TEXTO
        ).pack(pady=(24, 16), padx=30)

        vars_plan = {}
        for tipo in TIPOS_PLAN:
            var = ctk.BooleanVar(value=tipo in self._planes_activos)
            vars_plan[tipo] = var
            ctk.CTkCheckBox(
                inner, text=tipo,
                variable=var,
                font=fuente_dato(), text_color=TEXTO,
                fg_color=BTN_PRINCIPAL,
                hover_color="#9DC95A",
                checkmark_color=TEXTO,
                corner_radius=6,
                border_width=2,
                border_color=BTN_SECUNDARIO
            ).pack(anchor="w", padx=40, pady=8)

        btn_f = ctk.CTkFrame(inner, fg_color="transparent")
        btn_f.pack(fill="x", padx=30, pady=(16, 24))
        btn_f.grid_columnconfigure((0, 1), weight=1)

        def _limpiar():
            for var in vars_plan.values():
                var.set(False)

        def _aplicar():
            self._planes_activos = {
                tipo for tipo, var in vars_plan.items() if var.get()
            }
            popup.destroy()
            self._actualizar_indicador_filtro()
            self._aplicar_filtros()

        ctk.CTkButton(
            btn_f, text="Limpiar", height=48,
            font=fuente_boton_sec(), fg_color=BTN_SECUNDARIO,
            hover_color="#C4A882", text_color=TEXTO,
            corner_radius=10, command=_limpiar
        ).grid(row=0, column=0, padx=(0, 8), sticky="ew")

        ctk.CTkButton(
            btn_f, text="✅  Aplicar", height=48,
            font=fuente_boton(), fg_color=BTN_PRINCIPAL,
            hover_color="#9DC95A", text_color=TEXTO,
            corner_radius=10, command=_aplicar
        ).grid(row=0, column=1, padx=(8, 0), sticky="ew")

    def _actualizar_indicador_filtro(self):
        if self._planes_activos:
            planes_str = ", ".join(sorted(self._planes_activos))
            self.label_filtro_activo.configure(
                text=f"⚠ Filtro activo: {planes_str}")
            self.btn_filtro_plan.configure(fg_color=BARRA)
        else:
            self.label_filtro_activo.configure(text="")
            self.btn_filtro_plan.configure(fg_color=BTN_SECUNDARIO)

    def _aplicar_filtros(self):
        if not self._planes_activos:
            self._filtrados = self._todos
        else:
            self._filtrados = [
                s for s in self._todos
                if s.get("tipo_plan") in self._planes_activos
            ]
        # Vigentes primero, vencidas al final
        if self._planes_activos:
            self._filtrados = sorted(
                self._filtrados,
                key=lambda s: fecha_fin_ya_vencida(s["fecha_fin"])
            )
        self._pagina_actual = 0
        self._renderizar()

    # ── Paginación ───────────────────────────────────────────

    def _pagina_anterior(self):
        if self._pagina_actual > 0:
            self._pagina_actual -= 1
            self._renderizar()

    def _pagina_siguiente(self):
        total_paginas = max(1, -(-len(self._filtrados) // self._por_pagina))
        if self._pagina_actual < total_paginas - 1:
            self._pagina_actual += 1
            self._renderizar()

    # ── Renderizar ────────────────────────────────────────────

    def _renderizar(self):
        for widget in self.scroll.winfo_children():
            widget.destroy()

        total     = len(self._todos)
        mostrando = len(self._filtrados)

        # Contador
        if self._planes_activos and not self.entry_buscar.get().strip():
            lineas = []
            for plan in sorted(self._planes_activos):
                socios_plan = [
                    s for s in self._filtrados if s.get("tipo_plan") == plan]
                vigentes = sum(
                    1 for s in socios_plan
                    if not fecha_fin_ya_vencida(s["fecha_fin"]))
                vencidas = len(socios_plan) - vigentes
                partes = [f"{len(socios_plan)} con plan {plan}"]
                if vigentes > 0:
                    partes.append(
                        f"{vigentes} vigente{'s' if vigentes != 1 else ''}")
                if vencidas > 0:
                    partes.append(
                        f"{vencidas} vencida{'s' if vencidas != 1 else ''}")
                lineas.append(" — ".join(partes))
            self.label_contador.configure(
                text="  |  ".join(lineas))
        elif mostrando == total:
            self.label_contador.configure(
                text=f"Total: {total} clienta{'s' if total != 1 else ''} "
                     f"registrada{'s' if total != 1 else ''}")
        else:
            self.label_contador.configure(
                text=f"Mostrando {mostrando} de {total} clientas")

        if not self._filtrados:
            self.label_pagina.configure(text="")
            self.btn_anterior.configure(state="disabled")
            self.btn_siguiente.configure(state="disabled")
            ctk.CTkLabel(
                self.scroll,
                text="No se encontraron clientas.",
                font=fuente_dato(), text_color=TEXTO_SUAVE
            ).grid(row=0, column=0, columnspan=6, pady=40)
            return

        # Calcular páginas
        total_paginas = max(1, -(-len(self._filtrados) // self._por_pagina))
        inicio        = self._pagina_actual * self._por_pagina
        fin           = inicio + self._por_pagina
        pagina_socios = self._filtrados[inicio:fin]

        # Actualizar controles paginación
        self.label_pagina.configure(
            text=f"Página {self._pagina_actual + 1} de {total_paginas}")
        self.btn_anterior.configure(
            state="normal" if self._pagina_actual > 0 else "disabled")
        self.btn_siguiente.configure(
            state="normal" if self._pagina_actual < total_paginas - 1
            else "disabled")

        # Ocultar paginación si cabe en una página
        if total_paginas == 1:
            self.frame_pag.grid_remove()
        else:
            self.frame_pag.grid()

        # Renderizar solo la página actual
        for i, socio in enumerate(pagina_socios):
            color_fila = FONDO_CARD if i % 2 == 0 else CAMPO

            fila = ctk.CTkFrame(
                self.scroll, fg_color=color_fila, corner_radius=10)
            fila.grid(row=i, column=0, columnspan=6,
                      sticky="ew", pady=2)
            fila.grid_columnconfigure((0,1,2,3,4,5), weight=1)

            tipo_texto, tipo_color = formato_tipo_plan(
                socio.get("tipo_plan", "—"),
                socio["fecha_fin"]
            )

            datos = [
                (socio.get("tipo_documento", "DNI"), TEXTO),
                (socio["dni"],                       TEXTO),
                (f"{socio['nombre']} {socio['apellido']}", TEXTO),
                (tipo_texto,                         tipo_color),
                (formatear_fecha_legible(socio["fecha_inicio"]), TEXTO),
                (formatear_fecha_legible(socio["fecha_fin"]),    TEXTO),
            ]

            for col, (valor, color) in enumerate(datos):
                entry = ctk.CTkEntry(
                    fila,
                    font=fuente_dato(),
                    text_color=color,
                    fg_color="transparent",
                    border_width=0,
                    justify="center"
                )
                entry.insert(0, valor)
                entry.configure(state="readonly")
                entry.grid(row=0, column=col, padx=10,
                           pady=14, sticky="ew")