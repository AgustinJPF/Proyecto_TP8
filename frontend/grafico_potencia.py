"""Gráfico de potencia recibida vs. tiempo (FRONT-END)."""
import matplotlib.dates as mdates
from matplotlib.backends.backend_qtagg import (FigureCanvasQTAgg,
                                               NavigationToolbar2QT)
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter
from PySide6.QtWidgets import QVBoxLayout, QWidget

DIAS = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]


def _nombre_dia(x, _pos):
    return DIAS[mdates.num2date(x).weekday()]


class GraficoPotencia(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figura = Figure(figsize=(6, 2.8), layout="constrained")
        self.canvas = FigureCanvasQTAgg(self.figura)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)
        self.ax = self.figura.add_subplot(111)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

    def graficar(self, df, canal, frecuencia_mhz, umbral, ventana):
        """df: DataFrame con columnas 'potencia' y 'promedio' indexado por fecha."""
        ax = self.ax
        ax.clear()
        ax.plot(df.index, df["potencia"], lw=0.8, color="#1f77b4",
                label="Potencia (dBm)")
        ax.plot(df.index, df["promedio"], lw=1.2, color="#ff9f1c",
                label=f"Promedio móvil ({ventana})")
        ax.axhline(umbral, ls="--", lw=1, color="red",
                   label=f"Umbral ({umbral:.0f} dBm)")
        ax.set_title(f"Potencia recibida del canal {canal} ({frecuencia_mhz:.3f} MHz)",
                     fontsize=10)
        ax.set_ylabel("Potencia (dBm)")
        ax.xaxis.set_major_locator(mdates.DayLocator())
        ax.xaxis.set_major_formatter(FuncFormatter(_nombre_dia))
        ax.grid(alpha=0.3)
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3,
                  fontsize=8, frameon=False)
        self.canvas.draw_idle()
