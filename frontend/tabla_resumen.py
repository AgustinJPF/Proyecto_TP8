"""Tabla 'Resumen por canal' (FRONT-END)."""
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import (QAbstractItemView, QHeaderView, QTableWidget,
                               QTableWidgetItem)

from frontend.utilidades import fmt

COLUMNAS = ["Canal", "Frecuencia (MHz)", "Válidas", "Ocupación", "Observación"]
ROJO = QColor("#f4b6b6")
AMBAR = QColor("#fbe3a8")


class TablaResumen(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(0, len(COLUMNAS), parent)
        self.setHorizontalHeaderLabels(COLUMNAS)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def cargar(self, estadisticas):
        """Muestra solo los canales con observaciones (como en la Figura 1)."""
        filas = [e for e in estadisticas if e.anomalo]
        self.setRowCount(len(filas))
        for i, e in enumerate(filas):
            valores = [e.canal, f"{e.frecuencia_mhz:.3f}".replace(".", ","),
                       fmt(e.validas, 0), f"{fmt(e.ocupacion_pct)} %",
                       ", ".join(e.observaciones)]
            for j, v in enumerate(valores):
                item = QTableWidgetItem(v)
                item.setTextAlignment(Qt.AlignCenter)
                if j == 4:
                    item.setBackground(QBrush(ROJO if e.persistente else AMBAR))
                self.setItem(i, j, item)
