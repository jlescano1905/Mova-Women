# gui/widgets/fecha_picker.py
import customtkinter as ctk
from datetime import date
import calendar
from gui.tema import *

MESES = [
    "Enero","Febrero","Marzo","Abril","Mayo","Junio",
    "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"
]

class FechaPicker(ctk.CTkFrame):
    def __init__(self, parent, fecha_inicial=None, on_change=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self._on_change = on_change
        hoy = fecha_inicial or date.today()
        self.grid_columnconfigure((0,1,2,3,4), weight=0)

        ctk.CTkLabel(
            self, text="Día",
            font=fuente_label(), text_color=TEXTO
        ).grid(row=0, column=0, padx=(0, 4))

        self.combo_dia = ctk.CTkComboBox(
            self, width=90, height=50,
            values=[str(d).zfill(2) for d in range(1, 32)],
            font=fuente(18), text_color=TEXTO,
            fg_color=CAMPO, border_color=BTN_SECUNDARIO,
            button_color=BTN_SECUNDARIO,
            button_hover_color=BARRA,
            dropdown_font=fuente(17),
            command=self._on_change_interno
        )
        self.combo_dia.set(str(hoy.day).zfill(2))
        self.combo_dia.grid(row=1, column=0, padx=(0, 8))

        ctk.CTkLabel(
            self, text="/",
            font=fuente(20, "bold"), text_color=TEXTO
        ).grid(row=1, column=1, padx=4)

        ctk.CTkLabel(
            self, text="Mes",
            font=fuente_label(), text_color=TEXTO
        ).grid(row=0, column=2, padx=(0, 4))

        self.combo_mes = ctk.CTkComboBox(
            self, width=160, height=50,
            values=MESES,
            font=fuente(18), text_color=TEXTO,
            fg_color=CAMPO, border_color=BTN_SECUNDARIO,
            button_color=BTN_SECUNDARIO,
            button_hover_color=BARRA,
            dropdown_font=fuente(17),
            command=self._on_change_interno
        )
        self.combo_mes.set(MESES[hoy.month - 1])
        self.combo_mes.grid(row=1, column=2, padx=(0, 8))

        ctk.CTkLabel(
            self, text="/",
            font=fuente(20, "bold"), text_color=TEXTO
        ).grid(row=1, column=3, padx=4)

        anio_actual = hoy.year
        anios = [str(a) for a in range(anio_actual - 5, anio_actual + 6)]

        ctk.CTkLabel(
            self, text="Año",
            font=fuente_label(), text_color=TEXTO
        ).grid(row=0, column=4, padx=(0, 4))

        self.combo_anio = ctk.CTkComboBox(
            self, width=110, height=50,
            values=anios,
            font=fuente(18), text_color=TEXTO,
            fg_color=CAMPO, border_color=BTN_SECUNDARIO,
            button_color=BTN_SECUNDARIO,
            button_hover_color=BARRA,
            dropdown_font=fuente(17),
            command=self._on_change_interno
        )
        self.combo_anio.set(str(anio_actual))
        self.combo_anio.grid(row=1, column=4)

    def _on_change_interno(self, _=None):
        try:
            mes      = MESES.index(self.combo_mes.get()) + 1
            anio     = int(self.combo_anio.get())
            max_dias = calendar.monthrange(anio, mes)[1]
            dias     = [str(d).zfill(2) for d in range(1, max_dias + 1)]
            self.combo_dia.configure(values=dias)
            if int(self.combo_dia.get()) > max_dias:
                self.combo_dia.set(str(max_dias).zfill(2))
        except Exception:
            pass
        # Llamar callback externo si existe
        if self._on_change:
            self._on_change()

    def get_fecha(self):
        try:
            dia  = int(self.combo_dia.get())
            mes  = MESES.index(self.combo_mes.get()) + 1
            anio = int(self.combo_anio.get())
            return date(anio, mes, dia).strftime("%Y-%m-%d")
        except Exception:
            return date.today().strftime("%Y-%m-%d")

    def set_fecha(self, fecha_str):
        try:
            from datetime import datetime
            d = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            self.combo_dia.set(str(d.day).zfill(2))
            self.combo_mes.set(MESES[d.month - 1])
            self.combo_anio.set(str(d.year))
        except Exception:
            pass