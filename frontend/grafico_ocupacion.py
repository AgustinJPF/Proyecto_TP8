"""Gráfico de barras: porcentaje de ocupación por canal (FRONT-END)."""
from matplotlib.backends.backend_qtagg import (FigureCanvasQTAgg,
                                               NavigationToolbar2QT)
from matplotlib.figure import Figure
from PySide6.QtWidgets import QVBoxLayout, QWidget

from frontend.utilidades import fmt


class GraficoOcupacion(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figura = Figure(figsize=(6, 2.4), layout="constrained")
        self.canvas = FigureCanvasQTAgg(self.figura)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)
        self.ax = self.figura.add_subplot(111)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

    def graficar(self, canales, porcentajes, seleccionado):
        ax = self.ax
        ax.clear()
        colores = ["#e8833a" if c == seleccionado else "#4c8bc7" for c in canales]
        barras = ax.bar(canales, porcentajes, color=colores)
        for barra, valor in zip(barras, porcentajes):
            ax.text(barra.get_x() + barra.get_width() / 2, valor + 1,
                    f"{fmt(valor)} %", ha="center", va="bottom", fontsize=7)
        ax.set_ylim(0, 105)
        ax.set_ylabel("Ocupación (%)")
        ax.set_title("Porcentaje de ocupación por canal", fontsize=10)
        ax.tick_params(axis="x", labelsize=8)
        ax.grid(axis="y", alpha=0.3)
        self.canvas.draw_idle()
