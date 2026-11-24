"""Panel 'Parámetros de análisis' (FRONT-END)."""
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (QDoubleSpinBox, QFileDialog, QFormLayout,
                               QGroupBox, QHBoxLayout, QLineEdit, QPushButton,
                               QSpinBox, QVBoxLayout, QWidget)


class PanelParametros(QGroupBox):
    analizar_solicitado = Signal()

    def __init__(self, ruta_inicial="espectro.csv", parent=None):
        super().__init__("Parámetros de análisis", parent)
        self.edit_archivo = QLineEdit(ruta_inicial)
        self.btn_examinar = QPushButton("…")
        self.btn_examinar.setFixedWidth(30)

        fila_archivo = QWidget()
        h = QHBoxLayout(fila_archivo)
        h.setContentsMargins(0, 0, 0, 0)
        h.addWidget(self.edit_archivo)
        h.addWidget(self.btn_examinar)

        self.spin_umbral = QDoubleSpinBox()
        self.spin_umbral.setRange(-150.0, 0.0)
        self.spin_umbral.setDecimals(1)
        self.spin_umbral.setSingleStep(1.0)
        self.spin_umbral.setValue(-85.0)

        self.spin_ventana = QSpinBox()
        self.spin_ventana.setRange(1, 500)
        self.spin_ventana.setValue(5)

        self.btn_analizar = QPushButton("Analizar")

        form = QFormLayout()
        form.addRow("Archivo CSV", fila_archivo)
        form.addRow("Umbral potencia (dBm)", self.spin_umbral)
        form.addRow("Ventana prom. móvil", self.spin_ventana)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self.btn_analizar)

        self.btn_examinar.clicked.connect(self._examinar)
        self.btn_analizar.clicked.connect(self.analizar_solicitado.emit)

    def _examinar(self):
        ruta, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar archivo CSV", "", "Archivos CSV (*.csv);;Todos (*)")
        if ruta:
            self.edit_archivo.setText(ruta)

    # --- Accesores ---
    def ruta(self):
        return self.edit_archivo.text().strip()

    def set_ruta(self, ruta):
        self.edit_archivo.setText(ruta)

    def umbral(self):
        return self.spin_umbral.value()

    def ventana(self):
        return self.spin_ventana.value()
