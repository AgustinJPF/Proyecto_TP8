"""Ventana principal que integra todos los paneles (FRONT-END)."""
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (QComboBox, QFileDialog, QGroupBox, QHBoxLayout,
                               QMessageBox, QMainWindow, QVBoxLayout, QWidget)

from backend.analizador import AnalizadorEspectro
from frontend.grafico_ocupacion import GraficoOcupacion
from frontend.grafico_potencia import GraficoPotencia
from frontend.panel_informe import PanelInforme
from frontend.panel_parametros import PanelParametros
from frontend.tabla_resumen import TablaResumen


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PRGII-PRJ08 – Monitor de ocupación del espectro radioeléctrico")
        self.resize(1200, 900)

        self.analizador = AnalizadorEspectro()
        self.estadisticas = {}
        self._umbral = -85.0
        self._ventana = 5

        self._crear_widgets()
        self._crear_menu()
        self.statusBar().showMessage(
            "Listo. Seleccione el CSV y presione «Analizar».")

    # ---------- Construcción de la interfaz ----------
    def _crear_widgets(self):
        self.panel_parametros = PanelParametros()
        self.combo_canal = QComboBox()
        grupo_canal = QGroupBox("Canal a graficar")
        QVBoxLayout(grupo_canal).addWidget(self.combo_canal)
        self.panel_informe = PanelInforme()

        izquierda = QVBoxLayout()
        izquierda.addWidget(self.panel_parametros)
        izquierda.addWidget(grupo_canal)
        izquierda.addWidget(self.panel_informe, 1)
        w_izq = QWidget()
        w_izq.setLayout(izquierda)
        w_izq.setFixedWidth(300)

        self.grafico_potencia = GraficoPotencia()
        self.grafico_ocupacion = GraficoOcupacion()
        self.tabla = TablaResumen()
        derecha = QVBoxLayout()
        derecha.addWidget(self.grafico_potencia, 3)
        derecha.addWidget(self.grafico_ocupacion, 3)
        derecha.addWidget(self.tabla, 2)
        w_der = QWidget()
        w_der.setLayout(derecha)

        central = QWidget()
        principal = QHBoxLayout(central)
        principal.addWidget(w_izq)
        principal.addWidget(w_der, 1)
        self.setCentralWidget(central)

        self.panel_parametros.analizar_solicitado.connect(self._analizar)
        self.combo_canal.currentIndexChanged.connect(self._actualizar_canal)

    def _crear_menu(self):
        menu_archivo = self.menuBar().addMenu("Archivo")
        a_abrir = QAction("Abrir CSV…", self)
        a_abrir.triggered.connect(self._abrir_csv)
        a_salir = QAction("Salir", self)
        a_salir.triggered.connect(self.close)
        menu_archivo.addAction(a_abrir)
        menu_archivo.addSeparator()
        menu_archivo.addAction(a_salir)

        menu_ayuda = self.menuBar().addMenu("Ayuda")
        a_acerca = QAction("Acerca de", self)
        a_acerca.triggered.connect(self._acerca_de)
        menu_ayuda.addAction(a_acerca)

    # ---------- Acciones ----------
    def _abrir_csv(self):
        ruta, _ = QFileDialog.getOpenFileName(
            self, "Abrir archivo CSV", "", "Archivos CSV (*.csv);;Todos (*)")
        if ruta:
            self.panel_parametros.set_ruta(ruta)
            self._analizar()

    def _acerca_de(self):
        QMessageBox.about(
            self, "Acerca de",
            "PRGII-PRJ08\nMonitor de ocupación del espectro radioeléctrico\n"
            "Programación II (5002) – Ing. en Telecomunicaciones")

    def _analizar(self):
        try:
            self.analizador.cargar(self.panel_parametros.ruta())
        except (FileNotFoundError, ValueError) as exc:
            QMessageBox.critical(self, "Error al cargar el archivo", str(exc))
            self.statusBar().showMessage("Error al cargar el archivo.")
            return

        self._umbral = self.panel_parametros.umbral()
        self._ventana = self.panel_parametros.ventana()
        self.estadisticas = self.analizador.analizar(self._umbral)
        lista = list(self.estadisticas.values())

        # Canal por defecto: el de mayor ocupación
        mejor = max(lista, key=lambda e: e.ocupacion_pct).canal
        self.combo_canal.blockSignals(True)
        self.combo_canal.clear()
        for e in lista:
            self.combo_canal.addItem(f"{e.canal} — {e.frecuencia_mhz:.3f} MHz", e.canal)
        self.combo_canal.setCurrentIndex(self.combo_canal.findData(mejor))
        self.combo_canal.blockSignals(False)

        self.panel_informe.actualizar_anomalias(lista)
        self.panel_informe.actualizar_calidad(self.analizador.resumen_carga)
        self.tabla.cargar(lista)
        self._actualizar_canal()
        self.statusBar().showMessage(
            f"Análisis completo: {len(lista)} canales procesados")

    def _actualizar_canal(self):
        canal = self.combo_canal.currentData()
        if canal is None:
            return
        e = self.estadisticas[canal]
        serie = self.analizador.serie(canal, self._ventana)
        self.grafico_potencia.graficar(serie, canal, e.frecuencia_mhz,
                                       self._umbral, self._ventana)
        self.grafico_ocupacion.graficar(
            list(self.estadisticas),
            [x.ocupacion_pct for x in self.estadisticas.values()], canal)
        self.panel_informe.actualizar_canal(e)
