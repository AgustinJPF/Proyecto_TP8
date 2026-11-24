"""Fachada del back-end: la usa la interfaz gráfica (BACK-END)."""
from backend.anomalias import CriteriosAnomalia, DetectorAnomalias
from backend.carga import CargadorCSV, ResumenCarga
from backend.ocupacion import CalculadorOcupacion


class AnalizadorEspectro:
    def __init__(self, criterios: CriteriosAnomalia = None):
        self.criterios = criterios or CriteriosAnomalia()
        self.resumen_carga = ResumenCarga()
        self.calculador = None

    def cargar(self, ruta):
        df, self.resumen_carga = CargadorCSV().cargar(ruta)
        self.calculador = CalculadorOcupacion(df)
        return self.resumen_carga

    def analizar(self, umbral) -> dict:
        """Devuelve {canal: EstadisticasCanal} para todos los canales."""
        if self.calculador is None:
            raise RuntimeError("Primero debe cargar un archivo CSV.")
        det = DetectorAnomalias(self.calculador, self.criterios)
        return {c: det.evaluar(c, umbral) for c in self.calculador.canales()}

    def serie(self, canal, ventana):
        return self.calculador.serie_con_promedio(canal, ventana)
