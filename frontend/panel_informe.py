"""Panel 'Informe' con anomalías y ocupación del canal (FRONT-END)."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QGroupBox, QLabel, QProgressBar, QScrollArea,
                               QVBoxLayout)

from frontend.utilidades import fmt


class PanelInforme(QGroupBox):
    def __init__(self, parent=None):
        super().__init__("Informe", parent)
        titulo = QLabel("<b>Canales con situaciones anormales</b>")
        self.lbl_anomalias = QLabel("Sin análisis")
        self.lbl_anomalias.setTextFormat(Qt.RichText)
        self.lbl_anomalias.setWordWrap(True)
        self.lbl_anomalias.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.lbl_anomalias)
        scroll.setFrameShape(QScrollArea.NoFrame)

        self.lbl_calidad = QLabel("")
        self.lbl_calidad.setWordWrap(True)
        self.lbl_calidad.setStyleSheet("color: #555; font-size: 11px;")

        self.lbl_titulo_canal = QLabel("<b>Ocupación del canal</b>")
        self.barra = QProgressBar()
        self.barra.setRange(0, 1000)
        self.barra.setTextVisible(False)
        self.lbl_detalle = QLabel("")
        self.lbl_porcentaje = QLabel("")

        layout = QVBoxLayout(self)
        layout.addWidget(titulo)
        layout.addWidget(scroll, 1)
        layout.addWidget(self.lbl_calidad)
        layout.addWidget(self.lbl_titulo_canal)
        layout.addWidget(self.barra)
        layout.addWidget(self.lbl_detalle)
        layout.addWidget(self.lbl_porcentaje)

    def actualizar_anomalias(self, estadisticas):
        lineas = []
        for e in estadisticas:
            for obs in e.observaciones:
                color = "#c0392b" if obs == "Ocupación persistente" else "#333"
                texto = obs[0].lower() + obs[1:]
                lineas.append(f'<span style="color:{color}">• {e.canal}: {texto}</span>')
        self.lbl_anomalias.setText("<br>".join(lineas) or "Ningún canal anómalo.")

    def actualizar_calidad(self, r):
        self.lbl_calidad.setText(
            f"Datos: {fmt(r.filas_leidas, 0)} filas leídas · "
            f"{r.duplicados} duplicadas · {r.filas_invalidas} inválidas "
            f"(ERROR: {r.estado_error}, vacías: {r.potencia_faltante}, "
            f"−999: {r.codigo_999})")

    def actualizar_canal(self, e):
        self.lbl_titulo_canal.setText(f"<b>Ocupación del canal {e.canal}</b>")
        self.barra.setValue(int(round(e.ocupacion_pct * 10)))
        self.lbl_detalle.setText(
            f"{fmt(e.ocupadas, 0)} ocupadas / {fmt(e.validas, 0)} válidas")
        self.lbl_porcentaje.setText(
            f"<b style='font-size:14px'>{fmt(e.ocupacion_pct)} % de ocupación</b>")
